use crate::features::db::models::user;
use crate::features::db::models::user_plant_finds::{self, ActiveModel, Column, Entity, Rarity};
use crate::prelude::*;
use chrono::NaiveDate;
use sea_orm::{QueryOrder, QuerySelect};
use server_types::plant_scan::responses::PlantScan;

#[derive(Debug, sea_orm::DerivePartialModel)]
#[sea_orm(entity = "user::Entity")]
pub struct RecentFindUser {
    pub first_name: Option<String>,
    pub last_name: Option<String>,
}

pub async fn insert_find(
    db: &impl ConnectionTrait,
    user_id: UserIdType,
    name: String,
    scientific_name: String,
    rarity: Option<Rarity>,
    found_on: NaiveDate,
    image_path: Option<String>,
    scan: &PlantScan,
) -> Result<user_plant_finds::Model, DbErr> {
    let scan_response =
        serde_json::to_string(scan).map_err(|error| DbErr::Custom(error.to_string()))?;
    ActiveModel {
        id: NotSet,
        user_id: Set(user_id),
        name: Set(name),
        scientific_name: Set(scientific_name),
        rarity: Set(rarity),
        found_on: Set(found_on),
        image_path: Set(image_path),
        scan_response: Set(Some(scan_response)),
    }
    .insert(db)
    .await
}

pub async fn list_by_user(
    db: &impl ConnectionTrait,
    user_id: UserIdType,
) -> Result<Vec<user_plant_finds::Model>, DbErr> {
    Entity::find()
        .filter(Column::UserId.eq(user_id))
        .order_by_desc(Column::FoundOn)
        .order_by_desc(Column::Id)
        .all(db)
        .await
}

pub async fn list_by_user_on_date(
    db: &impl ConnectionTrait,
    user_id: UserIdType,
    found_on: NaiveDate,
) -> Result<Vec<user_plant_finds::Model>, DbErr> {
    Entity::find()
        .filter(Column::UserId.eq(user_id))
        .filter(Column::FoundOn.eq(found_on))
        .all(db)
        .await
}

pub async fn find_by_id(
    db: &impl ConnectionTrait,
    user_id: UserIdType,
    plant_id: i32,
) -> Result<Option<user_plant_finds::Model>, DbErr> {
    Entity::find_by_id(plant_id)
        .filter(Column::UserId.eq(user_id))
        .one(db)
        .await
}

/**
 * List recent plant finds, passing in user_exclude to filter out a specific user's finds.
 */
pub async fn list_recent(
    db: &impl ConnectionTrait,
    count: u64,
    offset: u64,
    user_exclude: Option<UserIdType>,
) -> Result<Vec<(user_plant_finds::Model, Option<RecentFindUser>)>, DbErr> {
    let mut query = Entity::find()
        .find_also_related(user::Entity)
        .order_by_desc(Column::FoundOn)
        .order_by_desc(Column::Id)
        .offset(offset)
        .limit(count);

    if let Some(user_id) = user_exclude {
        query = query.filter(Column::UserId.ne(user_id));
    }

    query
        .into_partial_model::<user_plant_finds::Model, RecentFindUser>()
        .all(db)
        .await
}
