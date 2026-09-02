use crate::services::backend_api_service::tauri_exports::*;

pub fn invoke_handler() -> impl Fn(tauri::ipc::Invoke) -> bool + Send + Sync + 'static {
    tauri::generate_handler![log_in, sign_up, is_valid_session, log_out, ping]
}
