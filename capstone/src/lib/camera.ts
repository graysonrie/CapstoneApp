import { invoke } from "@tauri-apps/api/core";
import { useScanStore } from "@/features/plant_scan/store/useScanStore";

// TODO: command should live in main crate instead of reaching across plugin boundary
// TODO: remove this file and have tauri-typegen handle it

let pendingPhotoRecovery: Promise<void> | null = null;

export async function takePhoto() {
  return await invoke<string>("plugin:camera|take_photo");
}

// The native command deletes the saved path, so this can only run once per photo.
// iOS may kill the WebView while the camera is open; callers await this after reload.
export async function takePendingPhoto(): Promise<string | null> {
  if (!pendingPhotoRecovery) {
    pendingPhotoRecovery = Promise.resolve()
      .then(() => invoke<string | null>("plugin:camera|take_pending_photo"))
      .catch(() => null)
      .then((path) => {
        const state = useScanStore.getState();
        if (path && !state.pendingImagePath) {
          state.setPendingScan(state.previousPath || "/home", path);
        }
      });
  }
  // Read the store when the caller resumes. A failed scan clears the path, and
  // a cached string would otherwise send the user back into the analyzing screen.
  return pendingPhotoRecovery.then(
    () => useScanStore.getState().pendingImagePath,
  );
}
