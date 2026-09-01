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
