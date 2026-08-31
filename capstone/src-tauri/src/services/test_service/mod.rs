pub mod tauri_exports;
use crate::prelude::*;

#[derive(Default)]
pub struct TestService {}

impl TestService {
    pub fn emit_event(&self, handle: &AppHandle) {
        if let Err(e) = handle.emit(
            EVENT_TEST,
            json!({
                "field":"hello"
            }),
        ) {
            eprint!("error:{e}");
        }
    }
}
