use super::repo;
use crate::features::db::models::user;
use crate::prelude::*;

pub const USAGE_INTENT_OPTIONS: &[&str] = &[
    "Just for fun",
    "Learning",
    "Gardening",
    "Work or school",
];

#[derive(Debug)]
pub enum UserError {
    Database(DbErr),
    InvalidProfile,
    NotFound,
}

impl From<DbErr> for UserError {
    fn from(value: DbErr) -> Self {
        Self::Database(value)
    }
}

pub fn is_profile_complete(user: &user::Model) -> bool {
    let first = user.first_name.as_deref().unwrap_or("").trim();
    let last = user.last_name.as_deref().unwrap_or("").trim();
    let intent = user.usage_intent.as_deref().unwrap_or("").trim();
    !first.is_empty() && !last.is_empty() && !intent.is_empty()
}

pub async fn delete_user_with_email(
    db: &sea_orm::DatabaseConnection,
    email: String,
) -> Result<(), DbErr> {
    let email = email.trim();
    let Some(user) = repo::find_by_email(db, email).await? else {
        tracing::warn!("User not found: {}", email);
        return Err(DbErr::RecordNotFound("User not found".to_string()));
    };

    let user_id = user.id;
    repo::delete_user(db, user_id).await?;
    tracing::info!("User deleted: {}", email);
    Ok(())
}

pub async fn get_user_by_id(
    db: &sea_orm::DatabaseConnection,
    user_id: i32,
) -> Result<user::Model, DbErr> {
    let Some(user) = repo::find_by_id(db, user_id).await? else {
        return Err(DbErr::RecordNotFound("User not found".to_string()));
    };
    Ok(user)
}

pub async fn change_role(
    db: &sea_orm::DatabaseConnection,
    email: String,
    role: Role,
) -> Result<(), DbErr> {
    let email = email.trim();
    let Some(user) = repo::find_by_email(db, email).await? else {
        return Err(DbErr::RecordNotFound("User not found".to_string()));
    };

    let mut user_active_model: user::ActiveModel = user.into();
    user_active_model.role = Set(role);

    repo::update_user(db, user_active_model).await?;
    Ok(())
}

pub async fn complete_profile(
    db: &sea_orm::DatabaseConnection,
    user_id: i32,
    body: CompleteProfileRequest,
) -> Result<CompleteProfileResponse, UserError> {
    let first_name = body.first_name.trim().to_owned();
    let last_name = body.last_name.trim().to_owned();
    let usage_intent = body.usage_intent.trim().to_owned();

    if first_name.is_empty() || last_name.is_empty() {
        return Err(UserError::InvalidProfile);
    }
    if !USAGE_INTENT_OPTIONS.contains(&usage_intent.as_str()) {
        return Err(UserError::InvalidProfile);
    }

    let Some(user) = repo::find_by_id(db, user_id).await? else {
        return Err(UserError::NotFound);
    };

    let mut active: user::ActiveModel = user.into();
    active.first_name = Set(Some(first_name));
    active.last_name = Set(Some(last_name));
    active.usage_intent = Set(Some(usage_intent));
    repo::update_user(db, active).await?;

    Ok(CompleteProfileResponse { success: true })
}
