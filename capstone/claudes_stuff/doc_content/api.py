"""Hand-written notes for every backend HTTP route, keyed by "METHOD /path"."""

_JSON_REJECTION = (
    " A missing or malformed JSON body is rejected by Axum's Json extractor before the handler runs "
    "(415 without a JSON Content-Type, 400 for invalid JSON, 422 when fields are missing or have the "
    "wrong type), with a plain-text explanation."
)

_AUTH_MIDDLEWARE_ERRORS = (
    "401 with an empty body from the require_auth middleware when the Authorization header is missing "
    "or not 'Bearer <token>', the token is invalid, expired or a refresh token, the user no longer "
    "exists, or (only when auth.require_email_verification is true) the user's email is unverified."
)

_DEV_ACCESS = "Dev only (only mapped when APP_ENV is not 'production'; no authentication)"

_DEV_NOTE = (
    "Mapped only in Dev mode, which is any APP_ENV value other than 'production'. In production the "
    "route does not exist and returns 404. The server refuses to start in Dev mode on a non-loopback "
    "host unless APP_ALLOW_INSECURE_DEV=1 is set, because these routes are unauthenticated."
)

ROUTES: dict[str, dict] = {
    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------
    "GET /ping": {
        "summary": "Health check that lets the client confirm the server is reachable.",
        "request": "No parameters or body.",
        "response": "200 with an empty body.",
        "errors": "None from the handler itself.",
        "notes": (
            "Defined directly in main.rs. Used by the Tauri ping command through MiscClient::ping, which "
            "treats any HTTP response as success."
        ),
    },
    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    "POST /auth/register/start": {
        "summary": (
            "Creates a new account with the User role. If email verification is disabled the account is "
            "marked verified immediately; otherwise a verification code is generated and sent."
        ),
        "access": "Public (rate limited: 10 requests per minute per IP, shared with POST /auth/login)",
        "request": "JSON RegisterRequest {email, password}.",
        "response": (
            "200 JSON RegisterAttemptedResponse {user_id, email_verification_code}. When "
            "auth.require_email_verification is false: user_id is set and email_verification_code is "
            "null. When it is true: both fields are only populated in Dev mode and are null in production."
        ),
        "errors": (
            "400 \"email must be 3–64 chars (letters, digits, underscore)\" when the email fails "
            "validation (the message is outdated; the real check is a basic email pattern with at most "
            "320 characters); 400 \"password must be at least 8 characters\"; 409 \"email already "
            "taken\"; 429 \"too many requests\" when the rate limit is exceeded; 500 \"something happend "
            "trying to send email verification\" when the code cannot be created or sent; 500 \"internal "
            "server error\" for database or hashing failures." + _JSON_REJECTION
        ),
        "notes": (
            "Does not log the user in. The Tauri sign_up command calls AuthClient::register_start and "
            "then AuthClient::login. The server currently uses a mock email sender, so no real email is "
            "delivered. The checked-in appsettings.ron has require_email_verification set to false."
        ),
    },
    "POST /auth/login": {
        "summary": "Verifies email and password and issues a new access and refresh token pair.",
        "access": "Public (rate limited: 10 requests per minute per IP, shared with POST /auth/register/start)",
        "request": "JSON LoginRequest {email, password}. The email is trimmed.",
        "response": "200 JSON LoginResponse {access_token, refresh_token, user_id, email}.",
        "errors": (
            "401 \"invalid credentials\" for an unknown email, a wrong password, or an account whose "
            "email is not verified (deliberately the same message); 429 \"too many requests\"; 500 "
            "\"internal server error\" for database, hashing or token errors." + _JSON_REJECTION
        ),
        "notes": (
            "Side effects: stores a hash of the new refresh token's id on the user (invalidating any "
            "previous refresh token, so only one session per user is active) and updates last_login_at. "
            "Access tokens last 15 minutes and refresh tokens 15 days with the checked-in settings "
            "(auth.access_token_ttl and auth.refresh_token_ttl). Used by the Tauri log_in and sign_up "
            "commands via AuthClient::login, which stores both tokens."
        ),
    },
    "POST /auth/refresh": {
        "summary": "Exchanges a valid refresh token for a new access and refresh token pair (refresh token rotation).",
        "access": "Public (rate limited: 20 requests per minute per IP)",
        "request": "JSON RefreshTokenRequest {refresh_token}.",
        "response": "200 JSON RefreshTokenResponse {access_token, refresh_token}.",
        "errors": (
            "401 \"invalid or expired refresh token\" when the token is empty, malformed, signed with a "
            "different secret, an access token, expired, belongs to a missing user, or is not the user's "
            "current refresh token (for example already rotated or revoked by logout or password "
            "reset); 429 \"too many requests\"; 500 \"internal server error\"." + _JSON_REJECTION
        ),
        "notes": (
            "The submitted refresh token becomes invalid as soon as the new pair is issued. Used by the "
            "Tauri get_session and is_valid_session commands (AuthClient::refresh) when the access token "
            "is missing or rejected."
        ),
    },
    "POST /auth/logout": {
        "summary": "Revokes the given refresh token so it can no longer be used to obtain new tokens.",
        "access": "Public",
        "request": "JSON RefreshTokenRequest {refresh_token}. An empty string is accepted.",
        "response": "204 No Content.",
        "errors": (
            "500 \"internal server error\" on a database or hashing error. Invalid, expired or unknown "
            "tokens are not errors; logout is idempotent and still returns 204." + _JSON_REJECTION
        ),
        "notes": (
            "Although the route sits behind the auth rate-limit middleware, /auth/logout is not in any "
            "rate-limit bucket, so it is effectively not rate limited. Access tokens that were already "
            "issued stay valid until they expire. Used by the Tauri log_out command via "
            "AuthClient::logout, which then clears the client's tokens."
        ),
    },
    "POST /auth/password/forgot": {
        "summary": (
            "Starts a password reset by creating a 6-digit reset code for the account and emailing it. "
            "Always returns the same generic message so that callers cannot tell whether an account exists."
        ),
        "access": "Public (rate limited: 5 requests per minute per IP, shared with POST /auth/password/reset)",
        "request": "JSON ForgotPasswordRequest {email}.",
        "response": (
            "200 JSON ForgotPasswordResponse {message, password_reset_code}. password_reset_code is only "
            "populated in Dev mode and only when the account exists; it is null otherwise."
        ),
        "errors": (
            "429 \"too many requests\"; 500 \"something happened trying to send password reset email\" "
            "when sending fails; 500 \"internal server error\" on database errors. An invalid or unknown "
            "email is not an error." + _JSON_REJECTION
        ),
        "notes": (
            "The code expires after 15 minutes. Any previous reset code for the user is deleted, and "
            "expired codes of all users are purged. Used by the Tauri request_password_reset command."
        ),
    },
    "POST /auth/password/reset": {
        "summary": "Completes a password reset using the emailed code and sets a new password.",
        "access": "Public (rate limited: 5 requests per minute per IP, shared with POST /auth/password/forgot)",
        "request": "JSON ResetPasswordRequest {email, code, new_password}.",
        "response": "200 JSON ResetPasswordResponse {message}.",
        "errors": (
            "400 \"email must be 3–64 chars (letters, digits, underscore)\" for an invalid email; 400 "
            "\"password must be at least 8 characters\"; 400 \"invalid or expired password reset code\" "
            "when the email is unknown, no code exists, the code expired or the code is wrong; 429 "
            "\"too many requests\"; 500 \"internal server error\"." + _JSON_REJECTION
        ),
        "notes": (
            "After 5 wrong codes the reset code is deleted and a new one must be requested. On success "
            "the password and salt are replaced, the reset code is deleted and the user's refresh token "
            "is revoked, ending other sessions at their next refresh. Used by the Tauri "
            "confirm_password_reset command."
        ),
    },
    "POST /auth/email/verify": {
        "summary": "Marks an account's email as verified when the correct verification code is supplied.",
        "access": (
            "Public (rate limited: 5 requests per minute per IP, shared with POST /auth/email/resend). "
            "Only mapped when auth.require_email_verification is true; otherwise 404."
        ),
        "request": "JSON VerifyEmailRequest {email, code}.",
        "response": "200 JSON VerifyEmailResponse {message: \"Email verified.\"}.",
        "errors": (
            "400 \"email must be 3–64 chars (letters, digits, underscore)\" for an invalid email; 400 "
            "\"invalid or expired verification code\" when the email is unknown, no pending code exists, "
            "the code expired or the code is wrong; 400 \"email already verified\"; 429 \"too many "
            "requests\"; 500 \"internal server error\"." + _JSON_REJECTION
        ),
        "notes": "No Tauri command uses this route yet; AuthClient::verify_email is used by tests.",
    },
    "POST /auth/email/resend": {
        "summary": (
            "Issues a new email verification code for an unverified account and sends it. Always returns "
            "the same generic message."
        ),
        "access": (
            "Public (rate limited: 5 requests per minute per IP, shared with POST /auth/email/verify). "
            "Only mapped when auth.require_email_verification is true; otherwise 404."
        ),
        "request": "JSON ResendVerificationEmailRequest {email}.",
        "response": (
            "200 JSON ResendVerificationEmailResponse {message, email_verification_code}. "
            "email_verification_code is only populated in Dev mode and only when a new code was "
            "generated (the account exists and is unverified)."
        ),
        "errors": (
            "429 \"too many requests\"; 500 \"something happend trying to send email verification\" "
            "when sending fails; 500 \"internal server error\" on database errors. Unknown, invalid or "
            "already verified emails are not errors." + _JSON_REJECTION
        ),
        "notes": "No Tauri command uses this route yet; AuthClient::resend_verification_email is used by tests.",
    },
    "GET /auth/session": {
        "summary": "Returns basic information about the user that owns the access token; also used to check that a session is still valid.",
        "request": "No body. Header Authorization: Bearer <access token>.",
        "response": "200 JSON SessionResponse {user_id, email, profile_complete, first_name}.",
        "errors": (
            _AUTH_MIDDLEWARE_ERRORS
            + " The handler also returns 401 (empty body) if the user cannot be loaded."
        ),
        "notes": (
            "profile_complete is true when first name, last name and usage intent are all non-empty; "
            "the frontend uses it to decide whether to show onboarding. Used by the Tauri get_session "
            "and is_valid_session commands via AuthClient::session."
        ),
    },
    "POST /auth/login/bypass": {
        "summary": (
            "Dev-only login that issues tokens for any existing account without checking the password or "
            "email verification."
        ),
        "access": _DEV_ACCESS,
        "request": "JSON LoginRequest {email, password}. The password is ignored.",
        "response": "200 JSON LoginResponse {access_token, refresh_token, user_id, email}.",
        "errors": (
            "401 \"invalid credentials\" when no account has that email; 500 \"internal server error\". "
            "Not rate limited." + _JSON_REJECTION
        ),
        "notes": (
            _DEV_NOTE
            + " Same token side effects as POST /auth/login. Used by tests through AuthClient::login_bypass."
        ),
    },
    "POST /auth/register/start/superadmin": {
        "summary": "Dev-only registration that creates the new account with the SuperAdmin role.",
        "access": _DEV_ACCESS,
        "request": "JSON RegisterRequest {email, password}.",
        "response": "200 JSON RegisterAttemptedResponse {user_id, email_verification_code}, populated as for POST /auth/register/start.",
        "errors": (
            "Same as POST /auth/register/start (400 invalid email or weak password, 409 email taken, "
            "500), except that it is not rate limited." + _JSON_REJECTION
        ),
        "notes": _DEV_NOTE + " Used by tests through AuthClient::register_start_as_super_admin.",
    },
    # ------------------------------------------------------------------
    # Dev clock and database
    # ------------------------------------------------------------------
    "GET /dev/clock": {
        "summary": "Returns the server's current simulated time and the offset from real time.",
        "access": _DEV_ACCESS,
        "request": "No parameters or body.",
        "response": "200 JSON ClockStatusResponse {now_utc (RFC 3339), offset_seconds}.",
        "errors": "None.",
        "notes": _DEV_NOTE + " Used by tests through ClockClient::get.",
    },
    "POST /dev/clock/advance": {
        "summary": (
            "Adds the given number of seconds to the server clock offset, so tests can simulate token "
            "expiry or a new day without waiting."
        ),
        "access": _DEV_ACCESS,
        "request": "JSON AdvanceClockRequest {seconds}; may be negative.",
        "response": "200 JSON ClockStatusResponse with the new time and offset.",
        "errors": (
            "400 with an empty body when the resulting offset would exceed 100 years in either "
            "direction." + _JSON_REJECTION
        ),
        "notes": (
            _DEV_NOTE
            + " The offset is global for the whole server process and affects token expiry, code "
            "expiry, the date used for daily quests and streaks, and stored timestamps. Used by tests "
            "through ClockClient::advance."
        ),
    },
    "POST /dev/clock/reset": {
        "summary": "Resets the server clock offset to zero so the server uses real time again.",
        "access": _DEV_ACCESS,
        "request": "No body.",
        "response": "200 JSON ClockStatusResponse with offset_seconds 0.",
        "errors": "None.",
        "notes": _DEV_NOTE + " Used by tests through ClockClient::reset.",
    },
    "POST /dev/erase-db": {
        "summary": (
            "Deletes all rows from the plant finds, password reset, email verification and users tables. "
            "Used by integration tests to start from a clean database."
        ),
        "access": _DEV_ACCESS,
        "request": "No body.",
        "response": "200 with an empty body.",
        "errors": "500 \"I am error\" when any delete fails (or, defensively, when not in Dev mode).",
        "notes": (
            _DEV_NOTE
            + " Despite the helper's name (erase_and_recreate_all_tables) the tables are not dropped or "
            "recreated; only their rows are deleted. Uploaded scan images in file storage are not "
            "removed. Used by tests through DevClient::erase_db."
        ),
    },
    # ------------------------------------------------------------------
    # Plant scanning and game data
    # ------------------------------------------------------------------
    "POST /plant-scan": {
        "summary": (
            "Uploads a photo, asks OpenAI to identify the plant, stores the photo and the result as a new "
            "find for the caller, and awards XP for new species and daily quest matches."
        ),
        "request": (
            "multipart/form-data with a file field named 'image'. Other fields are ignored; only the "
            "first 'image' field is used. The part's Content-Type is forwarded to OpenAI (defaults to "
            "image/jpeg) and the file name's extension is used for the stored file (defaults to jpg). "
            "Header Authorization: Bearer <access token>."
        ),
        "response": (
            "200 JSON PlantScanResult {scan: PlantScan, xp_awarded, is_new_species, daily_match, "
            "leveled_up}."
        ),
        "errors": (
            "400 \"invalid multipart body\" or \"failed to read image\" when the multipart stream is "
            "malformed or exceeds the 10 MiB body limit; 400 \"image is too large\"; 400 \"image is "
            "required\" when there is no 'image' field or it is empty; "
            + _AUTH_MIDDLEWARE_ERRORS
            + " 422 \"could not identify a plant in that photo\" when the model reports is_plant false "
            "or returns neither a common nor a scientific name; 502 \"failed to analyze the plant\" when "
            "the OpenAI request fails, takes longer than 90 seconds, or returns unparseable JSON; 503 "
            "\"plant scanning is not configured\" when no OpenAI API key is set (openai.api_key in "
            "config or the OPENAI_API_KEY environment variable); 500 \"internal server error\" for "
            "database or file storage failures."
        ),
        "notes": (
            "Upload limit is 10 MiB. The model defaults to gpt-4o (openai.model). XP: 10 when the "
            "species (normalized scientific name, or common name if missing) is new for the user, plus "
            "20 when the plant matches one of the three hard-coded daily plants (Ficus benjamina, "
            "Lantana camara, Salvia rosmarinus) and that daily plant has not already been found today "
            "(server UTC date, affected by the dev clock). Each level needs level x 30 XP. A find is "
            "stored even when 0 XP is awarded; the image is saved as scans/{user_id}/{uuid}.{ext} in "
            "file storage and the full PlantScan JSON is stored with the find. Called by the Tauri "
            "scan_plant command via PlantScanClient::scan_plant, which uses a 120 second client timeout."
        ),
    },
    "GET /plant-scan/{plant_id}": {
        "summary": "Returns the stored identification result for one of the caller's finds.",
        "request": "Path parameter plant_id (integer find id). Header Authorization: Bearer <access token>.",
        "response": "200 JSON PlantScan.",
        "errors": (
            "400 (Axum path rejection) when plant_id is not an integer; "
            + _AUTH_MIDDLEWARE_ERRORS
            + " 404 \"plant scan not found\" when the find does not exist, belongs to another user, or "
            "has no stored scan; 500 \"stored plant scan response is invalid\" when the stored JSON no "
            "longer matches PlantScan; 500 \"internal server error\" on database errors."
        ),
        "notes": (
            "Users can only read their own finds, even though GET /recent-finds exposes other users' find "
            "ids. Called by the Tauri get_plant_scan command via PlantScanClient::find_by_id."
        ),
    },
    "GET /plant-image-locations": {
        "summary": (
            "Lists the caller's scan photos together with the GPS position read from each photo's EXIF "
            "data and a small thumbnail, for the map view."
        ),
        "request": "No parameters. Header Authorization: Bearer <access token>.",
        "response": (
            "200 JSON array of UserPlantImageLocation {image_id, common_name, location?, "
            "thumbnail_data_url?}. Finds whose image file is missing are skipped. location and "
            "thumbnail_data_url are omitted from the JSON when the photo has no usable GPS data; the "
            "thumbnail is a 320x240 JPEG data URL."
        ),
        "errors": (
            _AUTH_MIDDLEWARE_ERRORS
            + " 500 \"internal server error\" on database errors or when an existing image file cannot "
            "be read."
        ),
        "notes": (
            "Only photos that still carry EXIF GPS tags get a location. Called by the Tauri "
            "get_user_image_locations command via "
            "PlantScanClient::get_user_image_locations."
        ),
    },
    "GET /home": {
        "summary": "Returns the home screen data: the caller's level, rank and XP, and today's three daily plant quests.",
        "request": "No parameters. Header Authorization: Bearer <access token>.",
        "response": (
            "200 JSON HomeResponse {first_name, level, rank_title, xp, max_xp, quests: "
            "[DailyPlantQuest {key, common_name, scientific_name, rarity, xp_reward, found, "
            "image_base64}]}."
        ),
        "errors": _AUTH_MIDDLEWARE_ERRORS + " 500 \"internal server error\" on database errors.",
        "notes": (
            "The MVP quests are hard-coded (Ficus Tree, Lantanas, Rosemary) and are the same every day. "
            "rarity is always Common and xp_reward is always 20. found is true when the caller has a "
            "matching find on the server's current UTC date. image_base64 is a reference photo from "
            "backend/assets/daily_plants/{key}.jpg, .jpeg, .png or .webp, or null if none exists. Called "
            "by the Tauri get_home command via PlantScanClient::get_home."
        ),
    },
    "GET /plant-geo-distribution/{scientific_name}": {
        "summary": (
            "Proxies the public GBIF occurrence search to return up to 300 recorded locations of a "
            "species, for showing where it grows."
        ),
        "request": (
            "Path parameter scientific_name (URL-encoded string, for example Lantana%20camara). Header "
            "Authorization: Bearer <access token>."
        ),
        "response": (
            "200 JSON GbifResponse {results: [PlantGeoData {species, decimalLatitude, "
            "decimalLongitude}], count}."
        ),
        "errors": (
            _AUTH_MIDDLEWARE_ERRORS
            + " 502 \"failed to analyze the plant\" when the GBIF request fails, returns a non-2xx "
            "status or unexpected JSON. GBIF failures are reported through the OpenAi error variant, so "
            "server logs show \"openai request failed\" even though OpenAI is not involved."
        ),
        "notes": (
            "Calls https://api.gbif.org/v1/occurrence/search with scientificName, hasCoordinate=true and "
            "limit=300, using a new reqwest client with no explicit timeout. The caller's identity is not "
            "used. count is GBIF's total number of matching records, not the length of results. Called "
            "by the Tauri get_plant_geo_distribution command via "
            "PlantScanClient::get_plant_geo_distribution."
        ),
    },
    "GET /recent-finds": {
        "summary": "Returns a page of the most recent finds from all users, for the community feed.",
        "request": (
            "Query parameters: count (required unsigned integer, page size), offset (required unsigned "
            "integer), user_exclude (optional user id whose finds are left out). Header Authorization: "
            "Bearer <access token>."
        ),
        "response": (
            "200 JSON array of RecentFind {find: CollectionPlant {id, common_name, scientific_name, "
            "rarity, found_on, image_base64}, first_name, last_name}, ordered by find date and then id, "
            "newest first."
        ),
        "errors": (
            "400 (Axum query rejection) when count or offset is missing or not a non-negative integer; "
            + _AUTH_MIDDLEWARE_ERRORS
            + " 500 \"internal server error\" on database errors. Unreadable images are logged and "
            "returned as null rather than failing the request."
        ),
        "notes": (
            "There is no server-side cap on count, and every entry embeds the full-size photo as base64, "
            "so large pages produce large responses. found_on has no year. The Tauri get_recent_finds "
            "command calls it via PlantScanClient::get_recent_finds."
        ),
    },
    "GET /leaderboard": {
        "summary": "Returns every user ordered by XP, highest first.",
        "request": "No parameters. Header Authorization: Bearer <access token>.",
        "response": "200 JSON array of LeaderboardUser {id, first_name, last_name, xp, level, rank_title}.",
        "errors": _AUTH_MIDDLEWARE_ERRORS + " 500 \"internal server error\" on database errors.",
        "notes": (
            "The list is not paged or limited and includes users who have not completed their profile "
            "(their names are empty strings). Ordering is by the xp column, which holds XP within the "
            "current level (it is reduced on each level-up), so a higher-level user can rank below a "
            "lower-level one. Called by the Tauri get_leaderboard command via "
            "PlantScanClient::get_leaderboard."
        ),
    },
    # ------------------------------------------------------------------
    # User
    # ------------------------------------------------------------------
    "GET /user/me": {
        "summary": (
            "Returns the caller's profile: name, join date, rank and XP, statistics (scans, unique "
            "species, daily streak) and the full plant collection."
        ),
        "request": "No parameters. Header Authorization: Bearer <access token>.",
        "response": (
            "200 JSON ProfileResponse {first_name, last_name, joined_at, rank: ProfileRank {level, name, "
            "next_rank, xp, xp_to_next}, stats: ProfileStats {scans, unique_species, streak_days}, "
            "found_plants: [CollectionPlant]}."
        ),
        "errors": (
            _AUTH_MIDDLEWARE_ERRORS
            + " 500 \"internal server error\" on database errors (errors use the plant scan error "
            "mapping). Unreadable images are logged and returned as null."
        ),
        "notes": (
            "Registered by the user router but implemented by the plant_scan service. In tb_client it "
            "is PlantScanClient::get_profile (not on UserClient), used by the Tauri get_profile command. "
            "streak_days is 0 unless the user has a find on the current server date. rank.xp_to_next "
            "holds the total XP needed for the current level (max_xp), not the remaining amount. Every "
            "collection photo is embedded as base64."
        ),
    },
    "POST /user/profile/complete": {
        "summary": "Saves the caller's first name, last name and usage intent, completing onboarding.",
        "request": (
            "JSON CompleteProfileRequest {first_name, last_name, usage_intent}. Header Authorization: "
            "Bearer <access token>."
        ),
        "response": "200 JSON CompleteProfileResponse {success: true}.",
        "errors": (
            "400 \"invalid profile data\" when a name is empty after trimming or usage_intent is not "
            "exactly one of \"Just for fun\", \"Learning\", \"Gardening\", \"Work or school\"; "
            + _AUTH_MIDDLEWARE_ERRORS
            + " 404 \"user not found\"; 500 \"internal server error\"." + _JSON_REJECTION
        ),
        "notes": (
            "Can be called again to overwrite the values. After success GET /auth/session reports "
            "profile_complete true. Called by the Tauri complete_profile command via "
            "UserClient::complete_profile."
        ),
    },
    "POST /user/delete": {
        "summary": "Deletes the account with the given email. Restricted to super admins.",
        "request": "JSON DeleteUserRequest {email}. Header Authorization: Bearer <access token of a super admin>.",
        "response": "200 with an empty body.",
        "errors": (
            "401 (empty body) from require_super_admin_auth when the token is missing, invalid or "
            "expired, the user no longer exists, or the caller's email is unverified (this middleware "
            "always requires a verified email, regardless of auth.require_email_verification); 403 "
            "(empty body) when the caller is not a SuperAdmin (Admin is not enough); 404 \"user not "
            "found\" when no account has that email; 500 \"internal server error\"." + _JSON_REJECTION
        ),
        "notes": "No Tauri command uses this route; it is exercised by tests through UserClient::delete_user.",
    },
    "POST /user/change-role/bypass": {
        "summary": "Dev-only route that sets any account's role without authentication.",
        "access": _DEV_ACCESS,
        "request": "JSON ChangeRoleRequest {email, role: \"User\" | \"Admin\" | \"SuperAdmin\"}.",
        "response": "200 JSON ChangeRoleResponse {success: true}.",
        "errors": "404 \"user not found\" when no account has that email; 500 \"internal server error\"." + _JSON_REJECTION,
        "notes": (
            _DEV_NOTE
            + " Used by tests through UserClient::change_role_bypass, which ignores the response body."
        ),
    },
}
