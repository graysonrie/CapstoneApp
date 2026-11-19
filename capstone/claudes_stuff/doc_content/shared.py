"""Hand-written descriptions for the shared crates (backend/crates/server_types and backend/crates/tb_client/src)."""

_CLIENT_ERRORS_AUTHED = [
    "ClientError::AuthTokenNotSet - no access token has been stored on the ApiClient (the user is not logged in).",
    "ClientError::AuthTokenLockPoisoned - the access token lock was poisoned by a panicking thread.",
    "ClientError::RequestFailed - the server answered with a non-2xx status; carries the status code and the plain-text body.",
    "ClientError::JsonDecode - the 2xx body could not be decoded into the expected type.",
    "ClientError::Http - a network or transport error from reqwest (server unreachable, timeout).",
    "ClientError::Url - the endpoint path could not be joined onto the base URL.",
]

_CLIENT_ERRORS_PUBLIC = [
    "ClientError::RequestFailed - the server answered with a non-2xx status; carries the status code and the plain-text body.",
    "ClientError::JsonDecode - the 2xx body could not be decoded into the expected type.",
    "ClientError::Http - a network or transport error from reqwest (server unreachable, timeout).",
    "ClientError::Url - the endpoint path could not be joined onto the base URL.",
]

_CLIENT_ERRORS_EMPTY = [
    "ClientError::RequestFailed - the server answered with a non-2xx status; carries the status code and the plain-text body.",
    "ClientError::Http - a network or transport error from reqwest (server unreachable, timeout).",
    "ClientError::Url - the endpoint path could not be joined onto the base URL.",
]

_SUB_CLIENT_NEW = {
    "description": (
        "Creates the sub-client as a thin borrow of the shared ApiClient. Normally called through the "
        "matching ApiClient accessor rather than directly."
    ),
    "params": {"api": "The ApiClient whose HTTP client, base URL and stored tokens are used."},
    "returns": "A new sub-client that lives as long as the borrow of the ApiClient.",
}

_DEV_FEATURE_NOTE = (
    "Compiled only when the tb_client 'dev' Cargo feature is enabled. The feature is currently in the "
    "crate's default feature set (marked with a TODO to remove), so it is available in normal builds. "
    "The server only maps the route when APP_ENV is not 'production'; against a production server the "
    "request fails with RequestFailed status 404."
)


FILES: dict[str, dict] = {
    # ------------------------------------------------------------------
    # server_types: crate root
    # ------------------------------------------------------------------
    "backend/crates/server_types/src/lib.rs": {
        "summary": (
            "Crate root of server_types, the library of request and response data transfer objects "
            "(DTOs) shared by the Axum backend and the tb_client HTTP client. It declares one module per "
            "backend feature (auth, clock, email_sender, user, plant_scan) plus a prelude."
        ),
        "details": (
            "Because both the server and the client compile against the same structs, the JSON wire "
            "format is defined in exactly one place. All structs derive serde Serialize and Deserialize "
            "with default serde naming, so JSON keys are the Rust field names in snake_case and enum "
            "variants are serialized as their PascalCase variant names (for example \"SuperRare\"). The "
            "only exceptions are the GBIF fields on PlantGeoData. Dependencies: serde, serde_json and "
            "chrono (chrono is declared but not currently used by any type)."
        ),
    },
    "backend/crates/server_types/src/prelude.rs": {
        "summary": (
            "Glob re-export of every request and response module so that consumers can write "
            "use server_types::prelude::* and get all DTOs in scope."
        ),
        "details": (
            "Re-exports auth, clock, email_sender and user requests and responses, and plant_scan "
            "responses. plant_scan::requests is not re-exported because it is empty. RoleType lives in "
            "server_types::user and is not part of the prelude; import it explicitly. The file carries "
            "#![allow(unused_imports)] because some modules (email_sender::requests) are empty."
        ),
    },
    # ------------------------------------------------------------------
    # server_types: auth
    # ------------------------------------------------------------------
    "backend/crates/server_types/src/auth/mod.rs": {
        "summary": "Module declaration for the authentication DTOs; exposes the requests and responses submodules.",
    },
    "backend/crates/server_types/src/auth/requests.rs": {
        "summary": (
            "JSON request bodies for the /auth/* endpoints: login, registration, token refresh and "
            "logout, email verification, and password reset."
        ),
        "details": (
            "All fields are plain strings with snake_case JSON keys. The server trims emails and codes "
            "before use, so leading and trailing whitespace is tolerated."
        ),
        "symbols": {
            "LoginRequest": (
                "Body of POST /auth/login and the dev-only POST /auth/login/bypass. JSON: "
                "{\"email\": string, \"password\": string}. The bypass route ignores the password."
            ),
            "RegisterRequest": (
                "Body of POST /auth/register/start and the dev-only POST /auth/register/start/superadmin. "
                "JSON: {\"email\": string, \"password\": string}. The email must match a basic email "
                "pattern and be at most 320 characters; the password must be at least 8 characters."
            ),
            "VerifyEmailRequest": (
                "Body of POST /auth/email/verify. JSON: {\"email\": string, \"code\": string}, where code "
                "is the verification code that was emailed (or returned in dev mode) after registration."
            ),
            "ResendVerificationEmailRequest": (
                "Body of POST /auth/email/resend. JSON: {\"email\": string}."
            ),
            "RefreshTokenRequest": (
                "Body of POST /auth/refresh and POST /auth/logout. JSON: {\"refresh_token\": string}. "
                "For logout an empty string is accepted and treated as a no-op."
            ),
            "ForgotPasswordRequest": (
                "Body of POST /auth/password/forgot. JSON: {\"email\": string}."
            ),
            "ResetPasswordRequest": (
                "Body of POST /auth/password/reset. JSON: {\"email\": string, \"code\": string, "
                "\"new_password\": string}. code is the 6-digit reset code; new_password must be at "
                "least 8 characters."
            ),
        },
    },
    "backend/crates/server_types/src/auth/responses.rs": {
        "summary": (
            "JSON response bodies for the /auth/* endpoints: registration result, issued token pairs, "
            "current session info and the generic message responses for email verification and "
            "password reset."
        ),
        "details": (
            "Several responses carry optional codes that are only filled in when the server runs in "
            "Dev mode (APP_ENV is not 'production'), so automated tests can complete verification and "
            "reset flows without a real mailbox. In production these fields are always null."
        ),
        "symbols": {
            "RegisterAttemptedResponse": (
                "Returned by POST /auth/register/start and POST /auth/register/start/superadmin. Fields: "
                "user_id (number or null) - the new user's id; it is always present when "
                "auth.require_email_verification is false, and only present in Dev mode when verification "
                "is required. email_verification_code (string or null) - the plaintext verification code, "
                "only populated in Dev mode when email verification is required."
            ),
            "LoginResponse": (
                "Returned by POST /auth/login and POST /auth/login/bypass. Fields: access_token (string, "
                "short-lived JWT sent as a Bearer token), refresh_token (string, long-lived JWT used with "
                "/auth/refresh and /auth/logout), user_id (number), email (string). With the checked-in "
                "settings access tokens live 15 minutes and refresh tokens 15 days."
            ),
            "RefreshTokenResponse": (
                "Returned by POST /auth/refresh. Fields: access_token and refresh_token (both strings). "
                "Refresh tokens rotate: the refresh token that was sent is invalidated and the new one "
                "must be stored."
            ),
            "SessionResponse": (
                "Returned by GET /auth/session. Fields: user_id (number), email (string), "
                "profile_complete (bool, true when first name, last name and usage intent are all set), "
                "first_name (string or null)."
            ),
            "VerifyEmailResponse": (
                "Returned by POST /auth/email/verify on success. Field: message (string, currently "
                "\"Email verified.\")."
            ),
            "ResendVerificationEmailResponse": (
                "Returned by POST /auth/email/resend. Fields: message (string, a generic message that does "
                "not reveal whether the account exists), email_verification_code (string or null, only "
                "populated in Dev mode when a new code was actually generated)."
            ),
            "ForgotPasswordResponse": (
                "Returned by POST /auth/password/forgot. Fields: message (string, generic anti-enumeration "
                "message), password_reset_code (string or null, the 6-digit code; only populated in Dev "
                "mode and only when a matching account exists)."
            ),
            "ResetPasswordResponse": (
                "Returned by POST /auth/password/reset on success. Field: message (string)."
            ),
        },
    },
    # ------------------------------------------------------------------
    # server_types: clock
    # ------------------------------------------------------------------
    "backend/crates/server_types/src/clock/mod.rs": {
        "summary": (
            "Module declaration for the dev clock DTOs used by the /dev/clock routes; exposes the "
            "requests and responses submodules."
        ),
    },
    "backend/crates/server_types/src/clock/requests.rs": {
        "summary": "Request body for advancing the server's simulated clock in Dev mode.",
        "symbols": {
            "AdvanceClockRequest": (
                "Body of POST /dev/clock/advance. JSON: {\"seconds\": integer}. The value is added to the "
                "server clock offset and may be negative. The total offset is limited to about 100 years "
                "in either direction."
            ),
        },
    },
    "backend/crates/server_types/src/clock/responses.rs": {
        "summary": "Response describing the server's current simulated time.",
        "symbols": {
            "ClockStatusResponse": (
                "Returned by GET /dev/clock, POST /dev/clock/advance and POST /dev/clock/reset. Fields: "
                "now_utc (string, the server's current time including the offset, RFC 3339 format), "
                "offset_seconds (integer, the current offset from real time in seconds; 0 after a reset)."
            ),
        },
    },
    # ------------------------------------------------------------------
    # server_types: email_sender
    # ------------------------------------------------------------------
    "backend/crates/server_types/src/email_sender/mod.rs": {
        "summary": (
            "Module declaration for the email sender DTOs; exposes the requests and responses submodules."
        ),
    },
    "backend/crates/server_types/src/email_sender/requests.rs": {
        "summary": (
            "Empty placeholder module for email sender request types. No email sender request structs "
            "exist yet."
        ),
    },
    "backend/crates/server_types/src/email_sender/responses.rs": {
        "summary": "Internal result type produced when the backend creates a pending email verification.",
        "symbols": {
            "PendingEmailVerificationResponse": (
                "Returned internally by the backend's email_server service when it stores a new pending "
                "email verification. Field: plaintext_code (string), the code before hashing, which the "
                "backend emails to the user. It is not sent over HTTP directly; in Dev mode the code is "
                "copied into RegisterAttemptedResponse or ResendVerificationEmailResponse."
            ),
        },
    },
    # ------------------------------------------------------------------
    # server_types: plant_scan
    # ------------------------------------------------------------------
    "backend/crates/server_types/src/plant_scan/mod.rs": {
        "summary": (
            "Module declaration for the plant scanning DTOs; exposes the requests and responses submodules."
        ),
    },
    "backend/crates/server_types/src/plant_scan/requests.rs": {
        "summary": (
            "Intentionally empty. Plant scans are uploaded as multipart/form-data (a single 'image' "
            "file field), so there are no JSON request body structs for this feature."
        ),
    },
    "backend/crates/server_types/src/plant_scan/responses.rs": {
        "summary": (
            "Response types for the plant scanning and game features: the OpenAI identification result "
            "(PlantScan and its parts), the XP outcome of a scan, the home screen with daily quests, the "
            "profile and collection, recent community finds, photo geolocations, GBIF distribution data "
            "and the leaderboard."
        ),
        "details": (
            "PlantScan and its nested types are also the schema the backend asks OpenAI to return, and "
            "the serialized PlantScan is stored verbatim in the user_plant_finds.scan_response column. "
            "Changing these structs therefore affects the model prompt contract and the ability to "
            "deserialize previously stored scans. Image fields named image_base64 or thumbnail_data_url "
            "contain complete data URLs (for example \"data:image/jpeg;base64,...\") that can be used "
            "directly as an img src."
        ),
        "symbols": {
            "PlantScan": (
                "The full plant identification result produced by OpenAI. Returned inside PlantScanResult "
                "by POST /plant-scan and on its own by GET /plant-scan/{plant_id}. Fields: is_plant (bool, "
                "false when the photo does not show a plant; the server rejects such scans with 422), "
                "identification (Identification), summary (string, short general description), sections "
                "(PlantSections, detailed information), identification_notes (IdentificationNotes, the "
                "model's reasoning and uncertainty)."
            ),
            "Identification": (
                "What the plant is. Fields: common_name, scientific_name, family (all string or null), "
                "confidence (Confidence), rarity (Rarity or null; null means the model could not "
                "determine the plant well enough to judge rarity). If both common_name and "
                "scientific_name are missing the server treats the scan as not a plant."
            ),
            "Rarity": (
                "How rare a plant is, as judged by the model. JSON values: \"Common\", \"Uncommon\", "
                "\"Rare\", \"SuperRare\", \"Exotic\". Rarity is stored with each find but does not "
                "currently affect XP. Converted to and from the database RarityType enum."
            ),
            "Confidence": (
                "The model's confidence in its identification. JSON values: \"High\", \"Medium\", \"Low\"."
            ),
            "PlantSections": (
                "Detailed plant information. Fields: appearance (string), native_range (string or null), "
                "care (Care or null), interesting_facts (array of strings, may be empty), toxicity "
                "(Toxicity or null)."
            ),
            "Care": (
                "Plant care guidance. Fields: light, watering, soil, temperature (each string or null)."
            ),
            "Toxicity": (
                "Toxicity notes. Fields: humans (string or null, toxicity towards people), pets (string "
                "or null, toxicity towards domestic animals)."
            ),
            "IdentificationNotes": (
                "Explanation of the identification. Fields: reasoning_summary (string or null, why the "
                "model chose this identification), uncertainty (string or null, look-alikes or facts "
                "that could change the identification)."
            ),
            "DailyMatch": (
                "Present in PlantScanResult when the scan matched one of today's daily quest plants for "
                "the first time today. Fields: key (string, the daily plant key such as \"ficus\", "
                "\"lantanas\" or \"rosemary\"), common_name (string, the quest's display name)."
            ),
            "PlantScanResult": (
                "Returned by POST /plant-scan. Fields: scan (PlantScan), xp_awarded (number; 10 for a "
                "species the user has not found before plus 20 for a daily quest match, so 0, 10, 20 or "
                "30), is_new_species (bool), daily_match (DailyMatch or null), leveled_up (bool, true when "
                "the awarded XP pushed the user to a higher level)."
            ),
            "DailyPlantQuest": (
                "One daily quest on the home screen. Fields: key (string), common_name (string), "
                "scientific_name (string), rarity (Rarity; currently always \"Common\"), xp_reward (number, "
                "currently 20), found (bool, true when the user has scanned this plant today by the "
                "server's UTC date), image_base64 (data URL string or null; a reference photo loaded from "
                "backend/assets/daily_plants/ if one exists)."
            ),
            "HomeResponse": (
                "Returned by GET /home. Fields: first_name (string or null), level (number), rank_title "
                "(string), xp (number, XP earned within the current level), max_xp (number, XP needed to "
                "complete the current level, level times 30), quests (array of DailyPlantQuest; the three "
                "hard-coded MVP plants)."
            ),
            "CollectionPlant": (
                "One find in a user's collection. Fields: id (number, the find id usable with "
                "GET /plant-scan/{plant_id}), common_name (string), scientific_name (string, may be empty), "
                "rarity (Rarity or null), found_on (string, the find date formatted as month and day such "
                "as \"November 19\", with no year), image_base64 (data URL string of the full uploaded "
                "photo, or null if no image is stored or it could not be read)."
            ),
            "RecentFind": (
                "One entry in the community feed returned by GET /recent-finds. Fields: find "
                "(CollectionPlant), first_name and last_name (string or null, the finder's name; null when "
                "the user has not completed their profile)."
            ),
            "ImageGeolocation": (
                "GPS position read from a photo's EXIF data. Fields: latitude and longitude (decimal "
                "degrees as numbers; south and west are negative)."
            ),
            "UserPlantImageLocation": (
                "One of the caller's scan photos for the map view, returned by GET /plant-image-locations. "
                "Fields: image_id (number, the find id), common_name (string), location (ImageGeolocation; "
                "the key is omitted entirely when the photo has no GPS data), thumbnail_data_url (string, "
                "a 320x240 JPEG data URL; omitted when there is no location or the image could not be "
                "decoded)."
            ),
            "ProfileRank": (
                "Rank block of the profile. Fields: level (number), name (string, current rank title), "
                "next_rank (string, rank title of the next level), xp (number, XP within the current "
                "level), xp_to_next (number). Note that xp_to_next is filled with the user's max_xp, i.e. "
                "the total XP required for the current level, not the remaining amount."
            ),
            "ProfileStats": (
                "Statistics block of the profile. Fields: scans (number of finds), unique_species (number "
                "of distinct species keys, based on the normalized scientific name or else the common "
                "name), streak_days (number of consecutive days with at least one find, counted backwards "
                "from today; 0 if the user has not scanned anything today)."
            ),
            "ProfileResponse": (
                "Returned by GET /user/me. Fields: first_name and last_name (string or null), joined_at "
                "(string, account creation time in RFC 3339), rank (ProfileRank), stats (ProfileStats), "
                "found_plants (array of CollectionPlant, newest first)."
            ),
            "GbifResponse": (
                "Subset of the GBIF occurrence search response, returned by "
                "GET /plant-geo-distribution/{scientific_name}. Fields: results (array of PlantGeoData, at "
                "most 300 because the server requests limit=300), count (number, the total number of "
                "matching occurrence records GBIF knows about, which is usually larger than results). "
                "All other GBIF fields are dropped."
            ),
            "PlantGeoData": (
                "One GBIF occurrence record. Fields: species (string), latitude and longitude (number or "
                "null). Unlike every other DTO, the coordinates use GBIF's camelCase key names in JSON in "
                "both directions: \"decimalLatitude\" and \"decimalLongitude\"."
            ),
            "LeaderboardUser": (
                "One row of GET /leaderboard. Fields: id (number), first_name and last_name (strings; "
                "empty strings when the user has not completed their profile), xp (number, XP within the "
                "current level), level (number), rank_title (string)."
            ),
        },
    },
    # ------------------------------------------------------------------
    # server_types: user
    # ------------------------------------------------------------------
    "backend/crates/server_types/src/user/mod.rs": {
        "summary": (
            "Module for user management DTOs. Declares the requests and responses submodules and defines "
            "the RoleType enum shared by requests."
        ),
        "symbols": {
            "RoleType": (
                "User role on the wire. JSON values: \"User\", \"Admin\", \"SuperAdmin\". The backend "
                "converts it into its database Role enum (stored as user, admin, superadmin). Used by "
                "ChangeRoleRequest."
            ),
        },
    },
    "backend/crates/server_types/src/user/requests.rs": {
        "summary": "JSON request bodies for the /user/* endpoints: delete a user, change a role, complete a profile.",
        "symbols": {
            "DeleteUserRequest": (
                "Body of POST /user/delete (super admin only). JSON: {\"email\": string}, the email of the "
                "account to delete."
            ),
            "ChangeRoleRequest": (
                "Body of the dev-only POST /user/change-role/bypass. JSON: {\"email\": string, \"role\": "
                "RoleType}, for example {\"email\": \"a@b.com\", \"role\": \"SuperAdmin\"}."
            ),
            "CompleteProfileRequest": (
                "Body of POST /user/profile/complete. JSON: {\"first_name\": string, \"last_name\": string, "
                "\"usage_intent\": string}. Names must be non-empty after trimming; usage_intent must be "
                "exactly one of \"Just for fun\", \"Learning\", \"Gardening\" or \"Work or school\"."
            ),
        },
    },
    "backend/crates/server_types/src/user/responses.rs": {
        "summary": "JSON response bodies for the /user/* endpoints.",
        "symbols": {
            "UserResponse": (
                "Unused placeholder with a single private username field. No endpoint returns it and its "
                "field cannot be read outside the crate."
            ),
            "ChangeRoleResponse": (
                "Returned by the dev-only POST /user/change-role/bypass. Field: success (bool, always true "
                "on a 200 response). tb_client discards this body."
            ),
            "CompleteProfileResponse": (
                "Returned by POST /user/profile/complete. Field: success (bool, always true on a 200 "
                "response)."
            ),
        },
    },
    # ------------------------------------------------------------------
    # tb_client
    # ------------------------------------------------------------------
    "backend/crates/tb_client/src/lib.rs": {
        "summary": (
            "Crate root of tb_client, the typed async HTTP client for the Leaf Freak backend. Defines "
            "ApiClient, which owns the reqwest client, the server base URL and the in-memory access and "
            "refresh tokens, and hands out per-feature sub-clients (auth, user, plant scan, clock, dev, "
            "misc)."
        ),
        "details": (
            "The Tauri app creates one ApiClient (wrapped in an Arc and stored as Tauri state) and every "
            "Tauri command goes through it; the frontend never talks to the backend directly. The backend "
            "integration tests in backend/src/tests and backend/crates/tb_client/tests use it too. Tokens "
            "are kept only in memory behind RwLocks; persisting the refresh token (the Tauri side uses the "
            "OS keyring) is the caller's job. Re-exports AuthClient, ClockClient, DevClient, "
            "PlantScanClient, UserClient, ClientError and ClientResult. Dependencies: reqwest with rustls "
            "and multipart, serde, serde_json, url, thiserror, tokio and server_types."
        ),
        "symbols": {
            "DEFAULT_SERVER_ENDPOINT": (
                "Base URL used by ApiClient::default: \"http://127.0.0.1:3001\", which matches the backend's "
                "checked-in appsettings.ron host and port."
            ),
            "ApiClient": (
                "Shared client state. Fields: http (public reqwest::Client, reused for connection pooling), "
                "base_url (private Url that endpoint paths are joined onto), auth_token and refresh_token "
                "(private RwLock<Option<String>> holding the current JWTs). All methods take &self, so one "
                "instance can be shared between threads behind an Arc. No default request timeout is set; "
                "only scan_plant sets one."
            ),
            "ApiClient::default [Default]": {
                "description": "Creates an ApiClient pointing at DEFAULT_SERVER_ENDPOINT (http://127.0.0.1:3001).",
                "returns": "A new ApiClient with no tokens stored.",
            },
            "ApiClient::new": {
                "description": (
                    "Creates an ApiClient for the given server base URL with a fresh reqwest client and no "
                    "tokens."
                ),
                "params": {"server_endpoint": "Absolute base URL of the backend, for example \"http://127.0.0.1:3001\"."},
                "returns": "A new ApiClient.",
                "notes": (
                    "Panics (unwrap) if server_endpoint is not a valid absolute URL instead of returning a "
                    "Result. Endpoint paths are joined with Url::join using absolute paths such as "
                    "\"/auth/login\", so any path component in the base URL is replaced, not appended to."
                ),
            },
            "ApiClient::set_auth_token": {
                "description": "Stores the access token that authenticated_request attaches as a Bearer header.",
                "params": {"token": "The access token JWT."},
                "returns": "Ok(()) once stored.",
                "errors": "ClientError::AuthTokenLockPoisoned - the lock was poisoned by a panicking thread.",
                "notes": "Called automatically by AuthClient::login, login_bypass and refresh.",
            },
            "ApiClient::clear_auth_token": {
                "description": "Removes the stored access token so authenticated calls fail with AuthTokenNotSet.",
                "returns": "Ok(()) once cleared.",
                "errors": "ClientError::AuthTokenLockPoisoned - the lock was poisoned.",
            },
            "ApiClient::set_refresh_token": {
                "description": "Stores the refresh token used by AuthClient::refresh and AuthClient::logout.",
                "params": {"token": "The refresh token JWT."},
                "returns": "Ok(()) once stored.",
                "errors": "ClientError::RefreshTokenLockPoisoned - the lock was poisoned.",
                "notes": (
                    "The Tauri app calls this at start-up to hydrate a refresh token loaded from the OS "
                    "keyring."
                ),
            },
            "ApiClient::clear_refresh_token": {
                "description": "Removes the stored refresh token.",
                "returns": "Ok(()) once cleared.",
                "errors": "ClientError::RefreshTokenLockPoisoned - the lock was poisoned.",
            },
            "ApiClient::stored_refresh_token": {
                "description": (
                    "Returns a copy of the stored refresh token. Public so callers can persist it after "
                    "login or refresh, or check whether a session can be restored."
                ),
                "returns": "The refresh token string.",
                "errors": [
                    "ClientError::RefreshTokenNotSet - no refresh token is stored.",
                    "ClientError::RefreshTokenLockPoisoned - the lock was poisoned.",
                ],
            },
            "ApiClient::refresh_token": {
                "description": (
                    "Crate-internal alias of stored_refresh_token used by AuthClient::refresh."
                ),
                "returns": "The refresh token string.",
                "errors": [
                    "ClientError::RefreshTokenNotSet - no refresh token is stored.",
                    "ClientError::RefreshTokenLockPoisoned - the lock was poisoned.",
                ],
            },
            "ApiClient::authenticated_request": {
                "description": (
                    "Crate-internal helper that adds an \"Authorization: Bearer <access token>\" header to a "
                    "request builder. Every endpoint behind the backend's auth middleware goes through it."
                ),
                "params": {"request": "The reqwest RequestBuilder to decorate."},
                "returns": "The same builder with the bearer header attached.",
                "errors": [
                    "ClientError::AuthTokenNotSet - no access token is stored; the request is never sent.",
                    "ClientError::AuthTokenLockPoisoned - the lock was poisoned.",
                ],
                "notes": (
                    "It does not refresh expired tokens. When the access token has expired the server "
                    "answers 401 and the caller sees RequestFailed { status: 401 }; the Tauri layer then "
                    "calls AuthClient::refresh and retries."
                ),
            },
            "ApiClient::misc_client": {
                "description": "Returns a MiscClient for routes that do not belong to a feature (the /ping health check).",
                "returns": "A MiscClient borrowing this ApiClient.",
            },
            "ApiClient::auth_client": {
                "description": "Returns an AuthClient for the /auth/* endpoints.",
                "returns": "An AuthClient borrowing this ApiClient.",
            },
            "ApiClient::user_client": {
                "description": "Returns a UserClient for the /user/* endpoints.",
                "returns": "A UserClient borrowing this ApiClient.",
            },
            "ApiClient::plant_scan_client": {
                "description": (
                    "Returns a PlantScanClient for scanning plants and the game data endpoints (home, "
                    "profile, recent finds, leaderboard, map data)."
                ),
                "returns": "A PlantScanClient borrowing this ApiClient.",
            },
            "ApiClient::clock_client": {
                "description": "Returns a ClockClient for the dev-only /dev/clock endpoints.",
                "returns": "A ClockClient borrowing this ApiClient.",
            },
            "ApiClient::dev_client": {
                "description": "Returns a DevClient for other dev-only endpoints (/dev/erase-db).",
                "returns": "A DevClient borrowing this ApiClient.",
            },
        },
    },
    "backend/crates/tb_client/src/error.rs": {
        "summary": (
            "Error type for every tb_client call (ClientError), the ClientResult alias, and the "
            "user_message mapping that turns an error into text that is safe to show in the UI."
        ),
        "details": (
            "Contains an inline tests module that checks user_message for non-empty and whitespace-only "
            "response bodies."
        ),
        "symbols": {
            "ClientResult": "Shorthand for Result<T, ClientError>; the return type of every fallible tb_client method.",
            "ClientError": (
                "All failures a tb_client call can produce (derives thiserror::Error). Variants: "
                "AuthTokenLockPoisoned and RefreshTokenLockPoisoned (a token RwLock was poisoned); "
                "AuthTokenNotSet (an authenticated call was made before login, the request was not sent); "
                "RefreshTokenNotSet (refresh was called with no refresh token stored); "
                "RequestFailed { status: u16, body: String } (the server answered with a non-2xx status; "
                "body is the server's plain-text error message such as \"invalid credentials\"); "
                "JsonDecode { source, body } (a 2xx body did not match the expected type); "
                "MissingEmailVerificationCode (reserved for callers that expect a dev verification code in "
                "a register response; not produced inside tb_client itself); Http (wraps reqwest::Error, "
                "for example connection refused or timeout); Url (wraps url::ParseError when joining a "
                "path). The Display text of RequestFailed is \"request failed with status {status}: {body}\"."
            ),
            "ClientError::user_message": {
                "description": (
                    "Converts the error into a message suitable for end users. The Tauri commands use it "
                    "to build the String errors returned to the frontend."
                ),
                "returns": (
                    "For RequestFailed, the trimmed server body (or \"Something went wrong\" if the body is "
                    "empty); \"Unable to reach the server\" for Http; \"Invalid server address\" for Url; "
                    "\"You are not signed in\" for AuthTokenNotSet and RefreshTokenNotSet; \"Email "
                    "verification is required\" for MissingEmailVerificationCode; \"Something went wrong\" "
                    "for lock poisoning and JsonDecode."
                ),
                "notes": (
                    "Never exposes reqwest, JSON or lock details. Because server error bodies are passed "
                    "through, the UI text for API failures is controlled by the backend's error mappings. "
                    "Note that the auth middleware returns 401 and 403 with an empty body, which therefore "
                    "show as \"Something went wrong\"."
                ),
            },
        },
    },
    "backend/crates/tb_client/src/util.rs": {
        "summary": (
            "Crate-internal helpers that turn a reqwest response into a ClientResult: one for JSON bodies "
            "and one for endpoints whose body is ignored."
        ),
        "symbols": {
            "parse_json_response": {
                "description": (
                    "Reads the whole response body as text, returns RequestFailed for non-2xx statuses, "
                    "otherwise deserializes the body into T."
                ),
                "params": {"response": "The reqwest response to consume."},
                "returns": "The deserialized value of type T.",
                "errors": [
                    "ClientError::RequestFailed - non-2xx status, with the status code and raw body.",
                    "ClientError::JsonDecode - the body is not valid JSON for T; includes the raw body.",
                    "ClientError::Http - the body could not be read.",
                ],
            },
            "parse_empty_response": {
                "description": (
                    "Reads the whole response body and succeeds for any 2xx status, discarding the body."
                ),
                "params": {"response": "The reqwest response to consume."},
                "returns": "Ok(()) for a 2xx status.",
                "errors": [
                    "ClientError::RequestFailed - non-2xx status, with the status code and raw body.",
                    "ClientError::Http - the body could not be read.",
                ],
                "notes": (
                    "Used for /auth/logout (204), /user/delete, /dev/erase-db and "
                    "/user/change-role/bypass. The last one actually returns a JSON body, which is ignored."
                ),
            },
        },
    },
    "backend/crates/tb_client/src/clients/mod.rs": {
        "summary": (
            "Declares the per-feature sub-client modules and re-exports AuthClient, ClockClient, "
            "DevClient, MiscClient, PlantScanClient and UserClient."
        ),
        "details": (
            "Each sub-client is a zero-cost wrapper around a borrowed ApiClient and is obtained through "
            "the matching ApiClient accessor (for example api.auth_client().login(...))."
        ),
    },
    "backend/crates/tb_client/src/clients/auth_client.rs": {
        "summary": (
            "AuthClient wraps the /auth/* endpoints: registration, login, token refresh and logout, "
            "session lookup, email verification and password reset, plus two dev-only helpers."
        ),
        "details": (
            "login, login_bypass and refresh store the returned tokens on the ApiClient automatically; "
            "logout clears them. Only session sends a Bearer token; all other auth endpoints are public."
        ),
        "symbols": {
            "AuthClient": "Sub-client for the /auth/* endpoints. Holds a borrowed &ApiClient. Obtain it with ApiClient::auth_client.",
            "AuthClient::new": _SUB_CLIENT_NEW,
            "AuthClient::register_start": {
                "description": (
                    "Starts registration of a new account with the User role. Does not log in; the caller "
                    "must call login afterwards (the Tauri sign_up command does exactly that)."
                ),
                "params": {"email": "Email address for the new account.", "password": "Password, at least 8 characters."},
                "returns": "RegisterAttemptedResponse with the user id and, in Dev mode with verification enabled, the verification code.",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "RequestFailed 400 for an invalid email or a password shorter than 8 characters, 409 when the email is taken, 429 when rate limited.",
                ],
                "notes": "Calls POST /auth/register/start with a JSON RegisterRequest. No auth header.",
            },
            "AuthClient::login": {
                "description": "Logs in with email and password and stores the returned access and refresh tokens on the ApiClient.",
                "params": {"email": "Account email.", "password": "Account password."},
                "returns": "LoginResponse with both tokens, the user id and email.",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "RequestFailed 401 \"invalid credentials\" for an unknown email, a wrong password or an unverified email; 429 when rate limited.",
                    "ClientError::AuthTokenLockPoisoned / RefreshTokenLockPoisoned - storing the tokens failed.",
                ],
                "notes": "Calls POST /auth/login with a JSON LoginRequest. No auth header. Used by the Tauri log_in and sign_up commands.",
            },
            "AuthClient::refresh": {
                "description": (
                    "Exchanges the stored refresh token for a new access and refresh token pair and stores "
                    "both on the ApiClient."
                ),
                "returns": "RefreshTokenResponse with the new tokens.",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "ClientError::RefreshTokenNotSet - no refresh token is stored; nothing is sent.",
                    "RequestFailed 401 \"invalid or expired refresh token\" when the token is expired, malformed, an access token, or already rotated; 429 when rate limited.",
                ],
                "notes": (
                    "Calls POST /auth/refresh with a JSON RefreshTokenRequest. No auth header. Refresh "
                    "tokens rotate, so after success the previous refresh token is no longer valid and the "
                    "caller should persist the new one (the Tauri layer writes it to the keyring)."
                ),
            },
            "AuthClient::refresh_with_token": {
                "description": (
                    "Same request as refresh but with an explicitly supplied refresh token, and the returned "
                    "tokens are not stored on the ApiClient. Mainly useful in tests, for example to check "
                    "that an old refresh token is rejected after rotation."
                ),
                "params": {"refresh_token": "The refresh token to send."},
                "returns": "RefreshTokenResponse with the new tokens (not stored).",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "RequestFailed 401 \"invalid or expired refresh token\"; 429 when rate limited.",
                ],
                "notes": "Calls POST /auth/refresh. No auth header.",
            },
            "AuthClient::session": {
                "description": "Fetches information about the currently logged-in user; also serves as a check that the access token is still valid.",
                "returns": "SessionResponse with user id, email, profile_complete flag and first name.",
                "errors": _CLIENT_ERRORS_AUTHED + [
                    "RequestFailed 401 (empty body) when the access token is missing, invalid or expired, the user no longer exists, or the email is unverified while verification is required.",
                ],
                "notes": "Calls GET /auth/session with the Bearer access token. Used by the Tauri get_session and is_valid_session commands.",
            },
            "AuthClient::logout": {
                "description": (
                    "Revokes the stored refresh token on the server and then clears both tokens from the "
                    "ApiClient."
                ),
                "returns": "Ok(()) after the server answered with a 2xx status.",
                "errors": _CLIENT_ERRORS_EMPTY + [
                    "RequestFailed 500 only on a server database error; invalid or missing tokens still succeed.",
                ],
                "notes": (
                    "Calls POST /auth/logout with a JSON RefreshTokenRequest. If no refresh token is stored "
                    "an empty string is sent, which the server accepts as a no-op (204). Local tokens are "
                    "only cleared when the request succeeds, so a network failure leaves them in place. "
                    "Access tokens already issued remain valid until they expire."
                ),
            },
            "AuthClient::verify_email": {
                "description": "Confirms an account's email address with the code sent after registration.",
                "params": {"email": "Account email.", "code": "Verification code."},
                "returns": "VerifyEmailResponse with a confirmation message.",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "RequestFailed 400 for an invalid email, an invalid or expired code, or an already verified email; 404 when the server has email verification disabled (route not mapped); 429 when rate limited.",
                ],
                "notes": "Calls POST /auth/email/verify. No auth header.",
            },
            "AuthClient::resend_verification_email": {
                "description": "Asks the server to issue and send a new email verification code.",
                "params": {"email": "Account email."},
                "returns": "ResendVerificationEmailResponse with a generic message and, in Dev mode, the new code.",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "RequestFailed 404 when the server has email verification disabled; 429 when rate limited; 500 when sending fails.",
                ],
                "notes": "Calls POST /auth/email/resend. No auth header. Succeeds with the same message whether or not the account exists.",
            },
            "AuthClient::forgot_password": {
                "description": "Starts a password reset by requesting a 6-digit reset code for the email.",
                "params": {"email": "Account email."},
                "returns": "ForgotPasswordResponse with a generic message and, in Dev mode, the reset code.",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "RequestFailed 429 when rate limited; 500 when sending the email or the database fails.",
                ],
                "notes": (
                    "Calls POST /auth/password/forgot. No auth header. Used by the Tauri "
                    "request_password_reset command. The code expires after 15 minutes."
                ),
            },
            "AuthClient::reset_password": {
                "description": "Completes a password reset using the emailed code and sets a new password.",
                "params": {
                    "email": "Account email.",
                    "code": "The 6-digit reset code.",
                    "new_password": "New password, at least 8 characters.",
                },
                "returns": "ResetPasswordResponse with a confirmation message.",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "RequestFailed 400 for an invalid email, a short password, or an invalid or expired code; 429 when rate limited.",
                ],
                "notes": (
                    "Calls POST /auth/password/reset. No auth header. Used by the Tauri "
                    "confirm_password_reset command. On success the server also revokes the user's refresh "
                    "token. Five wrong codes invalidate the reset code."
                ),
            },
            "AuthClient::login_bypass": {
                "description": (
                    "Dev-only login that issues tokens for an existing account without checking the "
                    "password or email verification, and stores them on the ApiClient. Intended for tests "
                    "and local tooling."
                ),
                "params": {"email": "Email of an existing account.", "password": "Sent but ignored by the server."},
                "returns": "LoginResponse with both tokens.",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "RequestFailed 401 \"invalid credentials\" when no account has that email; 404 when the server is in production.",
                ],
                "notes": "Calls POST /auth/login/bypass. No auth header. " + _DEV_FEATURE_NOTE,
            },
            "AuthClient::register_start_as_super_admin": {
                "description": (
                    "Dev-only registration that creates the account with the SuperAdmin role. Otherwise "
                    "behaves like register_start."
                ),
                "params": {"email": "Email address for the new account.", "password": "Password, at least 8 characters."},
                "returns": "RegisterAttemptedResponse.",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "RequestFailed 400 / 409 as for register_start; 404 when the server is in production.",
                ],
                "notes": "Calls POST /auth/register/start/superadmin. No auth header. " + _DEV_FEATURE_NOTE,
            },
        },
    },
    "backend/crates/tb_client/src/clients/clock_client.rs": {
        "summary": (
            "ClockClient wraps the dev-only /dev/clock endpoints that read, advance and reset the "
            "server's simulated clock, so tests can exercise token expiry and day-based logic (daily "
            "quests, streaks) without waiting."
        ),
        "details": (
            "All request methods are compiled only with the 'dev' feature (enabled by default). None of "
            "them send an auth header; the server does not require one."
        ),
        "symbols": {
            "ClockClient": "Sub-client for the dev clock endpoints. Holds a borrowed &ApiClient. Obtain it with ApiClient::clock_client.",
            "ClockClient::new": _SUB_CLIENT_NEW,
            "ClockClient::get": {
                "description": "Reads the server's current simulated time and offset.",
                "returns": "ClockStatusResponse.",
                "errors": _CLIENT_ERRORS_PUBLIC,
                "notes": "Calls GET /dev/clock. " + _DEV_FEATURE_NOTE,
            },
            "ClockClient::advance": {
                "description": "Moves the server clock forward (or backward with a negative value) by the given number of seconds.",
                "params": {"seconds": "Seconds to add to the server's clock offset; may be negative."},
                "returns": "ClockStatusResponse after the change.",
                "errors": _CLIENT_ERRORS_PUBLIC + [
                    "RequestFailed 400 when the resulting offset would exceed about 100 years in either direction.",
                ],
                "notes": (
                    "Calls POST /dev/clock/advance with a JSON AdvanceClockRequest. The offset is global "
                    "to the server process, so it affects every user and test running against it until "
                    "reset. " + _DEV_FEATURE_NOTE
                ),
            },
            "ClockClient::reset": {
                "description": "Resets the server clock offset to zero (real time).",
                "returns": "ClockStatusResponse after the reset.",
                "errors": _CLIENT_ERRORS_PUBLIC,
                "notes": "Calls POST /dev/clock/reset. " + _DEV_FEATURE_NOTE,
            },
        },
    },
    "backend/crates/tb_client/src/clients/dev_client.rs": {
        "summary": "DevClient wraps miscellaneous dev-only endpoints; currently only the database wipe used by tests.",
        "symbols": {
            "DevClient": "Sub-client for dev-only maintenance endpoints. Holds a borrowed &ApiClient. Obtain it with ApiClient::dev_client.",
            "DevClient::new": _SUB_CLIENT_NEW,
            "DevClient::erase_db": {
                "description": (
                    "Deletes all rows from the users, plant finds, email verification and password reset "
                    "tables on the server. Used by integration tests to start from a clean database."
                ),
                "returns": "Ok(()) on success.",
                "errors": _CLIENT_ERRORS_EMPTY + [
                    "RequestFailed 500 when the database operation fails; 404 when the server is in production.",
                ],
                "notes": (
                    "Calls POST /dev/erase-db with no body and no auth header. Unlike the other dev "
                    "methods it is not gated behind the 'dev' Cargo feature, but the server only maps the "
                    "route when APP_ENV is not 'production'. Uploaded image files are not deleted."
                ),
            },
        },
    },
    "backend/crates/tb_client/src/clients/misc_client.rs": {
        "summary": "MiscClient wraps routes that do not belong to a feature; currently the /ping health check.",
        "symbols": {
            "MiscClient": "Sub-client for feature-less routes such as the health check. Holds a borrowed &ApiClient. Obtain it with ApiClient::misc_client.",
            "MiscClient::new": _SUB_CLIENT_NEW,
            "MiscClient::ping": {
                "description": "Checks whether the backend can be reached.",
                "returns": "Ok(()) if any HTTP response was received.",
                "errors": [
                    "ClientError::Http - the server could not be reached (connection refused, DNS failure, timeout).",
                    "ClientError::Url - the path could not be joined onto the base URL.",
                ],
                "notes": (
                    "Calls GET /ping with no auth header. The response status is not checked, so a 404 or "
                    "500 from something listening on the port also counts as success. Used by the Tauri "
                    "ping command."
                ),
            },
        },
    },
    "backend/crates/tb_client/src/clients/plant_scan_client.rs": {
        "summary": (
            "PlantScanClient wraps the plant scanning and game data endpoints: uploading a photo for "
            "identification, reading a stored scan, the home screen, the profile, map data, the "
            "community feed, GBIF distribution data and the leaderboard."
        ),
        "details": (
            "Every method sends the stored access token as a Bearer header, so the user must be logged "
            "in. Each method is called by a Tauri command of the same purpose (scan_plant, "
            "get_plant_scan, get_home, get_profile, get_user_image_locations, get_recent_finds, "
            "get_plant_geo_distribution, get_leaderboard)."
        ),
        "symbols": {
            "PlantScanClient": "Sub-client for plant scanning and game data. Holds a borrowed &ApiClient. Obtain it with ApiClient::plant_scan_client.",
            "PlantScanClient::new": _SUB_CLIENT_NEW,
            "PlantScanClient::scan_plant": {
                "description": (
                    "Uploads a photo for identification by OpenAI. The server stores the photo and the "
                    "result as a new find and awards XP."
                ),
                "params": {
                    "image_bytes": "Raw image file bytes. The server rejects images over 10 MiB.",
                    "file_name": "File name sent with the multipart part; the server uses its extension when storing the image.",
                    "mime": "MIME type of the image, for example \"image/jpeg\"; it is forwarded to OpenAI.",
                },
                "returns": "PlantScanResult with the identification, XP awarded, new-species flag, daily quest match and level-up flag.",
                "errors": _CLIENT_ERRORS_AUTHED + [
                    "ClientError::Http also when mime is not a valid MIME string (reqwest rejects it before sending) or when the 120 second timeout elapses.",
                    "RequestFailed 400 for a missing or oversized image, 401 when not authenticated, 422 when no plant was recognized, 502 when OpenAI fails, 503 when the server has no OpenAI API key.",
                ],
                "notes": (
                    "Calls POST /plant-scan as multipart/form-data with a single file field named 'image'. "
                    "This is the only tb_client request with an explicit timeout (120 seconds), because the "
                    "OpenAI call can take a long time; the server itself gives OpenAI 90 seconds."
                ),
            },
            "PlantScanClient::find_by_id": {
                "description": "Fetches the stored identification result for one of the caller's finds.",
                "params": {"plant_id": "The find id (CollectionPlant.id or UserPlantImageLocation.image_id)."},
                "returns": "The stored PlantScan.",
                "errors": _CLIENT_ERRORS_AUTHED + [
                    "RequestFailed 404 when the find does not exist or belongs to another user; 401 when not authenticated.",
                ],
                "notes": "Calls GET /plant-scan/{plant_id} with the Bearer token.",
            },
            "PlantScanClient::get_home": {
                "description": "Fetches the home screen data: the user's level and XP and today's three daily quests.",
                "returns": "HomeResponse.",
                "errors": _CLIENT_ERRORS_AUTHED + ["RequestFailed 401 when not authenticated; 500 on server errors."],
                "notes": "Calls GET /home with the Bearer token.",
            },
            "PlantScanClient::get_profile": {
                "description": "Fetches the current user's profile: name, join date, rank, stats and full plant collection.",
                "returns": "ProfileResponse.",
                "errors": _CLIENT_ERRORS_AUTHED + ["RequestFailed 401 when not authenticated; 500 on server errors."],
                "notes": (
                    "Calls GET /user/me with the Bearer token. Although it lives on PlantScanClient, the "
                    "route is registered by the backend's user router (its handler delegates to the "
                    "plant_scan service). The response embeds every collection photo as base64 and can be "
                    "large for users with many finds."
                ),
            },
            "PlantScanClient::get_user_image_locations": {
                "description": "Fetches the caller's scan photos with their EXIF GPS position and a thumbnail, for the map view.",
                "returns": "A list of UserPlantImageLocation; entries without GPS data have no location or thumbnail.",
                "errors": _CLIENT_ERRORS_AUTHED + ["RequestFailed 401 when not authenticated; 500 on storage or database errors."],
                "notes": "Calls GET /plant-image-locations with the Bearer token.",
            },
            "PlantScanClient::get_recent_finds": {
                "description": "Fetches a page of the most recent finds across all users (the community feed).",
                "params": {
                    "count": "Maximum number of finds to return (SQL LIMIT).",
                    "offset": "Number of finds to skip, for paging.",
                    "user_exclude": "Optional user id whose finds are left out, typically the caller's own id.",
                },
                "returns": "A list of RecentFind ordered by find date and then id, newest first.",
                "errors": _CLIENT_ERRORS_AUTHED + ["RequestFailed 401 when not authenticated; 500 on server errors."],
                "notes": (
                    "Calls GET /recent-finds?count=..&offset=..[&user_exclude=..] with the Bearer token. "
                    "The user_exclude query parameter is omitted when None. Each entry embeds the full "
                    "photo as base64, so keep count small."
                ),
            },
            "PlantScanClient::get_plant_geo_distribution": {
                "description": "Fetches up to 300 GBIF occurrence records with coordinates for a species, to show where it grows.",
                "params": {"scientific_name": "Scientific name of the species, for example \"Lantana camara\"."},
                "returns": "GbifResponse with occurrence coordinates and the total record count.",
                "errors": _CLIENT_ERRORS_AUTHED + [
                    "RequestFailed 502 \"failed to analyze the plant\" when the GBIF request fails (the server reports GBIF failures through its OpenAI error variant); 401 when not authenticated.",
                ],
                "notes": (
                    "Calls GET /plant-geo-distribution/{scientific_name} with the Bearer token. The name is "
                    "inserted into the path with format! and joined with Url::join, which percent-encodes "
                    "spaces; a name containing '/', '?' or '#' would change the URL."
                ),
            },
            "PlantScanClient::get_leaderboard": {
                "description": "Fetches every user ordered by XP, highest first.",
                "returns": "A list of LeaderboardUser.",
                "errors": _CLIENT_ERRORS_AUTHED + ["RequestFailed 401 when not authenticated; 500 on server errors."],
                "notes": "Calls GET /leaderboard with the Bearer token. The list is not paged or limited.",
            },
        },
    },
    "backend/crates/tb_client/src/clients/user_client.rs": {
        "summary": (
            "UserClient wraps the /user/* endpoints: deleting an account (super admin), completing the "
            "caller's profile, and the dev-only role change used by tests."
        ),
        "details": "The user's own profile (GET /user/me) is fetched through PlantScanClient::get_profile instead.",
        "symbols": {
            "UserClient": "Sub-client for the /user/* endpoints. Holds a borrowed &ApiClient. Obtain it with ApiClient::user_client.",
            "UserClient::new": _SUB_CLIENT_NEW,
            "UserClient::delete_user": {
                "description": "Deletes the account with the given email. The caller must be logged in as a super admin.",
                "params": {"email": "Email of the account to delete."},
                "returns": "Ok(()) on success.",
                "errors": _CLIENT_ERRORS_EMPTY + [
                    "ClientError::AuthTokenNotSet / AuthTokenLockPoisoned - no usable access token.",
                    "RequestFailed 401 when not authenticated or the caller's email is unverified, 403 when the caller is not a super admin, 404 when no account has that email.",
                ],
                "notes": "Calls POST /user/delete with the Bearer token and a JSON DeleteUserRequest.",
            },
            "UserClient::complete_profile": {
                "description": "Saves the caller's first name, last name and usage intent, which completes onboarding.",
                "params": {
                    "first_name": "First name; must be non-empty after trimming.",
                    "last_name": "Last name; must be non-empty after trimming.",
                    "usage_intent": "One of \"Just for fun\", \"Learning\", \"Gardening\", \"Work or school\" (exact match).",
                },
                "returns": "CompleteProfileResponse with success set to true.",
                "errors": _CLIENT_ERRORS_AUTHED + [
                    "RequestFailed 400 \"invalid profile data\" for empty names or an unknown usage intent; 401 when not authenticated.",
                ],
                "notes": "Calls POST /user/profile/complete with the Bearer token and a JSON CompleteProfileRequest. Used by the Tauri complete_profile command.",
            },
            "UserClient::change_role_bypass": {
                "description": "Dev-only helper that sets any account's role without authentication. Used by tests to create admins and super admins.",
                "params": {"email": "Email of the account to change.", "role": "The new RoleType."},
                "returns": "Ok(()) on success.",
                "errors": _CLIENT_ERRORS_EMPTY + [
                    "RequestFailed 404 when no account has that email or the server is in production.",
                ],
                "notes": (
                    "Calls POST /user/change-role/bypass with a JSON ChangeRoleRequest and no auth header. "
                    "The server returns a ChangeRoleResponse body that this method ignores. "
                    + _DEV_FEATURE_NOTE
                ),
            },
        },
    },
}
