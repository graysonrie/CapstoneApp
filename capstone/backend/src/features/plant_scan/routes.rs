use crate::features::auth::middleware::{AuthenticatedUser, require_auth};
use crate::prelude::*;
use axum::extract::{DefaultBodyLimit, Multipart, Path as AxumPath, Query};

use super::errors::PlantScanHttpError;
use super::service;

const MAX_IMAGE_BYTES: usize = 10 * 1024 * 1024;

#[derive(Deserialize)]
struct RecentFindsQuery {
    count: u64,
    offset: u64,
    user_exclude: Option<UserIdType>,
}

pub fn plant_scan_router(state: AppState) -> Router<AppState> {
    Router::new()
        .route(
            "/plant-scan",
            post(scan_plant).layer(DefaultBodyLimit::max(MAX_IMAGE_BYTES)),
        )
        .route("/plant-scan/{plant_id}", get(retrieve_find))
        .route("/plant-image-locations", get(plant_image_locations))
        .route("/home", get(home))
        .route(
            "/plant-geo-distribution/{scientific_name}",
            get(get_plant_geo_distribution),
        )
        .route("/recent-finds", get(get_recent_finds))
        .route_layer(axum::middleware::from_fn_with_state(state, require_auth))
}

async fn get_plant_geo_distribution(
    AxumPath(scientific_name): AxumPath<String>,
) -> Result<Json<GbifResponse>, PlantScanHttpError> {
    service::get_plant_geo_distributition(&scientific_name)
        .await
        .map(Json)
        .map_err(PlantScanHttpError::from)
}

async fn retrieve_find(
    user: AuthenticatedUser,
    State(state): State<AppState>,
    AxumPath(plant_id): AxumPath<i32>,
) -> Result<Json<PlantScan>, PlantScanHttpError> {
    service::retrieve_find(&state.db, user.user_id, plant_id)
        .await
        .map(Json)
        .map_err(PlantScanHttpError::from)
}

async fn plant_image_locations(
    user: AuthenticatedUser,
    State(state): State<AppState>,
) -> Result<Json<Vec<UserPlantImageLocation>>, PlantScanHttpError> {
    service::get_user_plant_image_locations(&state.db, state.file_storage, user.user_id)
        .await
        .map(Json)
        .map_err(PlantScanHttpError::from)
}

async fn home(
    user: AuthenticatedUser,
    State(state): State<AppState>,
) -> Result<Json<HomeResponse>, PlantScanHttpError> {
    service::get_home(&state.db, state.file_storage, &*state.clock, user.user_id)
        .await
        .map(Json)
        .map_err(PlantScanHttpError::from)
}

async fn get_recent_finds(
    State(state): State<AppState>,
    Query(params): Query<RecentFindsQuery>,
) -> Result<Json<Vec<RecentFind>>, PlantScanHttpError> {
    service::get_recent_finds(
        &state.db,
        state.file_storage,
        params.count,
        params.offset,
        params.user_exclude,
    )
    .await
    .map(Json)
    .map_err(PlantScanHttpError::from)
}

async fn scan_plant(
    user: AuthenticatedUser,
    State(state): State<AppState>,
    mut multipart: Multipart,
) -> Result<Json<PlantScanResult>, PlantScanHttpError> {
    let mut image_bytes: Option<Vec<u8>> = None;
    let mut mime = "image/jpeg".to_string();
    let mut extension = "jpg".to_string();

    while let Some(field) = multipart.next_field().await.map_err(|_| {
        PlantScanHttpError((StatusCode::BAD_REQUEST, "invalid multipart body".into()))
    })? {
        let name = field.name().unwrap_or("").to_string();
        if name != "image" {
            continue;
        }
        if let Some(file_name) = field.file_name() {
            extension = Path::new(file_name)
                .extension()
                .and_then(|ext| ext.to_str())
                .unwrap_or("jpg")
                .to_ascii_lowercase();
        }
        if let Some(content_type) = field.content_type() {
            mime = content_type.to_string();
        }
        let bytes = field.bytes().await.map_err(|_| {
            PlantScanHttpError((StatusCode::BAD_REQUEST, "failed to read image".into()))
        })?;
        if bytes.len() > MAX_IMAGE_BYTES {
            return Err(PlantScanHttpError((
                StatusCode::BAD_REQUEST,
                "image is too large".into(),
            )));
        }
        image_bytes = Some(bytes.to_vec());
        break;
    }

    let Some(image_bytes) = image_bytes else {
        return Err(PlantScanHttpError((
            StatusCode::BAD_REQUEST,
            "image is required".into(),
        )));
    };

    tracing::info!(
        user_id = user.user_id,
        image_bytes = image_bytes.len(),
        mime = %mime,
        "received plant scan request"
    );

    service::scan_plant_image(
        &state.db,
        &*state.clock,
        state.file_storage,
        &state.app_config,
        user.user_id,
        image_bytes,
        &mime,
        &extension,
    )
    .await
    .map(Json)
    .map_err(PlantScanHttpError::from)
}
