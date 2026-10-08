use tb_client::ApiClient;

use crate::prelude::*;
use crate::services::token_store;

//
pub fn register_services(handle: &AppHandle) {
    let handle = handle.clone();

    // Set BACKEND_URL at build time (e.g. http://10.0.2.2:3001 for the Android emulator,
    // or your machine's LAN IP for a physical device).
    let server_endpoint = option_env!("BACKEND_URL").unwrap_or(if cfg!(target_os = "ios") {
        "http://192.168.1.54:3001"
    } else {
        "http://127.0.0.1:3001"
    });
    let backend_api = Arc::new(ApiClient::new(server_endpoint));

    // Restore refresh token from OS keyring so the user stays signed in across launches.
    if let Some(token) = token_store::load_refresh_token() {
        if let Err(err) = backend_api.set_refresh_token(token) {
            log::warn!("Failed to hydrate refresh token into ApiClient: {err}");
        }
    }

    handle.manage(backend_api);
}
