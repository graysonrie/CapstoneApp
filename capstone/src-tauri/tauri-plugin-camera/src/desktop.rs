use serde::de::DeserializeOwned;
use tauri::{plugin::PluginApi, AppHandle, Runtime};
use tauri_plugin_dialog::DialogExt;

use crate::models::*;

pub fn init<R: Runtime, C: DeserializeOwned>(
  app: &AppHandle<R>,
  _api: PluginApi<R, C>,
) -> crate::Result<Camera<R>> {
  Ok(Camera(app.clone()))
}

/// Access to the camera APIs.
pub struct Camera<R: Runtime>(AppHandle<R>);

impl<R: Runtime> Camera<R> {
  pub fn take_photo(&self) -> crate::Result<String> {
    // No native camera on desktop; let the user pick an image file instead.
    let file = self
      .0
      .dialog()
      .file()
      .add_filter("Images", &["png", "jpg", "jpeg", "webp", "heic"])
      .blocking_pick_file();

    match file {
      Some(path) => Ok(path.to_string()),
      None => Err(
        std::io::Error::new(std::io::ErrorKind::Interrupted, "photo selection was cancelled")
          .into(),
      ),
    }
  }
}
