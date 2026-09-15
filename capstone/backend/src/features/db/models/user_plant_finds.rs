use sea_orm::entity::prelude::*;
use server_types::plant_scan::responses::Rarity as RarityType;

use crate::features::db::models::user::UserIdType;

/// A clone of what we have in the types crate
#[derive(Clone, Debug, PartialEq, EnumIter, DeriveActiveEnum)]
#[sea_orm(db_type = "Text")]
#[sea_orm(rs_type = "String")]
pub enum Rarity {
    #[sea_orm(string_value = "common")]
    Common,
    #[sea_orm(string_value = "uncommon")]
    Uncommon,
    #[sea_orm(string_value = "rare")]
    Rare,
    #[sea_orm(string_value = "super_rare")]
    SuperRare,
    #[sea_orm(string_value = "exotic")]
    Exotic,
}

impl From<RarityType> for Rarity {
    fn from(rarity: RarityType) -> Self {
        match rarity {
            RarityType::Common => Rarity::Common,
            RarityType::Uncommon => Rarity::Uncommon,
            RarityType::Rare => Rarity::Rare,
            RarityType::SuperRare => Rarity::SuperRare,
            RarityType::Exotic => Rarity::Exotic,
        }
    }
}

impl From<Rarity> for RarityType {
    fn from(rarity: Rarity) -> Self {
        match rarity {
            Rarity::Common => RarityType::Common,
            Rarity::Uncommon => RarityType::Uncommon,
            Rarity::Rare => RarityType::Rare,
            Rarity::SuperRare => RarityType::SuperRare,
            Rarity::Exotic => RarityType::Exotic,
        }
    }
}

#[derive(Clone, Debug, PartialEq, DeriveEntityModel)]
#[sea_orm(table_name = "user_plant_finds")]
pub struct Model {
    #[sea_orm(primary_key, auto_increment = true)]
    pub id: i32,

    pub user_id: UserIdType,

    pub name: String,
    pub scientific_name: String,
    pub rarity: Option<Rarity>,

    /// Calendar date the plant was found (format as e.g. "July 24" in the UI).
    pub found_on: Date,

    /// Relative path in file storage, e.g. `scans/{user_id}/{uuid}.jpg`
    pub image_path: Option<String>,
}

#[derive(Copy, Clone, Debug, EnumIter, DeriveRelation)]
pub enum Relation {
    #[sea_orm(
        belongs_to = "super::user::Entity",
        from = "Column::UserId",
        to = "super::user::Column::Id"
    )]
    User,
}

impl Related<super::user::Entity> for Entity {
    fn to() -> RelationDef {
        Relation::User.def()
    }
}

impl ActiveModelBehavior for ActiveModel {}
