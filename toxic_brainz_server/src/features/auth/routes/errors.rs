use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
};

use crate::features::auth::service::AuthError;

pub struct AuthHttpError(pub (StatusCode, String));

impl From<AuthError> for AuthHttpError {
    fn from(err: AuthError) -> Self {
        let (status, msg) = match err {
            AuthError::EmailTaken => (StatusCode::CONFLICT, "email already taken"),
            AuthError::InvalidCredentials => (StatusCode::UNAUTHORIZED, "invalid credentials"),
            AuthError::InvalidRefreshToken => {
                (StatusCode::UNAUTHORIZED, "invalid or expired refresh token")
            }
            AuthError::WeakPassword => (
                StatusCode::BAD_REQUEST,
                "password must be at least 8 characters",
            ),
            AuthError::InvalidEmail => (
                StatusCode::BAD_REQUEST,
                "email must be 3–64 chars (letters, digits, underscore)",
            ),
            AuthError::Token(_) | AuthError::Hash(_) | AuthError::Database(_) => {
                tracing::error!("auth error: {err:?}");
                (StatusCode::INTERNAL_SERVER_ERROR, "internal server error")
            }
            AuthError::EmailNotVerified => (StatusCode::UNAUTHORIZED, "email not verified"),
            AuthError::EmailAlreadyVerified => (StatusCode::BAD_REQUEST, "email already verified"),
            AuthError::InvalidVerificationCode => (
                StatusCode::BAD_REQUEST,
                "invalid or expired verification code",
            ),
        };
        Self((status, msg.into()))
    }
}

impl IntoResponse for AuthHttpError {
    fn into_response(self) -> Response {
        let (status, body) = self.0;
        (status, body).into_response()
    }
}
