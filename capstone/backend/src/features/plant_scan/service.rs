use super::daily::{
    DAILY_BONUS_XP, DAILY_PLANTS, DailyPlantDef, NEW_SPECIES_XP, find_daily_image_path,
    image_mime_from_path, match_daily_plant, species_key,
};
use super::errors::PlantScanError;
use super::openai;
use super::repo;
use crate::features::db::models::user::{
    self as user_model, max_xp_needed_for_level, rank_title_for_level,
};
use crate::features::db::models::user_plant_finds::Rarity as DbRarity;
use crate::features::file_storage::file_storage_trait::FileStorageStateType;
use crate::features::user;
use crate::prelude::*;
use base64::Engine;
use exif::{In, Tag, Value};
use server_types::plant_scan::responses::{
    CollectionPlant, DailyMatch, DailyPlantQuest, HomeResponse, ImageGeolocation, ProfileRank,
    ProfileResponse, ProfileStats, Rarity, UserPlantImageLocation,
};
use std::io::Cursor;

const MAX_IMAGE_BYTES: usize = 10 * 1024 * 1024;

pub fn resolve_openai_settings(config: &AppConfig) -> Result<(String, String), PlantScanError> {
    let api_key = config
        .openai
        .api_key
        .clone()
        .or_else(|| std::env::var("OPENAI_API_KEY").ok())
        .filter(|key| !key.trim().is_empty())
        .ok_or(PlantScanError::MissingApiKey)?;
    let model = config
        .openai
        .model
        .clone()
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| "gpt-4o".to_string());
    Ok((api_key, model))
}

// technically this could be collapsed but this works for now
#[allow(clippy::too_many_arguments)]
pub async fn scan_plant_image(
    db: &DatabaseConnection,
    clock: &impl Clock,
    storage: FileStorageStateType,
    config: &AppConfig,
    user_id: UserIdType,
    image_bytes: Vec<u8>,
    mime: &str,
    extension: &str,
) -> Result<PlantScanResult, PlantScanError> {
    if image_bytes.is_empty() {
        return Err(PlantScanError::MissingImage);
    }
    if image_bytes.len() > MAX_IMAGE_BYTES {
        return Err(PlantScanError::ImageTooLarge);
    }

    let (api_key, model) = resolve_openai_settings(config)?;
    tracing::info!(
        bytes = image_bytes.len(),
        mime,
        "calling OpenAI for plant identification"
    );
    let scan = openai::identify_plant(&api_key, &model, &image_bytes, mime).await?;

    if !scan.is_plant {
        return Err(PlantScanError::NotAPlant);
    }

    let common_name = scan
        .identification
        .common_name
        .as_deref()
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .unwrap_or("Unknown plant")
        .to_string();
    let scientific_name = scan
        .identification
        .scientific_name
        .as_deref()
        .map(str::trim)
        .unwrap_or("")
        .to_string();

    if scan.identification.common_name.is_none() && scientific_name.is_empty() {
        return Err(PlantScanError::NotAPlant);
    }

    let existing = repo::list_by_user(db, user_id).await?;
    let key = species_key(&common_name, &scientific_name);
    let is_new_species = !existing
        .iter()
        .any(|find| species_key(&find.name, &find.scientific_name) == key);

    let today = clock.now_utc().date_naive();
    let todays_finds = repo::list_by_user_on_date(db, user_id, today).await?;

    let daily_def = match_daily_plant(Some(&common_name), Some(&scientific_name));
    let daily_already_found_today = daily_def.is_some_and(|plant| {
        todays_finds.iter().any(|find| {
            match_daily_plant(Some(&find.name), Some(&find.scientific_name))
                .is_some_and(|matched| matched.key == plant.key)
        })
    });
    let daily_match = daily_def
        .filter(|_| !daily_already_found_today)
        .map(|plant| DailyMatch {
            key: plant.key.to_string(),
            common_name: plant.common_name.to_string(),
        });

    let mut xp_awarded = 0;
    if is_new_species {
        xp_awarded += NEW_SPECIES_XP;
    }
    if daily_match.is_some() {
        xp_awarded += DAILY_BONUS_XP;
    }

    let relative_path = format!(
        "scans/{user_id}/{}.{}",
        uuid::Uuid::new_v4(),
        extension.trim_start_matches('.')
    );
    storage
        .write_file_bytes(&relative_path, &image_bytes)
        .await?;

    let rarity = scan.identification.rarity.map(DbRarity::from);
    repo::insert_find(
        db,
        user_id,
        common_name,
        scientific_name,
        rarity,
        today,
        Some(relative_path),
    )
    .await?;

    let leveled_up = if xp_awarded > 0 {
        apply_xp(db, user_id, xp_awarded).await?
    } else {
        false
    };

    Ok(PlantScanResult {
        scan,
        xp_awarded,
        is_new_species,
        daily_match,
        leveled_up,
    })
}

async fn apply_xp(
    db: &DatabaseConnection,
    user_id: UserIdType,
    awarded: u32,
) -> Result<bool, PlantScanError> {
    let user = user::service::get_user_by_id(db, user_id).await?;
    let starting_level = user.level;
    let mut level = user.level.max(1);
    let mut xp = user.xp + awarded;
    let mut max_xp = max_xp_needed_for_level(level);

    while xp >= max_xp {
        xp -= max_xp;
        level += 1;
        max_xp = max_xp_needed_for_level(level);
    }

    let mut active: user_model::ActiveModel = user.into();
    active.xp = Set(xp);
    active.level = Set(level);
    active.max_xp = Set(max_xp);
    active.rank_title = Set(rank_title_for_level(level).to_owned());
    active.update(db).await?;
    Ok(level > starting_level)
}

pub async fn get_home(
    db: &DatabaseConnection,
    storage: FileStorageStateType,
    clock: &impl Clock,
    user_id: UserIdType,
) -> Result<HomeResponse, PlantScanError> {
    let user = user::service::get_user_by_id(db, user_id).await?;
    let today = clock.now_utc().date_naive();
    let todays_finds = repo::list_by_user_on_date(db, user_id, today).await?;

    let mut quests = Vec::new();
    for plant in DAILY_PLANTS {
        let found = todays_finds.iter().any(|find| {
            match_daily_plant(Some(&find.name), Some(&find.scientific_name))
                .is_some_and(|matched| matched.key == plant.key)
        });
        quests.push(DailyPlantQuest {
            key: plant.key.to_string(),
            common_name: plant.common_name.to_string(),
            scientific_name: plant.scientific_name.to_string(),
            rarity: Rarity::Common,
            xp_reward: DAILY_BONUS_XP,
            found,
            image_base64: load_daily_image_base64(plant),
        });
    }

    let _storage = storage;
    Ok(HomeResponse {
        first_name: user.first_name,
        level: user.level,
        rank_title: user.rank_title,
        xp: user.xp,
        max_xp: user.max_xp,
        quests,
    })
}

fn load_daily_image_base64(plant: &DailyPlantDef) -> Option<String> {
    let path = find_daily_image_path(plant.key)?;
    let bytes = std::fs::read(&path).ok()?;
    let mime = image_mime_from_path(&path);
    Some(format!(
        "data:{mime};base64,{}",
        base64::engine::general_purpose::STANDARD.encode(bytes)
    ))
}

pub async fn get_profile(
    db: &DatabaseConnection,
    storage: FileStorageStateType,
    clock: &impl Clock,
    user_id: UserIdType,
) -> Result<ProfileResponse, PlantScanError> {
    let user = user::service::get_user_by_id(db, user_id).await?;
    let finds = repo::list_by_user(db, user_id).await?;
    let next_rank = rank_title_for_level(user.level.saturating_add(1)).to_string();

    let mut found_plants = Vec::new();
    for find in &finds {
        let image_base64 = match find.image_path.as_deref() {
            Some(path) => match storage.read_file_bytes(path).await {
                Ok(bytes) => {
                    let mime = image_mime_from_path(Path::new(path));
                    Some(format!(
                        "data:{mime};base64,{}",
                        base64::engine::general_purpose::STANDARD.encode(bytes)
                    ))
                }
                Err(err) => {
                    tracing::warn!("failed to read scan image {path}: {err}");
                    None
                }
            },
            None => None,
        };
        found_plants.push(CollectionPlant {
            id: find.id,
            common_name: find.name.clone(),
            scientific_name: find.scientific_name.clone(),
            rarity: find.rarity.clone().map(Into::into),
            found_on: format_found_on(find.found_on),
            image_base64,
        });
    }

    let unique_species = {
        let mut keys: Vec<String> = finds
            .iter()
            .map(|find| species_key(&find.name, &find.scientific_name))
            .filter(|key| !key.is_empty())
            .collect();
        keys.sort();
        keys.dedup();
        keys.len() as u32
    };

    Ok(ProfileResponse {
        first_name: user.first_name,
        last_name: user.last_name,
        joined_at: user.created_at.to_rfc3339(),
        rank: ProfileRank {
            level: user.level,
            name: user.rank_title,
            next_rank,
            xp: user.xp,
            xp_to_next: user.max_xp,
        },
        stats: ProfileStats {
            scans: finds.len() as u32,
            unique_species,
            streak_days: compute_streak(&finds, clock.now_utc().date_naive()),
        },
        found_plants,
    })
}

pub async fn get_user_plant_image_locations(
    db: &DatabaseConnection,
    storage: FileStorageStateType,
    user_id: UserIdType,
) -> Result<Vec<UserPlantImageLocation>, PlantScanError> {
    let finds = repo::list_by_user(db, user_id).await?;
    let mut image_locations = Vec::new();

    for find in finds {
        let Some(image_path) = find.image_path.as_deref() else {
            continue;
        };
        let image_bytes = storage.read_file_bytes(image_path).await?;
        let location = read_image_geolocation(&image_bytes);
        let thumbnail_data_url = location
            .as_ref()
            .and_then(|_| image_thumbnail_data_url(&image_bytes));
        image_locations.push(UserPlantImageLocation {
            image_id: find.id,
            common_name: find.name,
            location,
            thumbnail_data_url,
        });
    }

    Ok(image_locations)
}

fn image_thumbnail_data_url(image_bytes: &[u8]) -> Option<String> {
    let thumbnail = image::load_from_memory(image_bytes)
        .ok()?
        .thumbnail(320, 240);
    let mut encoded_image = Cursor::new(Vec::new());
    thumbnail
        .write_to(&mut encoded_image, image::ImageFormat::Jpeg)
        .ok()?;
    Some(format!(
        "data:image/jpeg;base64,{}",
        base64::engine::general_purpose::STANDARD.encode(encoded_image.into_inner())
    ))
}

fn read_image_geolocation(image_bytes: &[u8]) -> Option<ImageGeolocation> {
    let mut reader = exif::Reader::new();
    reader.continue_on_error(true);
    let exif = reader
        .read_from_container(&mut Cursor::new(image_bytes))
        .or_else(|error| {
            error.distill_partial_result(|errors| {
                tracing::warn!(?errors, "recovering image GPS from partial EXIF data");
            })
        })
        .ok()?;
    let latitude = read_exif_coordinate(
        &exif,
        Tag::GPSLatitude,
        Tag::GPSLatitudeRef,
        b"N",
        b"S",
        90.0,
    )?;
    let longitude = read_exif_coordinate(
        &exif,
        Tag::GPSLongitude,
        Tag::GPSLongitudeRef,
        b"E",
        b"W",
        180.0,
    )?;

    Some(ImageGeolocation {
        latitude,
        longitude,
    })
}

fn read_exif_coordinate(
    exif: &exif::Exif,
    coordinate_tag: Tag,
    reference_tag: Tag,
    positive_reference: &[u8],
    negative_reference: &[u8],
    maximum_degrees: f64,
) -> Option<f64> {
    let coordinate_field = exif.get_field(coordinate_tag, In::PRIMARY)?;
    let Value::Rational(parts) = &coordinate_field.value else {
        return None;
    };
    let [degrees, minutes, seconds] = parts.as_slice() else {
        return None;
    };
    if [degrees, minutes, seconds]
        .iter()
        .any(|part| part.denom == 0)
    {
        return None;
    }

    let reference_field = exif.get_field(reference_tag, In::PRIMARY)?;
    let Value::Ascii(references) = &reference_field.value else {
        return None;
    };
    let reference = references.first()?.as_slice();
    let sign = if reference == positive_reference {
        1.0
    } else if reference == negative_reference {
        -1.0
    } else {
        return None;
    };

    let degrees = degrees.to_f64();
    let minutes = minutes.to_f64();
    let seconds = seconds.to_f64();
    if minutes >= 60.0 || seconds >= 60.0 {
        return None;
    }
    let absolute_degrees = degrees + minutes / 60.0 + seconds / 3600.0;
    if !absolute_degrees.is_finite() || absolute_degrees > maximum_degrees {
        return None;
    }

    Some(sign * absolute_degrees)
}

fn format_found_on(date: chrono::NaiveDate) -> String {
    date.format("%B %d").to_string()
}

fn compute_streak(
    finds: &[crate::features::db::models::user_plant_finds::Model],
    today: chrono::NaiveDate,
) -> u32 {
    let mut days: Vec<chrono::NaiveDate> = finds.iter().map(|find| find.found_on).collect();
    days.sort();
    days.dedup();
    days.reverse();

    let mut streak = 0u32;
    let mut expected = today;
    for day in days {
        if day == expected {
            streak += 1;
            expected = expected.pred_opt().unwrap_or(expected);
        } else if day > expected {
            continue;
        } else {
            break;
        }
    }
    streak
}
