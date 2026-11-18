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
  private let goodFixAccuracy: CLLocationAccuracy = 100

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
      manager.pausesLocationUpdatesAutomatically = false
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
    guard !locationRequestStarted, !cameraPresentationStarted, let manager = locationManager else {
      return
    }
    locationRequestStarted = true

    if let cached = manager.location {
      recordLocation(cached)
    }

    let timeout = DispatchWorkItem { [weak self] in
      guard let self = self, !self.cameraPresentationStarted else { return }
      self.presentCamera()
    }
    locationTimeout = timeout
    DispatchQueue.main.asyncAfter(
      deadline: .now() + locationTimeoutSeconds,
      execute: timeout
    )
    manager.startUpdatingLocation()

    if hasGoodFix() {
      presentCamera()
    }
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
    guard manager === locationManager else { return }
    for location in locations {
      recordLocation(location)
    }
    guard !cameraPresentationStarted, hasGoodFix() else { return }
    presentCamera()
  }

  func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
    guard manager === locationManager, !cameraPresentationStarted else { return }
    if let clError = error as? CLError, clError.code == .locationUnknown {
      return
    }
    NSLog("CameraPlugin: unable to get photo location: %@", error.localizedDescription)
    presentCamera()
  }

  private func presentCamera() {
    guard !cameraPresentationStarted, let invoke = pendingInvoke else { return }
    cameraPresentationStarted = true
    locationTimeout?.cancel()
    locationTimeout = nil

    DispatchQueue.main.async {
      guard let viewController = self.manager.viewController else {
        self.stopLocationUpdates()
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
    if let latest = locationManager?.location {
      recordLocation(latest)
    }
    let location = capturedLocation
    stopLocationUpdates()
    defer {
      pendingInvoke = nil
      capturedLocation = nil
    }

    guard let image = info[.originalImage] as? UIImage,
      let data = jpegData(for: image, location: location)
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

    var properties =
      CGImageSourceCopyPropertiesAtIndex(source, 0, nil) as? [String: Any] ?? [:]
    properties[kCGImagePropertyGPSDictionary as String] = gpsMetadata(for: location)

    let output = NSMutableData()
    guard let destination = CGImageDestinationCreateWithData(output, kUTTypeJPEG, 1, nil) else {
      NSLog("CameraPlugin: unable to create JPEG destination for GPS metadata")
      return jpegData
    }

    CGImageDestinationAddImageFromSource(
      destination,
      source,
      0,
      properties as CFDictionary
    )
    guard CGImageDestinationFinalize(destination) else {
      NSLog("CameraPlugin: unable to write GPS metadata to captured JPEG")
      return jpegData
    }
    return output as Data
  }

  private func gpsMetadata(for location: CLLocation) -> [String: Any] {
    let latitude = location.coordinate.latitude
    let longitude = location.coordinate.longitude
    let timeFormatter = DateFormatter()
    timeFormatter.locale = Locale(identifier: "en_US_POSIX")
    timeFormatter.timeZone = TimeZone(secondsFromGMT: 0)
    timeFormatter.dateFormat = "HH:mm:ss"
    let dateFormatter = DateFormatter()
    dateFormatter.locale = Locale(identifier: "en_US_POSIX")
    dateFormatter.timeZone = TimeZone(secondsFromGMT: 0)
    dateFormatter.dateFormat = "yyyy:MM:dd"

    var gps: [String: Any] = [
      kCGImagePropertyGPSLatitude as String: abs(latitude),
      kCGImagePropertyGPSLatitudeRef as String: latitude < 0 ? "S" : "N",
      kCGImagePropertyGPSLongitude as String: abs(longitude),
      kCGImagePropertyGPSLongitudeRef as String: longitude < 0 ? "W" : "E",
      kCGImagePropertyGPSVersion as String: "2.2.0.0",
      kCGImagePropertyGPSTimeStamp as String: timeFormatter.string(from: location.timestamp),
      kCGImagePropertyGPSDateStamp as String: dateFormatter.string(from: location.timestamp),
    ]
    if location.verticalAccuracy >= 0 {
      gps[kCGImagePropertyGPSAltitude as String] = abs(location.altitude)
      gps[kCGImagePropertyGPSAltitudeRef as String] = location.altitude < 0 ? 1 : 0
    }
    if location.horizontalAccuracy >= 0 {
      gps[kCGImagePropertyGPSHPositioningError as String] = location.horizontalAccuracy
    }
    return gps
  }

  func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
    picker.dismiss(animated: true)
    stopLocationUpdates()
    pendingInvoke?.reject("Photo capture was cancelled", code: "CANCELLED")
    pendingInvoke = nil
    capturedLocation = nil
  }

  private func recordLocation(_ location: CLLocation) {
    let age = Date().timeIntervalSince(location.timestamp)
    guard age >= 0, age <= maximumLocationAge, location.horizontalAccuracy >= 0 else { return }
    guard let current = capturedLocation else {
      capturedLocation = location
      return
    }
    let moreAccurate = location.horizontalAccuracy < current.horizontalAccuracy
    let newerAtSameAccuracy =
      location.horizontalAccuracy == current.horizontalAccuracy
      && location.timestamp > current.timestamp
    if moreAccurate || newerAtSameAccuracy {
      capturedLocation = location
    }
  }

  private func hasGoodFix() -> Bool {
    guard let capturedLocation else { return false }
    return capturedLocation.horizontalAccuracy <= goodFixAccuracy
  }

  private func stopLocationUpdates() {
    locationTimeout?.cancel()
    locationTimeout = nil
    locationManager?.stopUpdatingLocation()
    locationManager?.delegate = nil
    locationManager = nil
  }
}

@_cdecl("init_plugin_camera")
func initPlugin() -> Plugin {
  return CameraPlugin()
}
