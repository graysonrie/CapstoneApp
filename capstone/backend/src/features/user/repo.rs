use crate::features::db::models::user::{self, Column, Entity};
use crate::prelude::*;

pub async fn find_by_email(
    db: &impl ConnectionTrait,
    email: &str,
) -> Result<Option<user::Model>, DbErr> {
    Entity::find().filter(Column::Email.eq(email)).one(db).await
}

pub async fn get_all_users(db: &impl ConnectionTrait) -> Result<Vec<user::Model>, DbErr> {
    Entity::find().all(db).await
}

pub async fn create_user(
    db: &impl ConnectionTrait,
    user: user::ActiveModel,
) -> Result<user::Model, DbErr> {
    user.insert(db).await
}

pub async fn update_user(
    db: &impl ConnectionTrait,
    user: user::ActiveModel,
) -> Result<user::Model, DbErr> {
    user.update(db).await
}

pub async fn delete_user(
    db: &impl ConnectionTrait,
    user_id: UserIdType,
) -> Result<DeleteResult, DbErr> {
    Entity::delete_by_id(user_id).exec(db).await
}

pub async fn find_by_id(
    db: &impl ConnectionTrait,
    user_id: UserIdType,
) -> Result<Option<user::Model>, DbErr> {
    Entity::find_by_id(user_id).one(db).await
}
