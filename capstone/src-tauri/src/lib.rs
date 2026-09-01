use tauri::Manager;

mod prelude;
mod constants;
mod commands;
mod services;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default();

    // Let the WKWebView paint edge-to-edge; CSS env(safe-area-inset-*) handles padding.
    #[cfg(target_os = "ios")]
    let builder = builder.plugin(tauri_plugin_ios_webview_insets::init());

    builder
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }

            commands::register_services(app.handle());

            Ok(())
        })
        .invoke_handler(commands::invoke_handler())
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
