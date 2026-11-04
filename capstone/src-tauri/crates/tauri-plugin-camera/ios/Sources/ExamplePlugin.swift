import Tauri
import CoreLocation
import ImageIO
import MobileCoreServices
import UIKit

class CameraPlugin: Plugin, CLLocationManagerDelegate, UIImagePickerControllerDelegate,
  UINavigationControllerDelegate
{
  private var pendingInvoke: Invoke?
  private var locationManager: CLLocationManager?
  private var capturedLocation: CLLocation?
  private var locationTimeout: DispatchWorkItem?
  private var locationRequestStarted = false
  private var cameraPresentationStarted = false
  private let completedPathKey = "camera_plugin.completed_path"
  private let locationTimeoutSeconds = 7.0
  private let maximumLocationAge: TimeInterval = 120

  // Persisted because the WKWebView content process can be terminated while the camera is
  // open; the page reloads and the JS promise waiting for the result is lost.
  @objc public func takePendingPhoto(_ invoke: Invoke) {
    let defaults = UserDefaults.standard
    let path = defaults.string(forKey: completedPathKey)
    defaults.removeObject(forKey: completedPathKey)
    if let path = path, FileManager.default.fileExists(atPath: path) {
      invoke.resolve(["path": path])
    } else {
      invoke.resolve([:])
    }
  }

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
    capturedLocation = nil
    locationRequestStarted = false
    cameraPresentationStarted = false
    requestLocationThenPresentCamera()
  }

  private func requestLocationThenPresentCamera() {
    DispatchQueue.main.async {
      guard self.pendingInvoke != nil else { return }
      let usageDescription =
        Bundle.main.object(forInfoDictionaryKey: "NSLocationWhenInUseUsageDescription") as? String
      guard usageDescription?.isEmpty == false,
        CLLocationManager.locationServicesEnabled()
      else {
        self.presentCamera()
        return
      }

      let manager = CLLocationManager()
      manager.delegate = self
      manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
      self.locationManager = manager

      if #available(iOS 14.0, *) {
        self.handleLocationAuthorization(manager.authorizationStatus)
      } else {
        self.handleLocationAuthorization(CLLocationManager.authorizationStatus())
      }
    }
  }

  private func handleLocationAuthorization(_ status: CLAuthorizationStatus) {
    switch status {
    case .authorizedAlways, .authorizedWhenInUse:
      requestLocationFix()
    case .notDetermined:
      locationManager?.requestWhenInUseAuthorization()
    default:
      presentCamera()
    }
  }

  private func requestLocationFix() {
    guard !locationRequestStarted, !cameraPresentationStarted else { return }
    locationRequestStarted = true

    let timeout = DispatchWorkItem { [weak self] in
      guard let self = self, !self.cameraPresentationStarted else { return }
      self.presentCamera()
    }
    locationTimeout = timeout
    DispatchQueue.main.asyncAfter(
      deadline: .now() + locationTimeoutSeconds,
      execute: timeout
    )
    locationManager?.requestLocation()
  }

  func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
    guard manager === locationManager else { return }
    handleLocationAuthorization(manager.authorizationStatus)
  }

  func locationManager(
    _ manager: CLLocationManager,
    didChangeAuthorization status: CLAuthorizationStatus
  ) {
    guard manager === locationManager else { return }
    handleLocationAuthorization(status)
  }

  func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
    guard manager === locationManager, !cameraPresentationStarted else { return }
    let now = Date()
    capturedLocation = locations
      .filter {
        now.timeIntervalSince($0.timestamp) >= 0 &&
          now.timeIntervalSince($0.timestamp) <= maximumLocationAge &&
          $0.horizontalAccuracy >= 0
      }
      .max { $0.timestamp < $1.timestamp }
    presentCamera()
  }

  func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
    guard manager === locationManager, !cameraPresentationStarted else { return }
    NSLog("CameraPlugin: unable to get photo location: %@", error.localizedDescription)
    presentCamera()
  }

  private func presentCamera() {
    guard !cameraPresentationStarted, let invoke = pendingInvoke else { return }
    cameraPresentationStarted = true
    locationTimeout?.cancel()
    locationTimeout = nil
    locationManager?.delegate = nil
    locationManager = nil

    DispatchQueue.main.async {
      guard let viewController = self.manager.viewController else {
        self.pendingInvoke = nil
        self.capturedLocation = nil
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
    defer {
      pendingInvoke = nil
      capturedLocation = nil
    }

    guard let image = info[.originalImage] as? UIImage,
      let data = jpegData(for: image, location: capturedLocation)
    else {
      pendingInvoke?.reject("Unable to save photo", code: "CAMERA_ERROR")
      return
    }

    let url = FileManager.default.temporaryDirectory
      .appendingPathComponent("photo_\(UUID().uuidString).jpg")
    do {
      try data.write(to: url)
      UserDefaults.standard.set(url.path, forKey: completedPathKey)
      pendingInvoke?.resolve(["path": url.path])
    } catch {
      pendingInvoke?.reject(error.localizedDescription, code: "CAMERA_ERROR")
    }
  }

  private func jpegData(for image: UIImage, location: CLLocation?) -> Data? {
    guard let jpegData = image.jpegData(compressionQuality: 0.9) else { return nil }
    guard let location else { return jpegData }
    guard let source = CGImageSourceCreateWithData(jpegData as CFData, nil) else {
      NSLog("CameraPlugin: unable to read captured JPEG for GPS metadata")
      return jpegData
    }

    let gpsMetadata: [String: Any] = [
      kCGImagePropertyGPSLatitude as String: abs(location.coordinate.latitude),
      kCGImagePropertyGPSLatitudeRef as String: location.coordinate.latitude < 0 ? "S" : "N",
      kCGImagePropertyGPSLongitude as String: abs(location.coordinate.longitude),
      kCGImagePropertyGPSLongitudeRef as String: location.coordinate.longitude < 0 ? "W" : "E",
    ]
    let output = NSMutableData()
    guard let destination = CGImageDestinationCreateWithData(output, kUTTypeJPEG, 1, nil) else {
      NSLog("CameraPlugin: unable to create JPEG destination for GPS metadata")
      return jpegData
    }

    CGImageDestinationAddImageFromSource(
      destination,
      source,
      0,
      [kCGImagePropertyGPSDictionary as String: gpsMetadata] as CFDictionary
    )
    guard CGImageDestinationFinalize(destination) else {
      NSLog("CameraPlugin: unable to write GPS metadata to captured JPEG")
      return jpegData
    }
    return output as Data
  }

  func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
    picker.dismiss(animated: true)
    pendingInvoke?.reject("Photo capture was cancelled", code: "CANCELLED")
    pendingInvoke = nil
    capturedLocation = nil
  }
}

@_cdecl("init_plugin_camera")
func initPlugin() -> Plugin {
  return CameraPlugin()
}
