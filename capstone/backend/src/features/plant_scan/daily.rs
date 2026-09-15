use crate::prelude::*;

pub const NEW_SPECIES_XP: u32 = 10;
pub const DAILY_BONUS_XP: u32 = 20;

#[derive(Clone, Copy, Debug)]
pub struct DailyPlantDef {
    pub key: &'static str,
    pub common_name: &'static str,
    pub scientific_name: &'static str,
    pub aliases: &'static [&'static str],
}

pub const DAILY_PLANTS: &[DailyPlantDef] = &[
    DailyPlantDef {
        key: "ficus",
        common_name: "Ficus Tree",
        scientific_name: "Ficus benjamina",
        aliases: &["ficus"],
    },
    DailyPlantDef {
        key: "lantanas",
        common_name: "Lantanas",
        scientific_name: "Lantana camara",
        aliases: &["lantana"],
    },
    DailyPlantDef {
        key: "rosemary",
        common_name: "Rosemary",
        scientific_name: "Salvia rosmarinus",
        aliases: &["rosemary", "rosmarinus", "salvia rosmarinus"],
    },
];

pub fn normalize_name(value: &str) -> String {
    value
        .chars()
        .filter(|c| c.is_alphanumeric() || c.is_whitespace())
        .map(|c| c.to_ascii_lowercase())
        .collect::<String>()
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ")
}

pub fn match_daily_plant(common_name: Option<&str>, scientific_name: Option<&str>) -> Option<&'static DailyPlantDef> {
    let haystack = format!(
        "{} {}",
        common_name.unwrap_or(""),
        scientific_name.unwrap_or("")
    );
    let normalized = normalize_name(&haystack);
    if normalized.is_empty() {
        return None;
    }

    DAILY_PLANTS.iter().find(|plant| {
        plant
            .aliases
            .iter()
            .any(|alias| normalized.contains(&normalize_name(alias)))
    })
}

pub fn species_key(common_name: &str, scientific_name: &str) -> String {
    let scientific = normalize_name(scientific_name);
    if !scientific.is_empty() {
        scientific
    } else {
        normalize_name(common_name)
    }
}

/// Drop reference photos in `backend/assets/daily_plants/` named
/// `ficus.jpg`, `lantanas.jpg`, and `rosemary.jpg` (png/webp also work).
pub fn daily_plants_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("assets/daily_plants")
}

pub fn find_daily_image_path(key: &str) -> Option<PathBuf> {
    let dir = daily_plants_dir();
    let extensions = ["jpg", "jpeg", "png", "webp"];
    for ext in extensions {
        let path = dir.join(format!("{key}.{ext}"));
        if path.is_file() {
            return Some(path);
        }
    }
    None
}

pub fn image_mime_from_path(path: &Path) -> &'static str {
    match path
        .extension()
        .and_then(|ext| ext.to_str())
        .map(|ext| ext.to_ascii_lowercase())
        .as_deref()
    {
        Some("png") => "image/png",
        Some("webp") => "image/webp",
        Some("gif") => "image/gif",
        _ => "image/jpeg",
    }
}
