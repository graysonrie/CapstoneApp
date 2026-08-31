use axum::{Json, Router, extract::State, routing::post};
use server_types::user::requests::DeleteUserRequest;
mod dev;

use crate::{
    features::{
        auth::middleware::require_super_admin_auth,
        user::{errors::UserHttpError, service},
    },
    state::AppState,
};

pub fn user_router(state: AppState) -> Router<AppState> {
    let super_admin_routes = Router::new()
        .route("/user/delete", post(delete_user))
        .route_layer(axum::middleware::from_fn_with_state(
            state,
            require_super_admin_auth,
        ));
    let dev_routes = dev::map_routes_if_in_dev(Router::new());
    Router::new().merge(super_admin_routes).merge(dev_routes)
}

async fn delete_user(
    State(state): State<AppState>,
    Json(body): Json<DeleteUserRequest>,
) -> Result<(), UserHttpError> {
    service::delete_user_with_email(&state.db, body.email)
        .await
        .map_err(UserHttpError::from)
}
