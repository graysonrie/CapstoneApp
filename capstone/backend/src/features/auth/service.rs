use chrono::Duration;
use sea_orm::DbErr;

use crate::{
    app_config::AppConfig,
    clock::Clock,
    environment,
    features::{
        auth::Role,
        db::models::user::{self, UserIdType},
        email_server::{self, service::EmailVerificationError},
    },
};

use super::{password, repo, tokens};
use server_types::prelude::*;

#[derive(Clone, Debug)]
pub struct AccessTokenIssueSettings {
    pub jwt_secret: String,
    pub access_token_ttl: Duration,
    pub refresh_token_ttl: Duration,
}

impl AccessTokenIssueSettings {
    /// NOTE: panics if the access token ttl or refresh token ttl specified in the config cannot be parsed
    pub fn new_from_config(config: &AppConfig) -> Self {
        let access_token_ttl = duration_str::parse_chrono(&config.auth.access_token_ttl).unwrap();
        let refresh_token_ttl = duration_str::parse_chrono(&config.auth.refresh_token_ttl).unwrap();

        Self {
            jwt_secret: config.auth.jwt_secret.clone(),
            access_token_ttl,
            refresh_token_ttl,
        }
    }
}

#[derive(Debug)]
pub enum AuthError {
    EmailTaken,
    InvalidCredentials,
    InvalidRefreshToken,
    WeakPassword,
    InvalidEmail,
    #[allow(dead_code)]
    Token(jsonwebtoken::errors::Error),
    #[allow(dead_code)]
    Database(DbErr),
    #[allow(dead_code)]
    Hash(bcrypt::BcryptError),
    EmailNotVerified,
    EmailAlreadyVerified,
    InvalidVerificationCode,
}

impl From<DbErr> for AuthError {
    fn from(value: DbErr) -> Self {
        Self::Database(value)
    }
}

impl From<bcrypt::BcryptError> for AuthError {
    fn from(value: bcrypt::BcryptError) -> Self {
        Self::Hash(value)
    }
}

impl From<jsonwebtoken::errors::Error> for AuthError {
    fn from(value: jsonwebtoken::errors::Error) -> Self {
        Self::Token(value)
    }
}

impl From<EmailVerificationError> for AuthError {
    fn from(value: EmailVerificationError) -> Self {
        match value {
            EmailVerificationError::Database(err) => Self::Database(err),
            EmailVerificationError::Hash(err) => Self::Hash(err),
            EmailVerificationError::NotFound
            | EmailVerificationError::Expired
            | EmailVerificationError::InvalidCode => Self::InvalidVerificationCode,
        }
    }
}

struct AuthTokenPair {
    access_token: String,
    refresh_token: String,
}

fn valid_email(email: &str) -> bool {
    let email = email.trim();
    // very basic RFC 5322-compliant email regex for demonstration (not perfect)
    let email_regex = regex::Regex::new(r"(?i)^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$").unwrap();
    email_regex.is_match(email) && email.len() <= 320
}

/// Returns the user ID if the user was created successfully, or an error if the user was not created.
pub async fn register_pending(
    db: &sea_orm::DatabaseConnection,
    clock: &impl Clock,
    body: RegisterRequest,
    role: Role,
) -> Result<UserIdType, AuthError> {
    if !valid_email(&body.email) {
        return Err(AuthError::InvalidEmail);
    }
    if body.password.len() < 8 {
        return Err(AuthError::WeakPassword);
    }

    let email = body.email.trim().to_owned();
    if repo::find_by_email(db, &email).await?.is_some() {
        return Err(AuthError::EmailTaken);
    }

    let salt = password::generate_salt();
    let hash = password::hash_password(&body.password, &salt)?;
    let user =
        repo::create_pending_user(db, email.clone(), hash, salt, role, clock.now_db()).await?;

    Ok(user.id)
}

pub async fn login_bypass(
    db: &sea_orm::DatabaseConnection,
    clock: &impl Clock,
    body: LoginRequest,
    settings: &AccessTokenIssueSettings,
) -> Result<LoginResponse, AuthError> {
    if environment::is_prod() {
        return Err(AuthError::InvalidCredentials);
    }

    let email = body.email.trim();
    let Some(user) = repo::find_by_email(db, email).await? else {
        return Err(AuthError::InvalidCredentials);
    };

    let tokens = issue_auth_tokens(db, clock, &user, settings).await?;
    Ok(login_response(user, tokens))
}

pub async fn login(
    db: &sea_orm::DatabaseConnection,
    clock: &impl Clock,
    body: LoginRequest,
    settings: &AccessTokenIssueSettings,
) -> Result<LoginResponse, AuthError> {
    let email = body.email.trim();
    let Some(user) = repo::find_by_email(db, email).await? else {
        return Err(AuthError::InvalidCredentials);
    };

    if !password::verify_password(&body.password, &user.salt, &user.password_hash)? {
        return Err(AuthError::InvalidCredentials);
    }

    let is_email_verified = repo::is_email_registered(db, user.id)
        .await
        .map_err(AuthError::Database)?;

    if !is_email_verified {
        return Err(AuthError::EmailNotVerified);
    }

    let tokens = issue_auth_tokens(db, clock, &user, settings).await?;
    Ok(login_response(user, tokens))
}

pub async fn refresh_tokens(
    db: &sea_orm::DatabaseConnection,
    clock: &impl Clock,
    body: RefreshTokenRequest,
    settings: &AccessTokenIssueSettings,
) -> Result<RefreshTokenResponse, AuthError> {
    let refresh_token = body.refresh_token.trim();
    if refresh_token.is_empty() {
        return Err(AuthError::InvalidRefreshToken);
    }

    let claims = tokens::decode_claims(&settings.jwt_secret, refresh_token)
        .map_err(|_| AuthError::InvalidRefreshToken)?;

    if claims.typ != tokens::TOKEN_TYPE_REFRESH {
        return Err(AuthError::InvalidRefreshToken);
    }

    if claims.exp <= clock.now_utc().timestamp() {
        return Err(AuthError::InvalidRefreshToken);
    }

    let user_id: i32 = claims
        .sub
        .parse()
        .map_err(|_| AuthError::InvalidRefreshToken)?;

    let Some(user) = repo::find_by_id(db, user_id).await? else {
        return Err(AuthError::InvalidRefreshToken);
    };

    let Some(ref stored_hash) = user.refresh_token_hash else {
        return Err(AuthError::InvalidRefreshToken);
    };

    if !tokens::verify_refresh_token_jti(&claims.jti, stored_hash)? {
        return Err(AuthError::InvalidRefreshToken);
    }

    repo::set_refresh_token_hash(db, user.id, None).await?;

    let tokens = issue_auth_tokens(db, clock, &user, settings).await?;
    Ok(RefreshTokenResponse {
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
    })
}

/// Revokes the refresh token if it is currently valid. Always succeeds from the caller's
/// perspective when the token is already invalid (idempotent logout).
pub async fn logout(
    db: &sea_orm::DatabaseConnection,
    clock: &impl Clock,
    body: RefreshTokenRequest,
    settings: &AccessTokenIssueSettings,
) -> Result<(), AuthError> {
    let refresh_token = body.refresh_token.trim();
    if refresh_token.is_empty() {
        return Ok(());
    }

    let Ok(claims) = tokens::decode_claims(&settings.jwt_secret, refresh_token) else {
        return Ok(());
    };

    if claims.typ != tokens::TOKEN_TYPE_REFRESH {
        return Ok(());
    }

    if claims.exp <= clock.now_utc().timestamp() {
        return Ok(());
    }

    let Ok(user_id) = claims.sub.parse::<i32>() else {
        return Ok(());
    };

    let Some(user) = repo::find_by_id(db, user_id).await? else {
        return Ok(());
    };

    let Some(ref stored_hash) = user.refresh_token_hash else {
        return Ok(());
    };

    if tokens::verify_refresh_token_jti(&claims.jti, stored_hash)? {
        repo::set_refresh_token_hash(db, user.id, None).await?;
    }

    Ok(())
}

pub async fn verify_email(
    db: &sea_orm::DatabaseConnection,
    clock: &impl Clock,
    body: VerifyEmailRequest,
) -> Result<VerifyEmailResponse, AuthError> {
    let email = body.email.trim();
    if !valid_email(email) {
        return Err(AuthError::InvalidEmail);
    }

    let Some(user) = repo::find_by_email(db, email).await? else {
        return Err(AuthError::InvalidVerificationCode);
    };

    if !user.email_verified {
        email_server::service::verify_pending_email(db, clock, user.id, body.code.trim()).await?;
        repo::set_email_verified(db, user.id, true).await?;
        Ok(VerifyEmailResponse {
            message: "Email verified.".to_string(),
        })
    } else {
        Err(AuthError::EmailAlreadyVerified)
    }
}

pub async fn force_verify_email(
    db: &sea_orm::DatabaseConnection,
    user_id: i32,
) -> Result<(), AuthError> {
    repo::set_email_verified(db, user_id, true).await?;
    Ok(())
}

pub async fn prepare_verification_email_resend(
    db: &sea_orm::DatabaseConnection,
    clock: &impl Clock,
    body: ResendVerificationEmailRequest,
) -> Result<Option<PendingEmailVerificationResponse>, AuthError> {
    let email = body.email.trim();
    if !valid_email(email) {
        return Ok(None);
    }

    let Some(user) = repo::find_by_email(db, email).await? else {
        return Ok(None);
    };

    if user.email_verified {
        return Ok(None);
    }

    email_server::service::add_pending_email_verification(db, clock, user.id)
        .await
        .map(Some)
        .map_err(AuthError::from)
}

pub fn user_id_from_token(
    jwt_secret: &str,
    clock: &impl Clock,
    token: &str,
) -> Result<i32, AuthError> {
    let claims = tokens::decode_claims(jwt_secret, token)?;

    if claims.typ != tokens::TOKEN_TYPE_ACCESS {
        return Err(AuthError::InvalidCredentials);
    }

    if claims.exp <= clock.now_utc().timestamp() {
        return Err(AuthError::InvalidCredentials);
    }

    claims
        .sub
        .parse()
        .map_err(|_| AuthError::InvalidCredentials)
}

async fn issue_auth_tokens(
    db: &sea_orm::DatabaseConnection,
    clock: &impl Clock,
    user: &user::Model,
    settings: &AccessTokenIssueSettings,
) -> Result<AuthTokenPair, AuthError> {
    let AccessTokenIssueSettings {
        jwt_secret,
        access_token_ttl,
        refresh_token_ttl,
    } = settings;

    let access_token = tokens::issue_access_token(jwt_secret, user.id, clock, *access_token_ttl)?;
    let refresh_token =
        tokens::issue_refresh_token(jwt_secret, user.id, clock, *refresh_token_ttl)?;
    let refresh_claims = tokens::decode_claims(jwt_secret, &refresh_token)?;
    let refresh_token_hash = tokens::hash_refresh_token_jti(&refresh_claims.jti)?;

    repo::set_refresh_token_hash(db, user.id, Some(refresh_token_hash)).await?;
    repo::set_last_login_at(db, user.id, clock.now_db()).await?;

    Ok(AuthTokenPair {
        access_token,
        refresh_token,
    })
}

fn login_response(user: user::Model, tokens: AuthTokenPair) -> LoginResponse {
    LoginResponse {
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        user_id: user.id,
        email: user.email,
    }
}
