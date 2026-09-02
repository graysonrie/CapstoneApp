use crate::features::db::models::user::{self, ActiveModel, Column, Entity};
use crate::prelude::*;

pub async fn find_by_email(
    db: &impl ConnectionTrait,
    email: &str,
) -> Result<Option<user::Model>, DbErr> {
    Entity::find().filter(Column::Email.eq(email)).one(db).await
}

pub async fn find_by_id(
    db: &impl ConnectionTrait,
    user_id: i32,
) -> Result<Option<user::Model>, DbErr> {
    Entity::find_by_id(user_id).one(db).await
}

/// True if the user has registered their email. Will return an error if the user was not found or if there was a
/// db error
pub async fn is_email_registered(db: &impl ConnectionTrait, user_id: i32) -> Result<bool, DbErr> {
    if let Some(user) = Entity::find_by_id(user_id).one(db).await? {
        Ok(user.email_verified)
    } else {
        Err(DbErr::Custom("User not found".to_string()))
    }
}

pub async fn create_pending_user(
    db: &impl ConnectionTrait,
    email: String,
    password_hash: String,
    salt: String,
    role: Role,
    created_at: DateTimeWithTimeZone,
) -> Result<user::Model, DbErr> {
    ActiveModel {
        id: NotSet,
        email: Set(email),
        password_hash: Set(password_hash),
        salt: Set(salt),
        refresh_token_hash: Set(None),
        created_at: Set(created_at),
        email_verified: Set(false),
        role: Set(role),
        username: Set(None),
        last_login_at: Set(None),
    }
    .insert(db)
    .await
}

pub async fn set_email_verified(
    db: &impl ConnectionTrait,
    user_id: i32,
    value: bool,
) -> Result<UpdateResult, DbErr> {
    Entity::update_many()
        .filter(Column::Id.eq(user_id))
        .set(ActiveModel {
            email_verified: Set(value),
            ..Default::default()
        })
        .exec(db)
        .await
}

pub async fn set_refresh_token_hash(
    db: &impl ConnectionTrait,
    user_id: i32,
    refresh_token_hash: Option<String>,
) -> Result<UpdateResult, DbErr> {
    Entity::update_many()
        .filter(Column::Id.eq(user_id))
        .set(ActiveModel {
            refresh_token_hash: Set(refresh_token_hash),
            ..Default::default()
        })
        .exec(db)
        .await
}

pub async fn set_last_login_at(
    db: &impl ConnectionTrait,
    user_id: i32,
    last_login_at: DateTimeWithTimeZone,
) -> Result<UpdateResult, DbErr> {
    Entity::update_many()
        .filter(Column::Id.eq(user_id))
        .set(ActiveModel {
            last_login_at: Set(Some(last_login_at)),
            ..Default::default()
        })
        .exec(db)
        .await
}
