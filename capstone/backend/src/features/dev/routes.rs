use crate::prelude::*;

pub fn dev_router() -> Router<AppState> {
    if is_dev() {
        tracing::warn!("Dev environment: Main dev routes are getting mapped");
    } else {
        return Router::new();
    }
    Router::new().route("/dev/erase-db", post(erase_db))
}

async fn erase_db(State(state): State<AppState>) -> Result<(), impl IntoResponse> {
    tracing::warn!("Attempting to erase database");
    crate::features::db::erase_and_recreate_all_tables(&state.db)
        .await
        .map_err(|_| (StatusCode::INTERNAL_SERVER_ERROR, "I am error".to_string()))
}
