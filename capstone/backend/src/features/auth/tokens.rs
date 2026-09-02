use chrono::Duration;
use jsonwebtoken::{Algorithm, DecodingKey, EncodingKey, Header, Validation, decode, encode};
use rand::RngExt;
use rand::rand_core::UnwrapErr;
use rand::rngs::SysRng;

use crate::prelude::*;

pub const TOKEN_TYPE_ACCESS: &str = "access";
pub const TOKEN_TYPE_REFRESH: &str = "refresh";

#[derive(Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,
    pub exp: i64,
    pub typ: String,
    /// Unique token id so rotated refresh tokens never collide within the same second.
    pub jti: String,
}

fn generate_jti() -> String {
    let mut rng = UnwrapErr(SysRng);
    (0..32)
        .map(|_| format!("{:02x}", rng.random::<u8>()))
        .collect()
}

pub fn decode_claims(jwt_secret: &str, token: &str) -> Result<Claims, jsonwebtoken::errors::Error> {
    let mut validation = Validation::new(Algorithm::HS256);
    validation.validate_exp = false;

    decode::<Claims>(
        token,
        &DecodingKey::from_secret(jwt_secret.as_bytes()),
        &validation,
    )
    .map(|data| data.claims)
}

pub fn issue_access_token(
    jwt_secret: &str,
    user_id: i32,
    clock: &impl Clock,
    ttl: Duration,
) -> Result<String, jsonwebtoken::errors::Error> {
    issue_token(
        jwt_secret,
        user_id,
        clock,
        ttl,
        TOKEN_TYPE_ACCESS,
    )
}

pub fn issue_refresh_token(
    jwt_secret: &str,
    user_id: i32,
    clock: &impl Clock,
    ttl: Duration,
) -> Result<String, jsonwebtoken::errors::Error> {
    issue_token(
        jwt_secret,
        user_id,
        clock,
        ttl,
        TOKEN_TYPE_REFRESH,
    )
}

fn issue_token(
    jwt_secret: &str,
    user_id: i32,
    clock: &impl Clock,
    ttl: Duration,
    typ: &str,
) -> Result<String, jsonwebtoken::errors::Error> {
    let exp = (clock.now_utc() + ttl).timestamp();
    let claims = Claims {
        sub: user_id.to_string(),
        exp,
        typ: typ.to_string(),
        jti: generate_jti(),
    };
    encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(jwt_secret.as_bytes()),
    )
}

/// Hash the refresh token's `jti` claim, not the full JWT. Bcrypt only uses the first
/// 72 bytes, so hashing entire JWTs can falsely match across different tokens.
pub fn hash_refresh_token_jti(jti: &str) -> Result<String, bcrypt::BcryptError> {
    bcrypt::hash(jti, bcrypt::DEFAULT_COST)
}

pub fn verify_refresh_token_jti(
    jti: &str,
    refresh_token_hash: &str,
) -> Result<bool, bcrypt::BcryptError> {
    bcrypt::verify(jti, refresh_token_hash)
}
