use crate::prelude::*;

mod dev;

pub fn clock_router() -> Router<AppState> {
    dev::map_routes_if_in_dev(Router::new())
}
