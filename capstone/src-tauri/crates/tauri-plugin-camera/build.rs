const COMMANDS: &[&str] = &["take_photo", "take_pending_photo"];

fn main() {
  tauri_plugin::Builder::new(COMMANDS)
    .android_path("android")
    .ios_path("ios")
    .build();
}
