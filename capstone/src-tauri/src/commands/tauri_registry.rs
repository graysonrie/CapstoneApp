use crate::services::app_save_service::tauri_exports::*;
use crate::services::test_service::tauri_exports::*;

pub fn invoke_handler() -> impl Fn(tauri::ipc::Invoke) -> bool + Send + Sync + 'static {
    tauri::generate_handler![
        copy_file,
        delete_file,
        delete_folder,
        ensure_folder_created,
        get_full_path,
        get_items_in_folder,
        get_items_in_folder_names,
        read_file_string,
        read_json,
        rename_folder,
        save_json,
        file_exists,
        emit_event,
    ]
}
