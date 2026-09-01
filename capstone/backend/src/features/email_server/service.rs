use rand::RngExt;
use rand::rand_core::UnwrapErr;
use rand::rngs::SysRng;
use sea_orm::DbErr;
use server_types::email_sender::responses::PendingEmailVerificationResponse;

use crate::{clock::Clock, features::db::models::user::UserIdType};

#[derive(Debug)]
pub enum EmailVerificationError {
    Database(DbErr),
    Hash(bcrypt::BcryptError),
    NotFound,
    Expired,
    InvalidCode,
}

impl From<DbErr> for EmailVerificationError {
    fn from(value: DbErr) -> Self {
        Self::Database(value)
    }
}

impl From<bcrypt::BcryptError> for EmailVerificationError {
    fn from(value: bcrypt::BcryptError) -> Self {
        Self::Hash(value)
    }
}

pub async fn add_pending_email_verification(
    db: &sea_orm::DatabaseConnection,
    clock: &impl Clock,
    user_id: UserIdType,
) -> Result<PendingEmailVerificationResponse, DbErr> {
    let code = generate_verification_code();
    let now_utc = clock.now_utc();
    let now = now_utc.fixed_offset();
    let expires_at = (now_utc + chrono::Duration::minutes(2)).fixed_offset();
    super::repo::delete_expired(db, now).await?;
    super::repo::delete_by_user_id(db, user_id).await?;
    super::repo::create_email(db, user_id, &code, now, expires_at).await?;
    Ok(PendingEmailVerificationResponse {
        plaintext_code: code,
    })
}

pub async fn verify_pending_email(
    db: &sea_orm::DatabaseConnection,
    clock: &impl Clock,
    user_id: UserIdType,
    plaintext_code: &str,
) -> Result<(), EmailVerificationError> {
    let now = clock.now_db();
    super::repo::delete_expired(db, now).await?;

    let Some(verification) = super::repo::find_by_user_id(db, user_id).await? else {
        return Err(EmailVerificationError::NotFound);
    };

    if verification.expires_at <= now {
        super::repo::delete_by_user_id(db, user_id).await?;
        return Err(EmailVerificationError::Expired);
    }

    const MAX_ATTEMPTS: u32 = 5;

    if !bcrypt::verify(plaintext_code, &verification.code_hash)? {
        let updated =
            super::repo::increment_attempts(db, verification.id, verification.attempts).await?;
        if updated.attempts >= MAX_ATTEMPTS {
            super::repo::delete_by_user_id(db, user_id).await?;
        }
        return Err(EmailVerificationError::InvalidCode);
    }

    super::repo::delete_by_user_id(db, user_id).await?;
    Ok(())
}

fn generate_verification_code() -> String {
    let mut rng = UnwrapErr(SysRng);
    format!("{:06}", rng.random_range(0..1_000_000))
}
