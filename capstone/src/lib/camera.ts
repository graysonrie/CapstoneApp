import { invoke } from "@tauri-apps/api/core";

// TODO: command should live in main crate instead of reaching across plugin boundary
// TODO: remove this file and have tauri-typegen handle it
export async function takePhoto() {
  return await invoke<string>("plugin:camera|take_photo");
}
