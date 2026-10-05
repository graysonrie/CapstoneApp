import Tauri
import UIKit

class CameraPlugin: Plugin, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
  private var pendingInvoke: Invoke?

  @objc public func takePhoto(_ invoke: Invoke) {
    let usageDescription =
      Bundle.main.object(forInfoDictionaryKey: "NSCameraUsageDescription") as? String
    if usageDescription == nil || usageDescription?.isEmpty == true {
      invoke.reject(
        "NSCameraUsageDescription is missing from Info.plist",
        code: "CAMERA_PERMISSION_MISSING"
      )
      return
    }

    guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
      invoke.reject("Camera is not available", code: "CAMERA_UNAVAILABLE")
      return
    }

    pendingInvoke = invoke

    DispatchQueue.main.async {
      guard let viewController = self.manager.viewController else {
        self.pendingInvoke = nil
        invoke.reject("No view controller available to present camera", code: "CAMERA_ERROR")
        return
      }

      let picker = UIImagePickerController()
      picker.sourceType = .camera
      picker.delegate = self
      picker.modalPresentationStyle = .fullScreen
      viewController.present(picker, animated: true)
    }
  }

  func imagePickerController(
    _ picker: UIImagePickerController,
    didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]
  ) {
    picker.dismiss(animated: true)
    defer { pendingInvoke = nil }

    guard let image = info[.originalImage] as? UIImage,
      let data = image.jpegData(compressionQuality: 0.9)
    else {
      pendingInvoke?.reject("Unable to save photo", code: "CAMERA_ERROR")
      return
    }

    let url = FileManager.default.temporaryDirectory
      .appendingPathComponent("photo_\(UUID().uuidString).jpg")
    do {
      try data.write(to: url)
      pendingInvoke?.resolve(["path": url.path])
    } catch {
      pendingInvoke?.reject(error.localizedDescription, code: "CAMERA_ERROR")
    }
  }

  func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
    picker.dismiss(animated: true)
    pendingInvoke?.reject("Photo capture was cancelled", code: "CANCELLED")
    pendingInvoke = nil
  }
}

@_cdecl("init_plugin_camera")
func initPlugin() -> Plugin {
  return CameraPlugin()
}
