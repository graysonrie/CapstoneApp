use serde::{Deserialize, Serialize};

/// The complete JSON response that the Axum backend will return back
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct PlantScan {
    pub is_plant: bool,
    pub identification: Identification,
    pub summary: String,
    pub sections: PlantSections,
    pub identification_notes: IdentificationNotes,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Identification {
    pub common_name: Option<String>,
    pub scientific_name: Option<String>,
    pub family: Option<String>,
    pub confidence: Confidence,
    /// Assuming that the identification is mostly correct, how rare the plant is.
    ///
    /// A null rarity implies that the model could not accurately discern the plant.
    pub rarity: Option<Rarity>,
}

#[derive(Debug, Deserialize, Serialize, Clone, Copy, PartialEq, Eq)]
pub enum Rarity {
    Common,
    Uncommon,
    Rare,
    SuperRare,
    Exotic,
}

#[derive(Debug, Deserialize, Serialize, Clone, Copy, PartialEq, Eq)]
pub enum Confidence {
    High,
    Medium,
    Low,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct PlantSections {
    pub appearance: String,
    pub native_range: Option<String>,
    pub care: Option<Care>,
    pub interesting_facts: Vec<String>,
    pub toxicity: Option<Toxicity>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Care {
    pub light: Option<String>,
    pub watering: Option<String>,
    pub soil: Option<String>,
    pub temperature: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Toxicity {
    /// Notes about the toxicity towards humans, if any
    pub humans: Option<String>,
    /// Notes about the toxicity towards domestic animals, if any
    pub pets: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct IdentificationNotes {
    /// Why exactly the model classified the plant into the certain [`Identification`]
    ///
    /// Example summary: "The broad glossy leaves and characteristic fenestrations are consistent with Monstera deliciosa."
    pub reasoning_summary: Option<String>,
    /// Facts that may persuade the model in a different direction.
    ///
    /// Example uncertainty: "Some related Monstera species can appear similar from a single photograph."
    pub uncertainty: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct DailyMatch {
    pub key: String,
    pub common_name: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct PlantScanResult {
    pub scan: PlantScan,
    pub xp_awarded: u32,
    pub is_new_species: bool,
    pub daily_match: Option<DailyMatch>,
    pub leveled_up: bool,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct DailyPlantQuest {
    pub key: String,
    pub common_name: String,
    pub scientific_name: String,
    pub rarity: Rarity,
    pub xp_reward: u32,
    pub found: bool,
    pub image_base64: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct HomeResponse {
    pub first_name: Option<String>,
    pub level: u32,
    pub rank_title: String,
    pub xp: u32,
    pub max_xp: u32,
    pub quests: Vec<DailyPlantQuest>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct CollectionPlant {
    pub id: i32,
    pub common_name: String,
    pub scientific_name: String,
    pub rarity: Option<Rarity>,
    pub found_on: String,
    pub image_base64: Option<String>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ProfileRank {
    pub level: u32,
    pub name: String,
    pub next_rank: String,
    pub xp: u32,
    pub xp_to_next: u32,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ProfileStats {
    pub scans: u32,
    pub unique_species: u32,
    pub streak_days: u32,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ProfileResponse {
    pub first_name: Option<String>,
    pub last_name: Option<String>,
    pub joined_at: String,
    pub rank: ProfileRank,
    pub stats: ProfileStats,
    pub found_plants: Vec<CollectionPlant>,
}
