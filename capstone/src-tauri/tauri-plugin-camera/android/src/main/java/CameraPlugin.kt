package com.plugin.camera

import android.app.Activity
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

    private var pendingInvoke: Invoke? = null
    private var photoUri: Uri? = null

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
            pendingInvoke = null

            if (success && photoUri != null) {
                val result = JSObject()
                result.put("path", photoUri.toString())
                invoke?.resolve(result)
            } else {
                invoke?.reject("CANCELLED", "Photo capture was cancelled")
            }

            photoUri = null
        }
    }

    @Command
    fun takePhoto(invoke: Invoke) {
        try {
            val uri = createPhotoUri()

            photoUri = uri
            pendingInvoke = invoke

            cameraLauncher.launch(uri)

        } catch (e: Exception) {
            invoke.reject(
                "CAMERA_ERROR",
                e.message ?: "Unable to open camera"
            )
        }
    }

    private fun createPhotoUri(): Uri {
        val file = java.io.File.createTempFile(
            "photo_",
            ".jpg",
            activity.cacheDir
        )

        return FileProvider.getUriForFile(
            activity,
            "${activity.packageName}.fileprovider",
            file
        )
    }
}
