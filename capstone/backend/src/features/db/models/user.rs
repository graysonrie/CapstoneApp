use sea_orm::entity::prelude::*;
use serde::{Deserialize, Serialize};

use crate::features::auth::Role;

pub type UserIdType = i32;

pub fn max_xp_needed_for_level(level: u32) -> u32 {
    level * 30
}

pub fn rank_title_for_level(level: u32) -> &'static str {
    match level {
        0 => "Hacker",
        1 => "Weed Eater",
        2..=3 => "Gardener",
        _ => "Plant Master",
    }
}

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

    // App-specific fields:
    pub level: u32,
    pub rank_title: String,
    pub xp: u32,
    /// The XP needed to reach the next level
    pub max_xp: u32,

    /// The user IDs of the people that have accepted this user's friend request
    pub friend_user_ids: UserIdVec,
    /// The user IDs of the people that have not yet accepted this user's friend request
    pub pending_friend_user_ids: UserIdVec,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(has_many = "super::user_plant_finds::Entity")]
    UserPlantFinds,
}

impl Related<super::user_plant_finds::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::UserPlantFinds.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}

#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize, FromJsonQueryResult)]
pub struct StringVec(pub Vec<String>);

#[derive(Clone, Default, Debug, PartialEq, Eq, Serialize, Deserialize, FromJsonQueryResult)]
pub struct UserIdVec(pub Vec<UserIdType>);
