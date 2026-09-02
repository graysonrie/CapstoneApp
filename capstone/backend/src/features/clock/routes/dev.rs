use crate::prelude::*;

pub fn map_routes_if_in_dev(router: Router<AppState>) -> Router<AppState> {
    if is_dev() {
        tracing::warn!("Dev environment: Dev clock routes are getting mapped");
    } else {
        return router;
    }

    router
        .route("/dev/clock", get(get_clock))
        .route("/dev/clock/advance", post(advance_clock))
        .route("/dev/clock/reset", post(reset_clock))
}

async fn get_clock(State(state): State<AppState>) -> Json<ClockStatusResponse> {
    Json(clock_status(&state))
}

async fn advance_clock(
    State(state): State<AppState>,
    Json(body): Json<AdvanceClockRequest>,
) -> Result<Json<ClockStatusResponse>, StatusCode> {
    state
        .clock
        .advance_seconds(body.seconds)
        .map_err(|_| StatusCode::BAD_REQUEST)?;
    Ok(Json(clock_status(&state)))
}

async fn reset_clock(State(state): State<AppState>) -> Json<ClockStatusResponse> {
    state.clock.reset();
    Json(clock_status(&state))
}

fn clock_status(state: &AppState) -> ClockStatusResponse {
    ClockStatusResponse {
        now_utc: state.clock.now_utc().to_rfc3339(),
        offset_seconds: state.clock.offset_seconds(),
    }
}
