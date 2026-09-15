use crate::features::auth::middleware::{require_auth, AuthenticatedUser};
use crate::prelude::*;
use axum::extract::Multipart;

use super::errors::PlantScanHttpError;
use super::service;

const MAX_IMAGE_BYTES: usize = 10 * 1024 * 1024;

pub fn plant_scan_router(state: AppState) -> Router<AppState> {
    Router::new()
        .route("/plant-scan", post(scan_plant))
        .route("/home", get(home))
        .route_layer(axum::middleware::from_fn_with_state(state, require_auth))
}

async fn home(
    user: AuthenticatedUser,
    State(state): State<AppState>,
) -> Result<Json<HomeResponse>, PlantScanHttpError> {
    service::get_home(&state.db, state.file_storage.as_ref(), &*state.clock, user.user_id)
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

    service::scan_plant_image(
        &state.db,
        &*state.clock,
        state.file_storage.as_ref(),
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
