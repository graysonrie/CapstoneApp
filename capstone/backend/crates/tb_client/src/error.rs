use thiserror::Error;

pub type ClientResult<T> = Result<T, ClientError>;

#[derive(Debug, Error)]
pub enum ClientError {
    #[error("auth token lock poisoned")]
    AuthTokenLockPoisoned,

    #[error("refresh token lock poisoned")]
    RefreshTokenLockPoisoned,

    #[error("no auth token has been saved; call login first")]
    AuthTokenNotSet,

    #[error("no refresh token has been saved; call login first")]
    RefreshTokenNotSet,

    #[error("request failed with status {status}: {body}")]
    RequestFailed { status: u16, body: String },

    #[error("failed to decode response body as JSON: {source}; body: {body}")]
    JsonDecode {
        source: serde_json::Error,
        body: String,
    },

    #[error("missing email verification code in register response")]
    MissingEmailVerificationCode,

    #[error(transparent)]
    Http(#[from] reqwest::Error),

    #[error(transparent)]
    Url(#[from] url::ParseError),
}

impl ClientError {
    /// Message safe to show in the UI. Uses the backend's HTTP body for
    /// failed requests and never leaks internal details (reqwest, JSON, locks).
    pub fn user_message(&self) -> String {
        match self {
            Self::RequestFailed { body, .. } => {
                let body = body.trim();
                if body.is_empty() {
                    "Something went wrong".to_string()
                } else {
                    body.to_string()
                }
            }
            Self::Http(_) => "Unable to reach the server".to_string(),
            Self::Url(_) => "Invalid server address".to_string(),
            Self::AuthTokenNotSet | Self::RefreshTokenNotSet => "You are not signed in".to_string(),
            Self::MissingEmailVerificationCode => "Email verification is required".to_string(),
            Self::AuthTokenLockPoisoned
            | Self::RefreshTokenLockPoisoned
            | Self::JsonDecode { .. } => "Something went wrong".to_string(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn user_message_uses_http_body() {
        let err = ClientError::RequestFailed {
            status: 401,
            body: "invalid credentials".into(),
        };
        assert_eq!(err.user_message(), "invalid credentials");
        assert_eq!(
            err.to_string(),
            "request failed with status 401: invalid credentials"
        );
    }

    #[test]
    fn user_message_falls_back_on_empty_body() {
        let err = ClientError::RequestFailed {
            status: 500,
            body: "  \n".into(),
        };
        assert_eq!(err.user_message(), "Something went wrong");
    }
}
