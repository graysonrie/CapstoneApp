use serde::{Deserialize, Serialize};

/// The complete JSON response that the Axum backend will return back
#[derive(Serialize, Deserialize, Debug)]
pub struct PlantScan {
    identification: Identification,
    summary: String,
    sections: PlantSections,
    identification_notes: IdentificationNotes,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Identification {
    common_name: Option<String>,
    scientific_name: Option<String>,
    family: Option<String>,
    confidence: Confidence,
    /// Assuming that the identification is mostly correct, how rare the plant is.
    ///
    /// A null rarity implies that the model could not accurately discern the plant.
    rarity: Option<Rarity>,
}

#[derive(Debug, Deserialize, Serialize)]
pub enum Rarity {
    Common,
    Uncommon,
    Rare,
    SuperRare,
    Exotic,
}

#[derive(Debug, Deserialize, Serialize)]
pub enum Confidence {
    High,
    Medium,
    Low,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct PlantSections {
    appearance: String,
    native_range: Option<String>,
    care: Option<Care>,
    interesting_facts: Vec<String>,
    toxicity: Option<Toxicity>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Care {
    light: Option<String>,
    watering: Option<String>,
    soil: Option<String>,
    temperature: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Toxicity {
    /// Notes about the toxicity towards humans, if any
    humans: Option<String>,
    /// Notes about the toxicity towards domestic animals, if any
    pets: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct IdentificationNotes {
    /// Why exactly the model classified the plant into the certain [`Identification`]
    ///
    /// Example summary: "The broad glossy leaves and characteristic fenestrations are consistent with Monstera deliciosa."
    reasoning_summary: Option<String>,
    /// Facts that may persuade the model in a different direction.
    ///
    /// Example uncertainty: "Some related Monstera species can appear similar from a single photograph."
    uncertainty: Option<String>,
}
