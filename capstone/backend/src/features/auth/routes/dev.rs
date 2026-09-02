use super::*;

/// ONLY implements the routes if in dev mode
pub fn map_routes_if_in_dev(router: Router<AppState>) -> Router<AppState> {
    if is_dev() {
        tracing::warn!("Dev environment: Dev auth routes are getting mapped");
    } else {
        return router;
    }

    router
        .route("/auth/login/bypass", post(login_bypass))
        .route(
            "/auth/register/start/superadmin",
            post(register_start_as_super_admin),
        )
}

/// Only in dev environment
async fn login_bypass(
    State(state): State<AppState>,
    Json(body): Json<LoginRequest>,
) -> Result<Json<LoginResponse>, AuthHttpError> {
    let token_settings = AccessTokenIssueSettings::new_from_config(&state.app_config);

    service::login_bypass(&state.db, &*state.clock, body, &token_settings)
        .await
        .map(Json)
        .map_err(AuthHttpError::from)
}

/// Creates a temp user
async fn register_start_as_super_admin(
    State(state): State<AppState>,
    Json(body): Json<RegisterRequest>,
) -> Result<Json<RegisterAttemptedResponse>, AuthHttpError> {
    let email = body.email.clone();
    let user_id = service::register_pending(&state.db, &*state.clock, body, Role::SuperAdmin)
        .await
        .map_err(AuthHttpError::from)?;

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
