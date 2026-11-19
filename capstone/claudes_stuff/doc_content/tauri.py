"""Hand-written descriptions for the Tauri shell (src-tauri/src/) and the camera plugin."""

_FRONTEND_CALL = (
    "The frontend calls this through the generated camelCase binding in "
    "src/generated/commands.ts (which invokes the snake_case command name); argument "
    "names are camelCase in JavaScript."
)

_USER_MESSAGE = (
    "Any tb_client::ClientError is converted with ClientError::user_message, so the "
    "rejected promise carries a user-facing string: the backend's HTTP response body for "
    "non-2xx responses (or \"Something went wrong\" if the body is empty), \"Unable to "
    "reach the server\" for network failures, \"You are not signed in\" when no access "
    "token is held, and \"Something went wrong\" for JSON decode or lock errors."
)

_NO_AUTO_REFRESH = (
    "This command sends the in-memory access token as a Bearer header. It does not "
    "refresh the token itself: if the 15 minute access token has expired the backend "
    "responds 401 and the frontend receives that body as the error string. Only "
    "get_session / is_valid_session perform a refresh."
)

FILES: dict[str, dict] = {
    # ------------------------------------------------------------------
    # Tauri app crate (src-tauri/src)
    # ------------------------------------------------------------------
    "src-tauri/src/main.rs": {
        "summary": (
            "Desktop binary entry point of the Tauri app. It only calls app_lib::run(); all "
            "real setup lives in lib.rs so the same code can be used as the mobile entry point."
        ),
        "details": (
            "The windows_subsystem = \"windows\" attribute is applied in release builds so that "
            "no console window opens on Windows. The library crate is named app_lib in "
            "src-tauri/Cargo.toml (package name \"app\")."
        ),
        "symbols": {
            "main": {
                "description": "Process entry point for desktop builds; delegates to app_lib::run().",
                "notes": (
                    "On iOS and Android this function is not used; the mobile runtime calls "
                    "run() directly because it is marked with tauri::mobile_entry_point."
                ),
            },
        },
    },
    "src-tauri/src/lib.rs": {
        "summary": (
            "Library root of the Tauri app. Declares the commands, constants, prelude and "
            "services modules and defines run(), which builds and starts the Tauri application."
        ),
        "details": (
            "run() is also the mobile entry point (cfg_attr(mobile, tauri::mobile_entry_point)). "
            "Plugins registered: tauri-plugin-ios-webview-insets (iOS only, lets the WKWebView "
            "draw edge to edge so CSS env(safe-area-inset-*) can handle padding), fs, os, "
            "dialog, store and the local camera plugin. Capabilities granted to the main window "
            "are listed in src-tauri/capabilities/default.json (core, store, dialog, os, fs, "
            "camera:default and a few window permissions); remote URLs over http/https are "
            "allowed so the dev server can be loaded on a device."
        ),
        "symbols": {
            "run": {
                "description": (
                    "Builds the Tauri application: registers plugins, runs setup (enables "
                    "tauri-plugin-log at Info level in debug builds and calls "
                    "commands::register_services to create and manage the shared ApiClient), "
                    "installs the command handler from commands::invoke_handler and starts "
                    "the event loop with the generated context from tauri.conf.json."
                ),
                "errors": (
                    "Panics with \"error while running tauri application\" if the app fails "
                    "to start. Errors from adding the log plugin are propagated out of setup, "
                    "which also aborts startup."
                ),
                "notes": (
                    "Logging is only enabled in debug builds, so release builds produce no "
                    "log output from the Rust side. Blocks until the application exits."
                ),
            },
        },
    },
    "src-tauri/src/constants.rs": {
        "summary": (
            "Placeholder module for app-wide constants. It is currently empty; it is "
            "re-exported through the prelude so constants added here are visible everywhere."
        ),
        "symbols": {},
    },
    "src-tauri/src/prelude.rs": {
        "summary": (
            "Common imports re-exported for the app crate: the constants module, serde "
            "Serialize/Deserialize, serde_json json!/Value, std::sync::Arc, std fs/BufWriter/"
            "Path/PathBuf and the Tauri AppHandle, Emitter, Manager and State types."
        ),
        "details": (
            "Most re-exports carry #[allow(unused)] because not every module uses them. "
            "Modules opt in with use crate::prelude::*."
        ),
        "symbols": {},
    },
    "src-tauri/src/commands/mod.rs": {
        "summary": (
            "Groups app start-up wiring: re-exports register_services (creates the managed "
            "state) and invoke_handler (the list of Tauri commands exposed to the frontend)."
        ),
        "symbols": {},
    },
    "src-tauri/src/commands/service_container.rs": {
        "summary": (
            "Creates the shared tb_client::ApiClient used by every command, restores the "
            "saved refresh token from the OS keyring, and registers the client as Tauri "
            "managed state."
        ),
        "symbols": {
            "register_services": {
                "description": (
                    "Builds an Arc<ApiClient> pointed at the backend URL, hydrates it with a "
                    "refresh token loaded from token_store (so the user stays signed in across "
                    "launches), and stores it with AppHandle::manage. Commands then receive it "
                    "as State<Arc<ApiClient>>."
                ),
                "params": {"handle": "The application handle passed from the setup hook."},
                "notes": (
                    "The backend URL comes from the BACKEND_URL environment variable at "
                    "compile time (option_env!), not at run time. Without it, iOS builds use "
                    "the hard-coded LAN address http://192.168.1.54:3001 and every other "
                    "target uses http://127.0.0.1:3001. For the Android emulator set "
                    "BACKEND_URL=http://10.0.2.2:3001; for a physical device use the "
                    "development machine's LAN IP. Only the refresh token is restored at "
                    "startup; no access token exists until get_session refreshes or the user "
                    "logs in. ApiClient::new unwraps the URL parse, so an invalid BACKEND_URL "
                    "panics at startup. A failure to set the refresh token is only logged."
                ),
            },
        },
    },
    "src-tauri/src/commands/tauri_registry.rs": {
        "summary": (
            "Registers all app-level Tauri commands from "
            "services/backend_api_service/tauri_exports.rs with tauri::generate_handler!."
        ),
        "details": (
            "Any new #[tauri::command] must be added to this list or the frontend invoke "
            "fails with a \"command not found\" error. After changing commands, regenerate "
            "the TypeScript bindings with cargo tauri-typegen generate. The camera commands "
            "are not listed here; they belong to the camera plugin and are invoked as "
            "plugin:camera|take_photo and plugin:camera|take_pending_photo."
        ),
        "symbols": {
            "invoke_handler": {
                "description": (
                    "Returns the invoke handler closure for log_in, sign_up, is_valid_session, "
                    "get_session, complete_profile, log_out, ping, request_password_reset, "
                    "confirm_password_reset, scan_plant, get_plant_scan, get_home, get_profile, "
                    "get_user_image_locations, get_plant_geo_distribution, get_recent_finds "
                    "and get_leaderboard."
                ),
                "returns": "A closure suitable for tauri::Builder::invoke_handler.",
            },
        },
    },
    "src-tauri/src/services/mod.rs": {
        "summary": (
            "Declares the app services: backend_api_service (Tauri commands that call the "
            "backend) and token_store (OS keyring persistence of the refresh token)."
        ),
        "symbols": {},
    },
    "src-tauri/src/services/backend_api_service/mod.rs": {
        "summary": "Module wrapper that exposes the tauri_exports module containing the backend Tauri commands.",
        "symbols": {},
    },
    "src-tauri/src/services/token_store.rs": {
        "summary": (
            "Persists the backend refresh token in the operating system credential store "
            "(macOS/iOS Keychain, Windows Credential Manager, Linux Secret Service, via the "
            "keyring crate) so a session survives app restarts."
        ),
        "details": (
            "All functions are best effort: keyring failures are logged with log::warn and "
            "never returned to the caller, so a broken keyring simply means the user has to "
            "log in again on next launch. Only the refresh token is stored; the access token "
            "lives in memory inside ApiClient. Support tip: to force a signed-out state on a "
            "desktop machine, delete the \"plant-app\" / \"refresh_token\" entry from the "
            "system keychain."
        ),
        "symbols": {
            "SERVICE_NAME": "Keyring service name under which the token is stored (\"plant-app\").",
            "REFRESH_TOKEN_ACCOUNT": "Keyring account (user) name for the refresh token entry (\"refresh_token\").",
            "refresh_entry": {
                "description": "Opens the keyring entry identified by SERVICE_NAME and REFRESH_TOKEN_ACCOUNT.",
                "returns": "The keyring Entry handle.",
                "errors": "keyring::Error if the platform credential store cannot be accessed.",
            },
            "save_refresh_token": {
                "description": "Writes the refresh token to the keyring, overwriting any previous value.",
                "params": {"token": "The refresh token string returned by the backend."},
                "notes": "Errors are logged and swallowed.",
            },
            "load_refresh_token": {
                "description": "Reads the stored refresh token from the keyring.",
                "returns": (
                    "Some(token) if a non-empty token is stored; None if there is no entry, "
                    "the entry is empty, or the keyring could not be read."
                ),
                "notes": "Read errors other than NoEntry are logged.",
            },
            "clear_refresh_token": {
                "description": "Deletes the refresh token entry from the keyring.",
                "notes": "A missing entry is treated as success; other errors are logged and swallowed.",
            },
        },
    },
    "src-tauri/src/services/backend_api_service/tauri_exports.rs": {
        "summary": (
            "All app-level Tauri commands. Each command takes the managed Arc<ApiClient>, "
            "calls the Axum backend through the tb_client crate and maps errors to "
            "user-facing strings. This is the only path by which the frontend reaches the "
            "backend."
        ),
        "details": (
            "Session model: tb_client::ApiClient keeps the access token (15 minutes by "
            "default) and the refresh token (15 days by default) in memory. The refresh token "
            "is additionally saved in the OS keyring by token_store on login and after every "
            "refresh, and loaded back at startup and in get_session. Only get_session (and "
            "is_valid_session, which wraps it) refreshes tokens; the data commands simply "
            "fail with the backend's 401 body when the access token has expired, so the "
            "frontend should call getSession when it needs to recover a session. Errors "
            "returned to JavaScript are plain strings produced by ClientError::user_message. "
            "Tauri v2 maps camelCase JavaScript argument names to the snake_case Rust "
            "parameters; some commands also declare rename_all = \"camelCase\" explicitly."
        ),
        "symbols": {
            "BackendApiState": (
                "Type alias for State<'a, Arc<ApiClient>>, the managed tb_client::ApiClient "
                "registered by register_services and injected into every command."
            ),
            "SessionInfo": (
                "Session details returned to the frontend by get_session. Serialized in "
                "camelCase: profileComplete (bool, false until the user finishes the profile "
                "form), firstName (string or null), email and userId (number)."
            ),
            "ScanPlantPayload": (
                "Return value of scan_plant: result is the backend PlantScanResult and "
                "image_data_url is a data: URL (base64) of the photo that was sent, so the "
                "UI can show the image without file-system access. Unlike SessionInfo it is "
                "not renamed, so the JavaScript field is image_data_url in snake_case."
            ),
            "persist_refresh_token": {
                "description": (
                    "Copies the refresh token currently held by the ApiClient into the OS "
                    "keyring. Called after a successful refresh, because the backend rotates "
                    "refresh tokens and the old one becomes invalid."
                ),
                "params": {"api": "The shared API client."},
                "notes": "Does nothing if the client holds no refresh token.",
            },
            "clear_local_session": {
                "description": (
                    "Forgets the session locally: clears the in-memory access and refresh "
                    "tokens and deletes the keyring entry. Does not contact the server."
                ),
                "params": {"api": "The shared API client."},
            },
            "log_in": {
                "description": (
                    "Logs the user in with email and password (POST /auth/login), stores the "
                    "returned access and refresh tokens in the ApiClient and saves the refresh "
                    "token to the keyring. Invoked from JavaScript as "
                    "logIn({ email, password }). " + _FRONTEND_CALL
                ),
                "params": {
                    "api": "Managed ApiClient (injected by Tauri, not passed from JavaScript).",
                    "email": "Account email.",
                    "password": "Account password.",
                },
                "returns": "Nothing (resolves to undefined) on success.",
                "errors": [
                    "Wrong credentials or unverified email: the backend error body, e.g. invalid credentials.",
                    "Rate limited or server error: the backend body.",
                    "Unable to reach the server: backend not running or wrong BACKEND_URL.",
                    _USER_MESSAGE,
                ],
            },
            "sign_up": {
                "description": (
                    "Registers a new account (POST /auth/register/start) and, if the backend "
                    "returns a user_id, immediately logs in with the same credentials by "
                    "calling log_in. Invoked as signUp({ email, password }). " + _FRONTEND_CALL
                ),
                "params": {
                    "api": "Managed ApiClient (injected).",
                    "email": "Email for the new account.",
                    "password": "Password for the new account.",
                },
                "returns": "Nothing on success; the user is logged in afterwards.",
                "errors": [
                    "Backend rejections (email already registered, invalid email or weak password) as the backend body.",
                    "\"user_id does not exist\" if the backend did not return a user_id.",
                    _USER_MESSAGE,
                ],
                "notes": (
                    "Assumes email verification is disabled on the backend "
                    "(require_email_verification: false, the checked-in default). With "
                    "verification enabled the backend returns no user_id and sign-up fails "
                    "with \"user_id does not exist\" even though a pending user was created."
                ),
            },
            "get_session": {
                "description": (
                    "Returns the current session, refreshing tokens if needed. Invoked as "
                    "getSession(). Steps: (1) if the ApiClient has no refresh token in memory, "
                    "load it from the keyring; (2) call GET /auth/session with the access "
                    "token; (3) if that fails (no access token yet, expired token or any other "
                    "error) and a refresh token is available, call POST /auth/refresh, save "
                    "the rotated refresh token to the keyring and retry the session request "
                    "once; (4) if everything fails, clear the local session (memory and "
                    "keyring) and return null. " + _FRONTEND_CALL
                ),
                "params": {"api": "Managed ApiClient (injected)."},
                "returns": "SessionInfo when signed in, or null when not signed in.",
                "errors": (
                    "Never rejects in practice; all failures (including the backend being "
                    "unreachable) result in null after the local session is cleared."
                ),
                "notes": (
                    "Because any failure clears the keyring entry, launching the app while "
                    "the backend is offline signs the user out. Failures are logged with "
                    "log::warn (visible in debug builds). This is the command that restores a "
                    "session on cold start, since register_services only restores the refresh "
                    "token."
                ),
            },
            "try_load_session": {
                "description": (
                    "Calls GET /auth/session with the current access token and converts the "
                    "response into SessionInfo."
                ),
                "params": {"api": "The shared API client."},
                "returns": "SessionInfo for the signed-in user.",
                "errors": (
                    "ClientError::AuthTokenNotSet if no access token is held (no request is "
                    "sent), RequestFailed for 401 or other non-2xx responses, Http for "
                    "network errors."
                ),
            },
            "is_valid_session": {
                "description": (
                    "Returns true if get_session yields a session. Invoked as isValidSession(). "
                    "Has the same refresh and session-clearing side effects as get_session."
                ),
                "params": {"api": "Managed ApiClient (injected)."},
                "returns": "true when signed in, false otherwise.",
            },
            "complete_profile": {
                "description": (
                    "Submits the onboarding profile form (POST /user/profile/complete) so that "
                    "SessionInfo.profileComplete becomes true. Invoked as completeProfile({ "
                    "firstName, lastName, usageIntent }). " + _FRONTEND_CALL
                ),
                "params": {
                    "api": "Managed ApiClient (injected).",
                    "first_name": "User's first name (firstName in JavaScript).",
                    "last_name": "User's last name (lastName in JavaScript).",
                    "usage_intent": "Why the user is using the app (usageIntent in JavaScript).",
                },
                "returns": "Nothing on success.",
                "errors": [
                    "\"You are not signed in\" if no access token is held.",
                    "Validation or 401 errors as the backend body.",
                    _USER_MESSAGE,
                ],
                "notes": _NO_AUTO_REFRESH,
            },
            "log_out": {
                "description": (
                    "Logs out: asks the backend to revoke the refresh token (POST "
                    "/auth/logout) and then always clears the local session (memory and "
                    "keyring). Invoked as logOut()."
                ),
                "params": {"api": "Managed ApiClient (injected)."},
                "returns": "Nothing.",
                "errors": (
                    "Never rejects. A failed server call is only logged, so the user is "
                    "signed out locally even when offline (the refresh token then stays "
                    "valid on the server until it expires)."
                ),
            },
            "ping": {
                "description": (
                    "Health check against GET /ping, useful for checking connectivity to the "
                    "backend. Invoked as ping()."
                ),
                "params": {"api": "Managed ApiClient (injected)."},
                "returns": "Nothing on success.",
                "errors": ["\"Unable to reach the server\" if the backend is not reachable.", _USER_MESSAGE],
            },
            "request_password_reset": {
                "description": (
                    "Starts a password reset for the given email (POST /auth/password/forgot). "
                    "Invoked as requestPasswordReset({ email }). " + _FRONTEND_CALL
                ),
                "params": {"api": "Managed ApiClient (injected).", "email": "Email of the account to reset."},
                "returns": (
                    "The plaintext reset code when the backend runs in Dev mode (so testers "
                    "can complete the flow without email), otherwise null."
                ),
                "errors": _USER_MESSAGE,
                "notes": "Reset codes expire after 15 minutes on the backend.",
            },
            "confirm_password_reset": {
                "description": (
                    "Completes a password reset with the emailed (or dev-returned) code and "
                    "the new password (POST /auth/password/reset). Invoked as "
                    "confirmPasswordReset({ email, code, newPassword }). " + _FRONTEND_CALL
                ),
                "params": {
                    "api": "Managed ApiClient (injected).",
                    "email": "Account email.",
                    "code": "Reset code from request_password_reset.",
                    "new_password": "New password (newPassword in JavaScript).",
                },
                "returns": "Nothing on success. The user still has to log in afterwards.",
                "errors": ["Wrong or expired code as the backend body.", _USER_MESSAGE],
            },
            "mime_and_ext": {
                "description": (
                    "Guesses the MIME type and file extension of an image from its file "
                    "extension (case-insensitive): png, webp and gif are recognised; "
                    "everything else, including heic, is treated as image/jpeg / jpg."
                ),
                "params": {"path": "Path of the image file."},
                "returns": "A (mime, extension) tuple of static strings.",
                "notes": (
                    "HEIC images picked on desktop are therefore labelled image/jpeg; the "
                    "backend decides whether it can handle the actual bytes."
                ),
            },
            "scan_plant": {
                "description": (
                    "Reads the photo at imagePath from disk, uploads it to the backend (POST "
                    "/plant-scan, multipart) for OpenAI identification and XP award, and "
                    "returns the scan result together with a base64 data URL of the image. "
                    "Invoked as scanPlant({ imagePath }) with the path returned by the camera "
                    "plugin. " + _FRONTEND_CALL
                ),
                "params": {
                    "api": "Managed ApiClient (injected).",
                    "image_path": (
                        "Absolute path to the image file (imagePath in JavaScript), as "
                        "returned by plugin:camera|take_photo or take_pending_photo."
                    ),
                },
                "returns": "ScanPlantPayload { result, image_data_url }.",
                "errors": [
                    "\"failed to read image: ...\" if the file cannot be read (this message is not passed through user_message).",
                    "Backend errors such as image too large (10 MiB limit), OpenAI not configured or not signed in, as the backend body.",
                    _USER_MESSAGE,
                ],
                "notes": (
                    "The whole file is read into memory and base64-encoded, so the payload "
                    "returned over IPC is about 4/3 the image size. The file name sent to the "
                    "backend is the path's file name (fallback scan.jpg). GPS EXIF data "
                    "written by the native camera plugin travels inside the image bytes. "
                    "Log lines \"scan_plant: reading ...\" help when debugging device issues. "
                    + _NO_AUTO_REFRESH
                ),
            },
            "get_plant_scan": {
                "description": (
                    "Fetches a single saved scan of the current user (GET /plant-scan/{plant_id}). "
                    "Invoked as getPlantScan({ plantId })."
                ),
                "params": {"api": "Managed ApiClient (injected).", "plant_id": "Scan id (plantId in JavaScript)."},
                "returns": "server_types PlantScan.",
                "errors": ["Not found or not owned by the user as the backend body.", _USER_MESSAGE],
                "notes": _NO_AUTO_REFRESH,
            },
            "get_home": {
                "description": (
                    "Loads the home screen data (GET /home), such as the daily target plants, "
                    "XP and level information. Invoked as getHome()."
                ),
                "params": {"api": "Managed ApiClient (injected)."},
                "returns": "server_types HomeResponse.",
                "errors": _USER_MESSAGE,
                "notes": _NO_AUTO_REFRESH,
            },
            "get_profile": {
                "description": "Loads the current user's profile screen data (GET /user/me). Invoked as getProfile().",
                "params": {"api": "Managed ApiClient (injected)."},
                "returns": "server_types ProfileResponse.",
                "errors": _USER_MESSAGE,
                "notes": _NO_AUTO_REFRESH,
            },
            "get_user_image_locations": {
                "description": (
                    "Lists the GPS locations of the current user's scanned images for the map "
                    "view (GET /plant-image-locations). Invoked as getUserImageLocations()."
                ),
                "params": {"api": "Managed ApiClient (injected)."},
                "returns": "Array of UserPlantImageLocation.",
                "errors": _USER_MESSAGE,
                "notes": _NO_AUTO_REFRESH,
            },
            "get_plant_geo_distribution": {
                "description": (
                    "Returns where a species occurs worldwide, as proxied by the backend from "
                    "GBIF (GET /plant-geo-distribution/{scientific_name}). Invoked as "
                    "getPlantGeoDistribution({ scientificName })."
                ),
                "params": {
                    "api": "Managed ApiClient (injected).",
                    "scientific_name": "Scientific (Latin) plant name (scientificName in JavaScript).",
                },
                "returns": "server_types GbifResponse.",
                "errors": ["GBIF lookup failures as the backend body.", _USER_MESSAGE],
                "notes": _NO_AUTO_REFRESH,
            },
            "get_recent_finds": {
                "description": (
                    "Returns a page of recent plant finds across all users (GET /recent-finds), "
                    "optionally excluding one user. Invoked as getRecentFinds({ count, offset, "
                    "userExclude })."
                ),
                "params": {
                    "api": "Managed ApiClient (injected).",
                    "count": "Maximum number of finds to return.",
                    "offset": "Number of finds to skip (for paging).",
                    "user_exclude": (
                        "Optional user id whose finds are omitted (userExclude in JavaScript; "
                        "the recent finds page passes the current user's id)."
                    ),
                },
                "returns": "Array of RecentFind.",
                "errors": _USER_MESSAGE,
                "notes": _NO_AUTO_REFRESH,
            },
            "get_leaderboard": {
                "description": "Returns the XP leaderboard (GET /leaderboard). Invoked as getLeaderboard().",
                "params": {"api": "Managed ApiClient (injected)."},
                "returns": "Array of LeaderboardUser.",
                "errors": _USER_MESSAGE,
                "notes": _NO_AUTO_REFRESH,
            },
        },
    },
    # ------------------------------------------------------------------
    # Camera plugin (src-tauri/crates/tauri-plugin-camera)
    # ------------------------------------------------------------------
    "src-tauri/crates/tauri-plugin-camera/src/lib.rs": {
        "summary": (
            "Root of the custom Tauri camera plugin. Registers the plugin under the name "
            "\"camera\" with the take_photo and take_pending_photo commands and selects the "
            "desktop or mobile Camera implementation at compile time."
        ),
        "details": (
            "On iOS and Android the commands call native code: android/src/main/java/"
            "CameraPlugin.kt and ios/Sources/ExamplePlugin.swift (the Swift class is "
            "CameraPlugin despite the file name). On desktop the user picks an image file "
            "instead. The frontend invokes the commands as plugin:camera|take_photo and "
            "plugin:camera|take_pending_photo (wrapped in src/lib/camera.ts). Note that "
            "src/generated/commands.ts also contains takePhoto/takePendingPhoto bindings that "
            "invoke take_photo without the plugin: prefix; those do not reach the plugin and "
            "should not be used. Permissions: permissions/default.toml grants allow-take-photo "
            "and allow-take-pending-photo, and capabilities/default.json enables "
            "camera:default. The native side needs NSCameraUsageDescription (and optionally "
            "NSLocationWhenInUseUsageDescription) in the iOS Info.plist, and the Android "
            "manifest declares coarse and fine location permissions and requires a "
            "<package>.fileprovider FileProvider in the host app."
        ),
        "symbols": {
            "CameraExt": (
                "Extension trait that gives any Tauri Manager (App, AppHandle, Window) access "
                "to the plugin's Camera state via .camera()."
            ),
            "CameraExt::camera": {
                "description": "Returns the managed Camera instance for the current platform.",
                "returns": "Reference to the desktop or mobile Camera<R>.",
            },
            "T::camera [crate::CameraExt<R>]": {
                "description": (
                    "Blanket implementation of CameraExt for every Manager<R>; fetches the "
                    "Camera<R> stored in Tauri state by init()."
                ),
                "returns": "Reference to the managed Camera<R>.",
                "notes": "Panics (Tauri state lookup) if the plugin was not initialised with init().",
            },
            "init": {
                "description": (
                    "Builds the camera plugin: registers the two commands and, in setup, "
                    "creates the platform Camera (mobile::init or desktop::init) and stores it "
                    "with app.manage."
                ),
                "returns": "TauriPlugin to pass to tauri::Builder::plugin.",
                "errors": "Setup fails if registering the native Android/iOS plugin fails.",
            },
        },
    },
    "src-tauri/crates/tauri-plugin-camera/src/commands.rs": {
        "summary": (
            "The two Tauri commands exposed by the camera plugin. Both forward to the "
            "platform Camera implementation obtained through CameraExt."
        ),
        "symbols": {
            "take_photo": {
                "description": (
                    "Lets the user take (mobile) or choose (desktop) a photo and returns the "
                    "absolute path of the resulting image file. Invoked from JavaScript as "
                    "invoke(\"plugin:camera|take_photo\"), wrapped by takePhoto() in "
                    "src/lib/camera.ts."
                ),
                "params": {"app": "Application handle (injected by Tauri)."},
                "returns": (
                    "Path string of the image. On iOS it is a JPEG in the temporary directory "
                    "(photo_<uuid>.jpg); on Android a JPEG in the app cache directory; on "
                    "desktop the path of the picked file."
                ),
                "errors": (
                    "Rejects with a string (Error serializes via to_string). Typical messages: "
                    "\"photo selection was cancelled\" (desktop), \"Photo capture was "
                    "cancelled\" (mobile, code CANCELLED), \"Camera is not available\", "
                    "\"NSCameraUsageDescription is missing from Info.plist\", \"Unable to open "
                    "camera\" or \"Unable to save photo\"."
                ),
                "notes": (
                    "On mobile the native code first tries to get a GPS fix (waiting up to 7 "
                    "seconds, or until accuracy is within 100 m) and embeds it in the JPEG "
                    "EXIF so the backend can record where the plant was found. Location "
                    "permission is requested on first use; if it is denied the photo is still "
                    "taken without GPS. If the WebView is reloaded while the camera is open the "
                    "promise is lost; use take_pending_photo after reload."
                ),
            },
            "take_pending_photo": {
                "description": (
                    "Returns, once, the path of the last photo the native camera completed, "
                    "so a photo taken while the WebView was killed or reloaded can be "
                    "recovered. Invoked as invoke(\"plugin:camera|take_pending_photo\"), "
                    "wrapped by takePendingPhoto() in src/lib/camera.ts, which is called on "
                    "app load (ResumePendingScan) and on the plant screenshot page."
                ),
                "params": {"app": "Application handle (injected by Tauri)."},
                "returns": (
                    "The saved path, or null if there is none, the file no longer exists, or "
                    "on desktop (always null)."
                ),
                "errors": "Native plugin invocation errors as strings (mobile only).",
                "notes": (
                    "The native side deletes the saved path when it is read, so only the "
                    "first caller gets it. Note that a successful take_photo also leaves the "
                    "path saved, so a later take_pending_photo returns that same photo once "
                    "unless it was already consumed."
                ),
            },
        },
    },
    "src-tauri/crates/tauri-plugin-camera/src/desktop.rs": {
        "summary": (
            "Desktop (macOS, Windows, Linux) implementation of the camera plugin. There is no "
            "native camera capture on desktop, so take_photo opens a file picker for images."
        ),
        "details": "Uses tauri-plugin-dialog, which is a dependency of this crate only on non-mobile targets.",
        "symbols": {
            "init": {
                "description": "Creates the desktop Camera wrapper around a clone of the AppHandle.",
                "params": {"app": "Application handle.", "_api": "Plugin API (unused on desktop)."},
                "returns": "Ok(Camera).",
            },
            "Camera": "Desktop camera state; wraps an AppHandle used to open dialogs.",
            "Camera::take_photo": {
                "description": (
                    "Opens a blocking native file dialog filtered to png, jpg, jpeg, webp and "
                    "heic files and returns the chosen path."
                ),
                "returns": "Path of the selected file.",
                "errors": (
                    "Error::Io with kind Interrupted and message \"photo selection was "
                    "cancelled\" if the user closes the dialog."
                ),
                "notes": (
                    "No GPS data is added on desktop, so scans from desktop only have a "
                    "location if the chosen file already contains EXIF GPS."
                ),
            },
            "Camera::take_pending_photo": {
                "description": "Desktop has no pending-photo concept; always returns Ok(None).",
                "returns": "Ok(None).",
            },
        },
    },
    "src-tauri/crates/tauri-plugin-camera/src/mobile.rs": {
        "summary": (
            "iOS and Android implementation of the camera plugin. Registers the native plugin "
            "class and forwards take_photo / take_pending_photo to it with "
            "run_mobile_plugin."
        ),
        "details": (
            "Android: CameraPlugin.kt (package com.plugin.camera). takePhoto requests "
            "location permission if needed, gets a location fix (up to 7 seconds; accepts a "
            "cached fix up to 2 minutes old), launches the system camera with "
            "ActivityResultContracts.TakePicture writing to a temp file in the cache "
            "directory, writes GPS EXIF with ExifInterface and resolves { path }. The "
            "in-progress and completed paths are stored in SharedPreferences (camera_plugin) "
            "because the activity can be recreated while the camera app is open. iOS: "
            "ExamplePlugin.swift (class CameraPlugin). takePhoto checks "
            "NSCameraUsageDescription and camera availability, optionally requests "
            "when-in-use location, presents UIImagePickerController, re-encodes the image as "
            "JPEG (quality 0.9) with a GPS dictionary, saves it to the temporary directory and "
            "stores the path in UserDefaults (camera_plugin.completed_path). takePendingPhoto "
            "on both platforms returns and removes that stored path if the file still exists."
        ),
        "symbols": {
            "init": {
                "description": (
                    "Registers the native plugin (Android class com.plugin.camera.CameraPlugin, "
                    "or the Swift init_plugin_camera binding on iOS) and wraps the returned "
                    "PluginHandle in Camera."
                ),
                "params": {"_app": "Application handle (unused).", "api": "Plugin API used to register the native plugin."},
                "returns": "Camera wrapping the native plugin handle.",
                "errors": "Error::PluginInvoke if the native plugin cannot be registered.",
            },
            "Camera": "Mobile camera state; wraps the PluginHandle of the native Kotlin or Swift plugin.",
            "Camera::take_photo": {
                "description": (
                    "Calls the native takePhoto method and returns the path from the "
                    "PhotoResponse."
                ),
                "returns": "Absolute path of the captured JPEG.",
                "errors": (
                    "Error::PluginInvoke when the native side rejects (cancelled, camera "
                    "unavailable, missing Info.plist key, save failure)."
                ),
                "notes": "Blocks the calling (async command) thread until the user finishes with the camera.",
            },
            "Camera::take_pending_photo": {
                "description": (
                    "Calls the native takePendingPhoto method, which returns and clears the "
                    "last completed photo path."
                ),
                "returns": "Some(path) or None.",
                "errors": "Error::PluginInvoke if the native call fails.",
            },
        },
    },
    "src-tauri/crates/tauri-plugin-camera/src/models.rs": {
        "summary": "Response types deserialized from the native mobile plugin (camelCase JSON).",
        "symbols": {
            "PhotoResponse": "Native takePhoto result: { path } with the absolute path of the captured image.",
            "PendingPhotoResponse": (
                "Native takePendingPhoto result: { path } where path is absent when there is "
                "no recoverable photo."
            ),
        },
    },
    "src-tauri/crates/tauri-plugin-camera/src/error.rs": {
        "summary": (
            "Error and Result types of the camera plugin. Errors serialize to their display "
            "string so the frontend receives a plain message when a command rejects."
        ),
        "symbols": {
            "Result": "Alias for std::result::Result<T, camera plugin Error>.",
            "Error": (
                "Camera plugin error. Io wraps std::io::Error (used for desktop cancellation); "
                "PluginInvoke (mobile builds only) wraps errors returned by the native Kotlin "
                "or Swift plugin."
            ),
            "Error::serialize [Serialize]": {
                "description": "Serializes the error as its Display string so it can be returned to JavaScript.",
                "params": {"serializer": "Serde serializer supplied by Tauri."},
                "returns": "The serializer's result.",
            },
        },
    },
}
