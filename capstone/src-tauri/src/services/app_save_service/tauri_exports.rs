use crate::prelude::*;
use crate::services::AppSaveService;

type AppSaveState<'a> = State<'a, Arc<AppSaveService>>;

#[tauri::command]
pub fn copy_file(
    state: AppSaveState,
    source_path: String,
    relative_dest_path: String,
) -> Result<(), String> {
    state
        .copy_file(&source_path, &relative_dest_path)
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn delete_file(state: AppSaveState, relative_path: String) -> Result<(), String> {
    state.delete_file(&relative_path).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn delete_folder(state: AppSaveState, relative_path: String) -> Result<(), String> {
    state
        .delete_folder(&relative_path)
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn ensure_folder_created(state: AppSaveState, relative_path: String) -> Result<(), String> {
    state.ensure_folder_created(&relative_path);
    Ok(())
}

#[tauri::command]
pub fn get_full_path(state: AppSaveState, relative_path: String) -> Result<String, String> {
    Ok(state
        .get_full_path(&relative_path)
        .to_string_lossy()
        .to_string())
}

#[tauri::command]
pub fn get_items_in_folder(
    state: AppSaveState,
    relative_path: String,
) -> Result<Vec<String>, String> {
    state
        .get_items_in_folder(&relative_path)
        .map(|paths| {
            paths
                .into_iter()
                .map(|p| p.to_string_lossy().to_string())
                .collect()
        })
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn get_items_in_folder_names(
    state: AppSaveState,
    relative_path: String,
) -> Result<Vec<String>, String> {
    state
        .get_items_in_folder_names(&relative_path)
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn read_file_string(state: AppSaveState, relative_path: String) -> Result<String, String> {
    state
        .read_file_string(&relative_path)
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn read_json(state: AppSaveState, relative_path: String) -> Result<String, String> {
    state
        .read_json::<Value>(&relative_path)
        .map(|x| x.to_string())
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn rename_folder(state: AppSaveState, from: String, to: String) -> Result<(), String> {
    state.rename_folder(&from, &to).map_err(|e| e.to_string())
}

#[tauri::command]
pub fn save_json(state: AppSaveState, relative_path: String, json: String) -> Result<(), String> {
    state
        .save_json(&relative_path, &json)
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub fn file_exists(state: AppSaveState, relative_path: String) -> bool {
    state.exists(relative_path)
}
