use sea_orm::{
    ActiveModelTrait, ActiveValue::NotSet, ColumnTrait, ConnectionTrait, DbErr, DeleteResult,
    EntityTrait, QueryFilter, Set, entity::prelude::DateTimeWithTimeZone,
};

use crate::features::db::models::{
    email_verification::{self, ActiveModel, Column, Entity},
    user::UserIdType,
};

pub async fn create_email(
    db: &impl ConnectionTrait,
    user_id: UserIdType,
    plain_text_code: &str,
    created_at: DateTimeWithTimeZone,
    expires_at: DateTimeWithTimeZone,
) -> Result<email_verification::Model, DbErr> {
    let code_hash = bcrypt::hash(plain_text_code, bcrypt::DEFAULT_COST)
        .map_err(|err| DbErr::Custom(err.to_string()))?;
    ActiveModel {
        id: NotSet,
        user_id: Set(user_id),
        code_hash: Set(code_hash),
        expires_at: Set(expires_at),
        created_at: Set(created_at),
        attempts: Set(0),
    }
    .insert(db)
    .await
}

pub async fn find_by_user_id(
    db: &impl ConnectionTrait,
    user_id: UserIdType,
) -> Result<Option<email_verification::Model>, DbErr> {
    Entity::find()
        .filter(Column::UserId.eq(user_id))
        .one(db)
        .await
}

pub async fn delete_by_user_id(
    db: &impl ConnectionTrait,
    user_id: UserIdType,
) -> Result<DeleteResult, DbErr> {
    Entity::delete_many()
        .filter(Column::UserId.eq(user_id))
        .exec(db)
        .await
}

pub async fn delete_expired(
    db: &impl ConnectionTrait,
    now: DateTimeWithTimeZone,
) -> Result<DeleteResult, DbErr> {
    Entity::delete_many()
        .filter(Column::ExpiresAt.lt(now))
        .exec(db)
        .await
}
