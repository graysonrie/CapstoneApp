# Tauri Plugin camera

On Android, `takePhoto` requests foreground location permission and adds GPS
coordinates to the captured JPEG's EXIF metadata when a location is available.
If permission is denied or no location fix is available, the photo is still
captured without location metadata. Geotagged photos contain location data when
shared or uploaded.

On iOS, `takePhoto` requests when-in-use location permission and adds GPS
coordinates to the captured JPEG's EXIF metadata when a location is available.
The host app must provide `NSLocationWhenInUseUsageDescription` in its
`Info.plist`. If permission is denied or no location fix is available, the
photo is still captured without location metadata.
