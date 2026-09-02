use axum::{
    extract::FromRequestParts,
    http::{header::AUTHORIZATION, request::Parts},
    middleware::Next,
};

use super::service;
use crate::prelude::*;

#[derive(Clone, Debug)]
pub struct AuthenticatedUser {
    pub user_id: i32,
    pub role: Role,
}

impl<S> FromRequestParts<S> for AuthenticatedUser
where
    S: Send + Sync,
{
    type Rejection = StatusCode;

    async fn from_request_parts(parts: &mut Parts, _state: &S) -> Result<Self, Self::Rejection> {
        parts
            .extensions
            .get::<AuthenticatedUser>()
            .cloned()
            .ok_or(StatusCode::UNAUTHORIZED)
    }
}

pub async fn require_auth(
    State(state): State<AppState>,
    mut request: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let token =
        bearer_token(request.headers().get(AUTHORIZATION)).ok_or(StatusCode::UNAUTHORIZED)?;

    let user = authenticated_user_from_token(
        &state,
        token,
        state.app_config.auth.require_email_verification,
    )
    .await?;
    request.extensions_mut().insert(user);

    Ok(next.run(request).await)
}

pub async fn require_admin_auth(
    State(state): State<AppState>,
    mut request: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let token =
        bearer_token(request.headers().get(AUTHORIZATION)).ok_or(StatusCode::UNAUTHORIZED)?;

    let user = authenticated_user_from_token(&state, token, true).await?;
    tracing::info!("User role: {:?}", user.role);
    if !(user.role == Role::SuperAdmin || user.role == Role::Admin) {
        tracing::error!("User is not an admin");
        return Err(StatusCode::FORBIDDEN);
    }
    tracing::info!("User is an admin");

    request.extensions_mut().insert(user);
    Ok(next.run(request).await)
}

pub async fn require_super_admin_auth(
    State(state): State<AppState>,
    mut request: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    let token =
        bearer_token(request.headers().get(AUTHORIZATION)).ok_or(StatusCode::UNAUTHORIZED)?;

    let user = authenticated_user_from_token(&state, token, true).await?;
    tracing::info!("User role: {:?}", user.role);
    if user.role != Role::SuperAdmin {
        tracing::error!("User is not a super admin");
        return Err(StatusCode::FORBIDDEN);
    }
    tracing::info!("User is a super admin");

    request.extensions_mut().insert(user);
    Ok(next.run(request).await)
}

async fn authenticated_user_from_token(
    state: &AppState,
    token: &str,
    require_email_verified: bool,
) -> Result<AuthenticatedUser, StatusCode> {
    let jwt_secret = &state.app_config.auth.jwt_secret;

    let user_id = service::user_id_from_token(jwt_secret, &*state.clock, token)
        .map_err(|_| StatusCode::UNAUTHORIZED)?;

    let user = crate::features::user::service::get_user_by_id(&state.db, user_id)
        .await
        .map_err(|_| StatusCode::UNAUTHORIZED)?;

    if require_email_verified && !user.email_verified {
        return Err(StatusCode::UNAUTHORIZED);
    }

    Ok(AuthenticatedUser {
        user_id,
        role: user.role,
    })
}

fn bearer_token(header: Option<&axum::http::HeaderValue>) -> Option<&str> {
    let value = header?.to_str().ok()?;
    value.strip_prefix("Bearer ")
}
