package com.plugin.camera

import android.app.Activity
import android.content.Context
import android.net.Uri
import androidx.activity.ComponentActivity
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.FileProvider
import app.tauri.annotation.Command
import app.tauri.annotation.TauriPlugin
import app.tauri.plugin.Invoke
import app.tauri.plugin.JSObject
import app.tauri.plugin.Plugin


@TauriPlugin
class CameraPlugin(private val activity: Activity): Plugin(activity) {

    private companion object {
        const val PREFS = "camera_plugin"
        const val KEY_CAPTURING = "capturing_path"
        const val KEY_COMPLETED = "completed_path"
    }

    // Persisted because the WebView/activity can be recreated while the camera app is open,
    // which drops this instance's fields and the JS promise waiting for the result.
    private val prefs by lazy { activity.getSharedPreferences(PREFS, Context.MODE_PRIVATE) }

    private var pendingInvoke: Invoke? = null
    private var photoFile: java.io.File? = null

    private lateinit var cameraLauncher: ActivityResultLauncher<Uri>

    override fun load(webView: android.webkit.WebView) {
        super.load(webView)

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
                // Kept until consumed via takePendingPhoto, in case the page that
                // asked for the photo no longer exists.
                editor.putString(KEY_COMPLETED, path)
                val result = JSObject()
                result.put("path", path)
                invoke?.resolve(result)
            } else {
                invoke?.reject("CANCELLED", "Photo capture was cancelled")
            }
            editor.apply()
        }
    }

    @Command
    fun takePhoto(invoke: Invoke) {
        try {
            val file = createPhotoFile()
            val uri = FileProvider.getUriForFile(
                activity,
                "${activity.packageName}.fileprovider",
                file
            )

            photoFile = file
            pendingInvoke = invoke
            prefs.edit().putString(KEY_CAPTURING, file.absolutePath).apply()

            cameraLauncher.launch(uri)

        } catch (e: Exception) {
            photoFile = null
            pendingInvoke = null
            invoke.reject(
                "CAMERA_ERROR",
                e.message ?: "Unable to open camera"
            )
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
