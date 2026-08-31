use crate::prelude::*;
use crate::services::TestService;

type TestState<'a> = State<'a, Arc<TestService>>;

#[tauri::command]
pub fn emit_event(state: TestState, handle: AppHandle) -> Result<(), String> {
    state.emit_event(&handle);
    Ok(())
}
