import { invoke } from "@tauri-apps/api/core"

export async function takePhoto() {
    return await invoke<string>("plugin:camera|take_photo")
}