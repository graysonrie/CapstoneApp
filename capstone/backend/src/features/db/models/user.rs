use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

use crate::features::auth::Role;

pub type UserIdType = i32;

#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "users")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = true)]
    pub id: UserIdType,
    #[sea_orm(unique)]
    pub email: String,
    pub password_hash: String,
    pub created_at: DateTimeWithTimeZone,
    pub email_verified: bool,
    pub role: Role,

    pub salt: String,
    pub refresh_token_hash: Option<String>,

    pub username: Option<String>,
    pub last_login_at: Option<DateTimeWithTimeZone>,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {}

impl ActiveModelBehavior for ActiveModel {}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize, FromJsonQueryResult)]
pub struct StringVec(pub Vec<String>);
