use tauri::{command, AppHandle, Runtime};

use crate::CameraExt;
use crate::{models::PhotoResponse, Result};

#[command]
pub(crate) async fn take_photo<R: Runtime>(app: AppHandle<R>) -> Result<PhotoResponse> {
    app.camera().take_photo()
}
