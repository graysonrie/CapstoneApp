mod dev;

use crate::features::{
    auth::middleware::{require_auth, require_super_admin_auth, AuthenticatedUser},
    user::{errors::UserHttpError, service},
};
use crate::prelude::*;

pub fn user_router(state: AppState) -> Router<AppState> {
    let authenticated_routes = Router::new()
        .route("/user/profile/complete", post(complete_profile))
        .route_layer(axum::middleware::from_fn_with_state(
            state.clone(),
            require_auth,
        ));

    let super_admin_routes = Router::new()
        .route("/user/delete", post(delete_user))
        .route_layer(axum::middleware::from_fn_with_state(
            state,
            require_super_admin_auth,
        ));
    let dev_routes = dev::map_routes_if_in_dev(Router::new());
    Router::new()
        .merge(authenticated_routes)
        .merge(super_admin_routes)
        .merge(dev_routes)
}

async fn delete_user(
    State(state): State<AppState>,
    Json(body): Json<DeleteUserRequest>,
) -> Result<(), UserHttpError> {
    service::delete_user_with_email(&state.db, body.email)
        .await
        .map_err(UserHttpError::from)
}

async fn complete_profile(
    user: AuthenticatedUser,
    State(state): State<AppState>,
    Json(body): Json<CompleteProfileRequest>,
) -> Result<Json<CompleteProfileResponse>, UserHttpError> {
    service::complete_profile(&state.db, user.user_id, body)
        .await
        .map(Json)
        .map_err(UserHttpError::from)
}
