import Tauri
import UIKit

class CameraPlugin: Plugin, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
  private var pendingInvoke: Invoke?

  @objc public func takePhoto(_ invoke: Invoke) {
    guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
      invoke.reject("CAMERA_UNAVAILABLE", "Camera is not available")
      return
    }

    pendingInvoke = invoke
    let picker = UIImagePickerController()
    picker.sourceType = .camera
    picker.delegate = self
    viewController?.present(picker, animated: true)
  }

  func imagePickerController(_ picker: UIImagePickerController,
                             didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
    picker.dismiss(animated: true)
    defer { pendingInvoke = nil }

    guard let image = info[.originalImage] as? UIImage,
          let data = image.jpegData(compressionQuality: 0.9) else {
      pendingInvoke?.reject("CAMERA_ERROR", "Unable to save photo")
      return
    }

    let url = FileManager.default.temporaryDirectory
      .appendingPathComponent("photo_\(UUID().uuidString).jpg")
    do {
      try data.write(to: url)
      pendingInvoke?.resolve(["path": url.path])
    } catch {
      pendingInvoke?.reject("CAMERA_ERROR", error.localizedDescription)
    }
  }

  func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
    picker.dismiss(animated: true)
    pendingInvoke?.reject("CANCELLED", "Photo capture was cancelled")
    pendingInvoke = nil
  }
}

@_cdecl("init_plugin_camera")
func initPlugin() -> Plugin {
  return CameraPlugin()
}
