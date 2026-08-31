use sea_orm::entity::prelude::*;

use crate::features::db::models::user::UserIdType;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "email_verification")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = true)]
    pub id: i32,

    #[sea_orm(unique)]
    pub user_id: UserIdType,

    pub code_hash: String,

    pub expires_at: DateTimeWithTimeZone,
    pub attempts: u32,
    pub created_at: DateTimeWithTimeZone,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {}

impl ActiveModelBehavior for ActiveModel {}
