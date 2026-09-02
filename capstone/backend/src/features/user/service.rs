use super::repo;
use crate::features::db::models::user;
use crate::prelude::*;

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
