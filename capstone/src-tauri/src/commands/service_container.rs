use tb_client::ApiClient;

use crate::prelude::*;

pub fn register_services(handle: &AppHandle) {
    let handle = handle.clone();

    let server_endpoint = "http://127.0.0.1:3001";
    let backend_api = Arc::new(ApiClient::new(server_endpoint));
    handle.manage(backend_api);
}
