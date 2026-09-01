use axum::{
    Json, Router,
    extract::State,
    http::StatusCode,
    routing::{get, post},
};

mod dev;

mod errors;
use errors::*;

use super::service;
use crate::{
    app_config::AppConfig,
    environment,
    features::{
        auth::{
            Role,
            middleware::{AuthenticatedUser, require_auth},
            service::AccessTokenIssueSettings,
        },
        email_server, user,
    },
    state::AppState,
};
use server_types::prelude::*;

pub fn auth_router(config: &AppConfig, state: AppState) -> Router<AppState> {
    let session_routes = Router::new()
        .route("/auth/session", get(session))
        .route_layer(axum::middleware::from_fn_with_state(state, require_auth));

    let router = Router::new()
        .route("/auth/register/start", post(register_start))
        .route("/auth/login", post(login))
        .route("/auth/refresh", post(refresh))
        .merge(session_routes);

    let router = if config.auth.require_email_verification {
        tracing::info!(
            "Auth Router: Mapping email verification routes since email verification is enabled"
        );
        router
            .route("/auth/email/verify", post(verify_email))
            .route("/auth/email/resend", post(resend_verification_email))
    } else {
        router
    };

    dev::map_routes_if_in_dev(router)
}

async fn session(
    user: AuthenticatedUser,
    State(state): State<AppState>,
) -> Result<Json<SessionResponse>, StatusCode> {
    let user = user::service::get_user_by_id(&state.db, user.user_id)
        .await
        .map_err(|_| StatusCode::UNAUTHORIZED)?;

    Ok(Json(SessionResponse {
        user_id: user.id,
        email: user.email,
    }))
}

/// Creates a temp user
async fn register_start(
    State(state): State<AppState>,
    Json(body): Json<RegisterRequest>,
) -> Result<Json<RegisterAttemptedResponse>, AuthHttpError> {
    let email = body.email.clone();
    let user_id = service::register_pending(&state.db, &*state.clock, body, Role::User)
        .await
        .map_err(AuthHttpError::from)?;

    // Return early if we don't require email verification
    if !state.app_config.auth.require_email_verification {
        service::force_verify_email(&state.db, user_id)
            .await
            .map_err(AuthHttpError::from)?;

        return Ok(Json(RegisterAttemptedResponse {
            user_id: Some(user_id),
            email_verification_code: None,
        }));
    }

    let email_response =
        email_server::service::add_pending_email_verification(&state.db, &*state.clock, user_id)
            .await
            .map_err(|_| {
                AuthHttpError((
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "something happend trying to send email verification".to_string(),
                ))
            })?;

    let code = &email_response.plaintext_code;
    state
        .email_sender
        .send_verification_code(&email, code)
        .await
        .map_err(|_| {
            AuthHttpError((
                StatusCode::INTERNAL_SERVER_ERROR,
                "something happend trying to send email verification".to_string(),
            ))
        })?;

    // Don't send the user ID to the end user in production
    let user_id = if environment::is_dev() {
        Some(user_id)
    } else {
        None
    };
    let email_verification_code = if environment::is_dev() {
        Some(email_response.plaintext_code)
    } else {
        None
    };
    Ok(Json(RegisterAttemptedResponse {
        user_id,
        email_verification_code,
    }))
}

async fn login(
    State(state): State<AppState>,
    Json(body): Json<LoginRequest>,
) -> Result<Json<LoginResponse>, AuthHttpError> {
    let token_settings = AccessTokenIssueSettings::new_from_config(&state.app_config);

    service::login(&state.db, &*state.clock, body, &token_settings)
        .await
        .map(Json)
        .map_err(AuthHttpError::from)
}

async fn refresh(
    State(state): State<AppState>,
    Json(body): Json<RefreshTokenRequest>,
) -> Result<Json<RefreshTokenResponse>, AuthHttpError> {
    let token_settings = AccessTokenIssueSettings::new_from_config(&state.app_config);

    service::refresh_tokens(&state.db, &*state.clock, body, &token_settings)
        .await
        .map(Json)
        .map_err(AuthHttpError::from)
}

async fn verify_email(
    State(state): State<AppState>,
    Json(body): Json<VerifyEmailRequest>,
) -> Result<Json<VerifyEmailResponse>, AuthHttpError> {
    service::verify_email(&state.db, &*state.clock, body)
        .await
        .map(Json)
        .map_err(AuthHttpError::from)
}

async fn resend_verification_email(
    State(state): State<AppState>,
    Json(body): Json<ResendVerificationEmailRequest>,
) -> Result<Json<ResendVerificationEmailResponse>, AuthHttpError> {
    let email = body.email.trim().to_string();
    let email_response = service::prepare_verification_email_resend(&state.db, &*state.clock, body)
        .await
        .map_err(AuthHttpError::from)?;

    if let Some(ref email_response) = email_response {
        state
            .email_sender
            .send_verification_code(&email, &email_response.plaintext_code)
            .await
            .map_err(|_| {
                AuthHttpError((
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "something happend trying to send email verification".to_string(),
                ))
            })?;
    }

    let email_verification_code = if environment::is_dev() {
        tracing::warn!("sending email_response: {:?}", email_response);
        email_response
            .as_ref()
            .map(|resp| resp.plaintext_code.clone())
    } else {
        None
    };
    Ok(Json(ResendVerificationEmailResponse {
        message: "If an unverified account exists for that email, a new verification email has been sent."
            .to_string(),
        email_verification_code,
    }))
}
