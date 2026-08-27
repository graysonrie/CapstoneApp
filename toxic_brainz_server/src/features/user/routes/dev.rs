use super::*;
use axum::Router;
use server_types::prelude::*;

use crate::{environment::is_dev, features::auth::Role, state::AppState};

/// ONLY implements the routes if in dev mode
pub fn map_routes_if_in_dev(router: Router<AppState>) -> Router<AppState> {
    if is_dev() {
        tracing::warn!("Dev environment: Dev user routes are getting mapped");
    } else {
        return router;
    }

    router.route("/user/change-role/bypass", post(change_role_bypass))
}

/// Only in dev environment
async fn change_role_bypass(
    State(state): State<AppState>,
    Json(body): Json<ChangeRoleRequest>,
) -> Result<Json<ChangeRoleResponse>, UserHttpError> {
    service::change_role(&state.db, body.email, body.role.into())
        .await
        .map_err(UserHttpError::from)?;
    Ok(Json(ChangeRoleResponse { success: true }))
}
