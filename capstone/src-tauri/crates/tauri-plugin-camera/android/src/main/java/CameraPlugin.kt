package com.plugin.camera

import android.Manifest
import android.app.Activity
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import android.net.Uri
import android.os.Build
import android.os.CancellationSignal
import android.os.Handler
import android.os.Looper
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.app.ActivityCompat
import androidx.core.content.FileProvider
import androidx.exifinterface.media.ExifInterface
import app.tauri.annotation.Command
import app.tauri.annotation.TauriPlugin
import app.tauri.plugin.Invoke
import app.tauri.plugin.JSObject
import app.tauri.plugin.Plugin
import java.io.IOException


@TauriPlugin
class CameraPlugin(private val activity: Activity): Plugin(activity) {

    private companion object {
        const val TAG = "CameraPlugin"
        const val PREFS = "camera_plugin"
        const val KEY_CAPTURING = "capturing_path"
        const val KEY_COMPLETED = "completed_path"
        const val KEY_LATITUDE = "capturing_latitude"
        const val KEY_LONGITUDE = "capturing_longitude"
        const val LOCATION_TIMEOUT_MS = 7_000L
        const val MAX_CACHED_LOCATION_AGE_MS = 120_000L
    }

    // Persisted because the WebView/activity can be recreated while the camera app is open,
    // which drops this instance's fields and the JS promise waiting for the result.
    private val prefs by lazy { activity.getSharedPreferences(PREFS, Context.MODE_PRIVATE) }

    private var pendingInvoke: Invoke? = null
    private var photoFile: java.io.File? = null

    private lateinit var cameraLauncher: ActivityResultLauncher<Uri>
    private lateinit var locationPermissionLauncher: ActivityResultLauncher<Array<String>>

    override fun load(webView: android.webkit.WebView) {
        super.load(webView)

        locationPermissionLauncher = (activity as ComponentActivity).activityResultRegistry.register(
            "camera_location_permission",
            ActivityResultContracts.RequestMultiplePermissions()
        ) { permissions ->
            val invoke = pendingInvoke
            if (permissions.values.any { it }) {
                captureLocationAndLaunchCamera(invoke)
            } else {
                launchCamera(invoke, null)
            }
        }

        // Plugin.load() runs after the activity is already RESUMED, so the
        // LifecycleOwner-bound registerForActivityResult() would throw; register
        // directly against the activity's registry instead, which has no such restriction.
        cameraLauncher = (activity as ComponentActivity).activityResultRegistry.register(
            "camera_take_photo",
            ActivityResultContracts.TakePicture()
        ) { success ->

            val invoke = pendingInvoke
            val path = photoFile?.absolutePath ?: prefs.getString(KEY_CAPTURING, null)
            pendingInvoke = null
            photoFile = null

            val editor = prefs.edit().remove(KEY_CAPTURING)
            if (success && path != null) {
                val latitude = prefs.getString(KEY_LATITUDE, null)?.toDoubleOrNull()
                val longitude = prefs.getString(KEY_LONGITUDE, null)?.toDoubleOrNull()
                if (latitude != null && longitude != null) {
                    try {
                        ExifInterface(path).apply {
                            setLatLong(latitude, longitude)
                            saveAttributes()
                        }
                    } catch (e: IOException) {
                        Log.e(TAG, "Unable to write GPS data to captured photo", e)
                    }
                }

                // Kept until consumed via takePendingPhoto, in case the page that
                // asked for the photo no longer exists.
                editor.putString(KEY_COMPLETED, path)
                val result = JSObject()
                result.put("path", path)
                invoke?.resolve(result)
            } else {
                invoke?.reject("CANCELLED", "Photo capture was cancelled")
            }
            editor.remove(KEY_LATITUDE).remove(KEY_LONGITUDE)
            editor.apply()
        }
    }

    @Command
    fun takePhoto(invoke: Invoke) {
        pendingInvoke = invoke
        if (!hasLocationPermission()) {
            locationPermissionLauncher.launch(
                arrayOf(
                    Manifest.permission.ACCESS_COARSE_LOCATION,
                    Manifest.permission.ACCESS_FINE_LOCATION
                )
            )
            return
        }

        captureLocationAndLaunchCamera(invoke)
    }

    private fun captureLocationAndLaunchCamera(invoke: Invoke?) {
        if (!hasLocationPermission()) {
            launchCamera(invoke, null)
            return
        }
        requestCurrentLocation { location ->
            launchCamera(invoke, location)
        }
    }

    private fun launchCamera(invoke: Invoke?, location: Location?) {
        try {
            val file = createPhotoFile()
            val uri = FileProvider.getUriForFile(
                activity,
                "${activity.packageName}.fileprovider",
                file
            )

            photoFile = file
            pendingInvoke = invoke
            val editor = prefs.edit()
                .putString(KEY_CAPTURING, file.absolutePath)
                .remove(KEY_LATITUDE)
                .remove(KEY_LONGITUDE)
            if (location != null) {
                editor.putString(KEY_LATITUDE, location.latitude.toString())
                    .putString(KEY_LONGITUDE, location.longitude.toString())
            }
            editor.apply()

            cameraLauncher.launch(uri)

        } catch (e: Exception) {
            photoFile = null
            pendingInvoke = null
            prefs.edit()
                .remove(KEY_CAPTURING)
                .remove(KEY_LATITUDE)
                .remove(KEY_LONGITUDE)
                .apply()
            if (invoke != null) {
                invoke.reject(
                    "CAMERA_ERROR",
                    e.message ?: "Unable to open camera"
                )
            } else {
                Log.e(TAG, "Unable to reopen camera after activity recreation", e)
            }
        }
    }

    private fun hasLocationPermission(): Boolean {
        return ActivityCompat.checkSelfPermission(
            activity,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED ||
            ActivityCompat.checkSelfPermission(
                activity,
                Manifest.permission.ACCESS_COARSE_LOCATION
            ) == PackageManager.PERMISSION_GRANTED
    }

    private fun requestCurrentLocation(onResult: (Location?) -> Unit) {
        val locationManager =
            activity.getSystemService(Context.LOCATION_SERVICE) as LocationManager
        val providers = try {
            listOf(
                LocationManager.GPS_PROVIDER,
                LocationManager.NETWORK_PROVIDER
            ).filter { locationManager.isProviderEnabled(it) }
        } catch (e: SecurityException) {
            Log.w(TAG, "Location permission was revoked during photo capture", e)
            onResult(null)
            return
        }

        if (providers.isEmpty()) {
            onResult(null)
            return
        }

        var bestLocation = findRecentLocation(locationManager, providers)
        var finished = false
        var listener: LocationListener? = null
        val cancellationSignals = mutableListOf<CancellationSignal>()
        val handler = Handler(Looper.getMainLooper())

        fun finish(location: Location? = null) {
            if (finished) return
            finished = true
            handler.removeCallbacksAndMessages(null)
            listener?.let { locationManager.removeUpdates(it) }
            cancellationSignals.forEach { it.cancel() }
            onResult(location ?: bestLocation)
        }

        fun recordLocation(location: Location) {
            val currentBest = bestLocation
            if (
                currentBest == null ||
                location.accuracy < currentBest.accuracy ||
                (location.accuracy == currentBest.accuracy && location.time > currentBest.time)
            ) {
                bestLocation = location
            }
            if (location.accuracy <= 100f) {
                finish()
            }
        }

        handler.postDelayed({ finish() }, LOCATION_TIMEOUT_MS)

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                var remainingProviders = providers.size
                providers.forEach { provider ->
                    val cancellationSignal = CancellationSignal()
                    cancellationSignals.add(cancellationSignal)
                    locationManager.getCurrentLocation(
                        provider,
                        cancellationSignal,
                        activity.mainExecutor
                    ) { location ->
                        if (!finished) {
                            if (location != null) {
                                recordLocation(location)
                            }
                            remainingProviders--
                            if (remainingProviders == 0) {
                                finish()
                            }
                        }
                    }
                }
            } else {
                val locationListener = object : LocationListener {
                    override fun onLocationChanged(location: Location) {
                        recordLocation(location)
                        if (!finished) finish()
                    }

                    @Deprecated("Deprecated in Android")
                    override fun onStatusChanged(
                        provider: String?,
                        status: Int,
                        extras: android.os.Bundle?
                    ) = Unit

                    override fun onProviderEnabled(provider: String) = Unit

                    override fun onProviderDisabled(provider: String) = Unit
                }
                listener = locationListener
                providers.forEach { provider ->
                    @Suppress("DEPRECATION")
                    locationManager.requestSingleUpdate(
                        provider,
                        locationListener,
                        Looper.getMainLooper()
                    )
                }
            }
        } catch (e: SecurityException) {
            Log.w(TAG, "Location permission was revoked during photo capture", e)
            finish()
        }
    }

    private fun findRecentLocation(
        locationManager: LocationManager,
        providers: List<String>
    ): Location? {
        return try {
            val now = System.currentTimeMillis()
            providers.mapNotNull { locationManager.getLastKnownLocation(it) }
                .filter { now - it.time in 0..MAX_CACHED_LOCATION_AGE_MS }
                .minByOrNull { it.accuracy }
        } catch (e: SecurityException) {
            Log.w(TAG, "Location permission was revoked during photo capture", e)
            null
        }
    }

    @Command
    fun takePendingPhoto(invoke: Invoke) {
        val path = prefs.getString(KEY_COMPLETED, null)
        prefs.edit().remove(KEY_COMPLETED).apply()

        val result = JSObject()
        if (path != null && java.io.File(path).exists()) {
            result.put("path", path)
        }
        invoke.resolve(result)
    }

    private fun createPhotoFile(): java.io.File {
        return java.io.File.createTempFile(
            "photo_",
            ".jpg",
            activity.cacheDir
        )
    }
}
