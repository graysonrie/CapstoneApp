use tauri::{command, AppHandle, Runtime};

use crate::CameraExt;
use crate::Result;

#[command]
pub(crate) async fn take_photo<R: Runtime>(app: AppHandle<R>) -> Result<String> {
    app.camera().take_photo()
}

#[command]
pub(crate) async fn take_pending_photo<R: Runtime>(app: AppHandle<R>) -> Result<Option<String>> {
    app.camera().take_pending_photo()
}
