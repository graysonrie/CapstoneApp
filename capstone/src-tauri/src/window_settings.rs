use tauri::WebviewWindow;

/// panics if something goes wrong
pub fn set_up_window_vibrancy(window: &WebviewWindow) {
    #[cfg(target_os = "macos")]
    window_vibrancy::apply_vibrancy(
        window,
        window_vibrancy::NSVisualEffectMaterial::HudWindow,
        None,
        None,
    )
    .expect("Unsupported platform! 'apply_vibrancy' is only supported on macOS");

    #[cfg(target_os = "windows")]
    window_vibrancy::apply_mica(window, None)
        .expect("Unsupported platform! 'apply_mica' is only supported on Windows");
}

/// Re-apply system Mica when the OS theme changes while the app is running.
pub fn register_system_mica_listener(main_window: &WebviewWindow) {
    let window = main_window.clone();
    let window_for_theme_changes = window.clone();
    window.on_window_event(move |event| {
        if let tauri::WindowEvent::ThemeChanged(_) = event {
            #[cfg(target_os = "windows")]
            let _ = window_vibrancy::apply_mica(&window_for_theme_changes, None);
        }
    });
}
