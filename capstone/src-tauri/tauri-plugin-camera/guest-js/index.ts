import { invoke } from '@tauri-apps/api/core'

export async function takePhoto(): Promise<string> {
  const result = await invoke<{path: string}>('plugin:camera|take_photo')
  return result.path
}
