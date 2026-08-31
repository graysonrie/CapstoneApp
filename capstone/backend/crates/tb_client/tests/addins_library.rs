mod common;

use std::path::Path;

use addin_server_interactor::ApiClient;
use common::*;
use server_types::addins_management::addins_library::requests::UploadAddinRequest;

const TEST_EXPORT_FILES_DIR: &str =
    "C:\\Users\\GRieger\\Desktop\\rust\\addinmanager2_dev\\TEST_EXPORT_FILES";

fn addin_files_in_dir(dir: impl AsRef<Path>) -> Vec<std::path::PathBuf> {
    std::fs::read_dir(dir)
        .unwrap()
        .filter_map(|entry| entry.ok())
        .map(|entry| entry.path())
        .filter(|path| path.is_file())
        .filter(|path| {
            path.extension()
                .and_then(|ext| ext.to_str())
                .is_some_and(|ext| {
                    let ext = ext.to_ascii_lowercase();
                    ext == "dll"
                })
        })
        .collect()
}

#[tokio::test]
async fn test_upload_addin_to_library() {
    clear_test_local_server().await;
    let client = ApiClient::default();

    reset_db(&client).await.unwrap();

    log_in_as_super_admin(&client).await;

    let project = common::build_sample_csharp_project().await.unwrap();
    let file_paths = project.dll_file_paths;

    let metadata = UploadAddinRequest {
        addin_name: "Tab colorizer".to_string(),
        csharp_project_name: project.csharp_project_name.to_string(),
        for_revit_versions: vec!["All Versions".to_string()],
        reason_for_export: None,
        vendor: "EMA".to_string(),
        vendor_description: "does something".to_string(),
    };

    client
        .addins_library_client()
        .upload_addin_files(&metadata, &file_paths)
        .await
        .unwrap();
}

/// Does not clear the test local server
#[tokio::test]
async fn test_update_addin_in_library() {
    let client = ApiClient::default();

    log_in_as_super_admin(&client).await;

    let dir = Path::new(TEST_EXPORT_FILES_DIR).join("tab_colorizer_export");
    let file_paths = addin_files_in_dir(&dir);
    assert!(
        !file_paths.is_empty(),
        "expected at least one .dll or .addin file in {:?}",
        dir
    );

    let metadata = UploadAddinRequest {
        addin_name: "Tab colorizer".to_string(),
        csharp_project_name: "TabColorizer".to_string(),
        for_revit_versions: vec!["All Versions".to_string()],
        reason_for_export: None,
        vendor: "EMA".to_string(),
        vendor_description: "does something".to_string(),
    };

    client
        .addins_library_client()
        .upload_addin_files(&metadata, &file_paths)
        .await
        .unwrap();
}
