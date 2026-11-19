"""Hand-written descriptions for test code (backend/src/tests/, tb_client/tests/ and inline tests modules)."""

# ----------------------------------------------------------------------
# Shared note fragments
# ----------------------------------------------------------------------

_BACKEND_FIXTURE = (
    "Self-contained: TestFixture::new spawns an in-process Axum server on a random "
    "127.0.0.1 port with a fresh SQLite file (./<uuid>.db under backend/), email "
    "verification enabled, MockEmailSender and Dev-mode routes. No external backend, "
    "OpenAI key or network access is needed."
)

_BACKEND_RUN = (
    "Run from backend/: cargo test tests::login::{name} (or cargo test tests::login for "
    "the whole file, or cargo test for every backend test). backend/ is a single package "
    "(toxic_brainz_server), not a workspace, so -p is not required."
)

_TB_CLIENT_BROKEN = (
    "Known problem: this file does not compile. It imports addin_server_interactor (a "
    "crate from another project that is not a dependency of tb_client), so cargo test in "
    "backend/crates/tb_client fails with E0432/E0433 before any test runs. It would need "
    "to use tb_client::ApiClient instead."
)

_TB_CLIENT_LIVE = (
    "Preconditions (once it compiles): a backend already running at the "
    "ApiClient::default() address http://127.0.0.1:3001 in Dev mode (APP_ENV not "
    "\"production\") so the /dev and bypass routes exist, with email verification enabled "
    "(APP__auth__require_email_verification=true; the checked-in appsettings.ron disables "
    "it, in which case register_start returns no code and /auth/email/verify is not "
    "mounted). The tests call /dev/erase-db and wipe the backend's database "
    "(backend/the_database.db by default), so never point them at a database you care "
    "about. Because all tests share one server, one database and the dev clock, run them "
    "single-threaded: cargo test --test {binary} -- --test-threads=1 from "
    "backend/crates/tb_client. The backend's per-IP auth rate limits (10 login/register, "
    "20 refresh and 5 email verify/resend requests per minute) can make long runs fail "
    "with 429 responses; restart the backend between runs if that happens."
)

_DUPLICATE_OF_BACKEND = (
    "Duplicated: backend/src/tests/login.rs contains a near-identical test with the same "
    "name that runs against an in-process server and does compile and pass; prefer that one."
)

FILES: dict[str, dict] = {
    # ------------------------------------------------------------------
    # backend/src/tests (compiled into the backend binary under cfg(test))
    # ------------------------------------------------------------------
    "backend/src/tests/mod.rs": {
        "summary": (
            "Root of the backend's in-crate integration test module (declared in main.rs as "
            "#[cfg(test)] mod tests). Pulls in the login tests, the shared constants/helpers "
            "in common and the TestFixture utilities in utils."
        ),
        "details": (
            "These tests start a real Axum server inside the test process and talk to it over "
            "HTTP with the tb_client crate (a dev-dependency of the backend), so they exercise "
            "routing, middleware, services and the SQLite database end to end. Run all of them "
            "from backend/ with cargo test; as of this writing all 6 login tests plus the 7 "
            "inline unit tests pass in about 5 seconds."
        ),
        "symbols": {},
    },
    "backend/src/tests/common.rs": {
        "summary": (
            "Shared test constants (test user credentials) and helpers that register, verify "
            "and log in users or reset the database through tb_client."
        ),
        "details": (
            "This file is a copy of backend/crates/tb_client/tests/common/mod.rs adapted to "
            "take the fixture's ApiClient as a parameter instead of creating "
            "ApiClient::default(). Several items carry #[allow(dead_code)] because only some "
            "of them are used by login.rs."
        ),
        "symbols": {
            "EMAIL": "Email of the primary test user (\"myemail@email.com\").",
            "PASSWORD": "Password of the primary test user (\"testpassword\").",
            "EMAIL2": "Email of a second test user (\"myemail2@email.com\"); currently unused in this crate.",
            "PASSWORD2": "Password of the second test user (\"testpassword2\"); currently unused in this crate.",
            "EXPIRING_EMAIL": (
                "Email used by expiry tests (\"expiring.email@example.com\"); currently unused "
                "in this crate (used by tb_client/tests/email.rs)."
            ),
            "log_in_as_super_admin": {
                "description": (
                    "Ensures EMAIL exists as a SuperAdmin and logs the client in. Tries the "
                    "dev route POST /auth/register/start/superadmin and verifies the returned "
                    "code; ignores failure (the user may already exist). Then forces the role "
                    "with POST /user/change-role/bypass (errors are printed) and logs in with "
                    "POST /auth/login/bypass, storing the tokens in the client."
                ),
                "params": {"client": "ApiClient pointed at the test server."},
                "errors": (
                    "Panics (unwrap) if the registration succeeds but returns no verification "
                    "code, if verification fails, or if the bypass login fails."
                ),
                "notes": (
                    "Requires Dev mode and email verification enabled (true in "
                    "default_app_config). Not used by login.rs at the moment."
                ),
            },
            "reset_db": {
                "description": "Erases and recreates all tables through the dev route POST /dev/erase-db.",
                "params": {"client": "ApiClient pointed at the test server."},
                "returns": "Ok(()) on success.",
                "errors": "ClientError if the request fails (for example when not in Dev mode).",
                "notes": (
                    "Redundant for in-process tests, which already get a brand-new database "
                    "file per fixture, but harmless."
                ),
            },
            "register_verified_user_into_db": {
                "description": (
                    "Registers EMAIL/PASSWORD with POST /auth/register/start and verifies it "
                    "with the code returned in the response (POST /auth/email/verify)."
                ),
                "params": {"client": "ApiClient pointed at the test server."},
                "returns": "The VerifyEmailResponse.",
                "errors": (
                    "The registration ClientError, ClientError::MissingEmailVerificationCode "
                    "if no code was returned (not Dev mode or verification disabled), or the "
                    "verification error."
                ),
            },
            "register_user_into_db": {
                "description": "Registers EMAIL/PASSWORD without verifying it.",
                "params": {"client": "ApiClient pointed at the test server."},
                "returns": "The RegisterAttemptedResponse (contains the verification code in Dev mode).",
                "errors": "ClientError from the registration request.",
            },
            "register_certain_user_into_db": {
                "description": "Registers an arbitrary email/password pair without verifying it.",
                "params": {
                    "client": "ApiClient pointed at the test server.",
                    "email": "Email to register.",
                    "password": "Password to register.",
                },
                "returns": "The RegisterAttemptedResponse.",
                "errors": "ClientError from the registration request.",
            },
        },
    },
    "backend/src/tests/login.rs": {
        "summary": (
            "End-to-end authentication tests run against an in-process backend: health check, "
            "registration with email verification, verification code resend, normal and "
            "bypass login, wrong credentials, and rejection of an unauthenticated protected "
            "route."
        ),
        "details": (
            "Each test creates its own TestFixture (isolated server and database) and calls "
            "fixture.finish() at the end to shut the server down and delete the database "
            "file; if a test panics first, TestFixture's Drop does best-effort cleanup. Tests "
            "can therefore run in parallel. The same tests exist in "
            "backend/crates/tb_client/tests/endpoint.rs, but that copy targets a live server "
            "and does not compile."
        ),
        "symbols": {
            "test_root": {
                "description": (
                    "Verifies the server is up: calls GET /ping through misc_client and asserts "
                    "the call succeeds."
                ),
                "notes": _BACKEND_FIXTURE + " " + _BACKEND_RUN.format(name="test_root"),
            },
            "test_auth_bypass": {
                "description": (
                    "Verifies the dev-only bypass login works for a verified user: registers "
                    "EMAIL, verifies it with the code returned in the register response, then "
                    "calls POST /auth/login/bypass and asserts it succeeds."
                ),
                "notes": (
                    _BACKEND_FIXTURE + " Relies on Dev mode (the bypass route is not mounted "
                    "when APP_ENV=production). " + _BACKEND_RUN.format(name="test_auth_bypass")
                ),
            },
            "protected_route_test": {
                "description": (
                    "Verifies that a protected route cannot be used without logging in: calls "
                    "delete_user(EMAIL) (POST /user/delete) on a fresh client and asserts an "
                    "error."
                ),
                "notes": (
                    _BACKEND_FIXTURE + " Caveat: because no access token is set, tb_client "
                    "returns ClientError::AuthTokenNotSet locally and never sends the request, "
                    "so this test does not actually exercise the server's auth middleware. "
                    + _BACKEND_RUN.format(name="protected_route_test")
                ),
            },
            "test_register_verify_and_login": {
                "description": (
                    "Verifies the full sign-up flow: resets the database, registers EMAIL, "
                    "asserts the response contains an email verification code (Dev mode "
                    "returns it), verifies the email with that code, then logs in with "
                    "POST /auth/login and asserts success."
                ),
                "notes": _BACKEND_FIXTURE + " " + _BACKEND_RUN.format(name="test_register_verify_and_login"),
            },
            "test_resend_verification_email": {
                "description": (
                    "Verifies that a resent verification code works: registers EMAIL, ignores "
                    "the first code, calls POST /auth/email/resend and asserts it returns a new "
                    "code, verifies with the new code and logs in successfully."
                ),
                "notes": (
                    _BACKEND_FIXTURE + " It does not check that the original code was "
                    "invalidated. " + _BACKEND_RUN.format(name="test_resend_verification_email")
                ),
            },
            "test_log_in": {
                "description": (
                    "Verifies credential checking on POST /auth/login: after creating a "
                    "verified user with register_verified_user_into_db, asserts that the "
                    "correct email and password succeed, the correct email with a wrong "
                    "password fails, and an unknown user (\"fakeuser\") with the right "
                    "password fails."
                ),
                "notes": _BACKEND_FIXTURE + " " + _BACKEND_RUN.format(name="test_log_in"),
            },
        },
    },
    "backend/src/tests/utils/mod.rs": {
        "summary": (
            "Test infrastructure for the backend: builds a test AppConfig and AppState, spawns "
            "an in-process TestServer on a random port and provides TestFixture, which pairs "
            "that server with a tb_client ApiClient and cleans everything up afterwards."
        ),
        "details": (
            "Every fixture gets its own SQLite database file named after a random UUID in the "
            "current directory (backend/ when run through cargo test), its own rate limiter "
            "and its own AppClock, so tests do not interfere with each other or with "
            "backend/the_database.db. Local file storage points at ../TEST_LOCAL_SERVER "
            "(capstone/TEST_LOCAL_SERVER), which is shared. OpenAI settings are defaults "
            "(no API key), so plant scanning cannot be tested through this fixture without "
            "changes. If a test run is killed, leftover <uuid>.db files may remain in backend/ "
            "and can be deleted."
        ),
        "symbols": {
            "default_app_config": {
                "description": (
                    "Returns an AppConfig for tests: host 127.0.0.1 with port 0, JWT secret "
                    "\"change-me\", 15 minute access and 15 day refresh tokens, email "
                    "verification required, no email domain restriction, a local SQLite "
                    "database at ./<random uuid>.db, local file storage at "
                    "../TEST_LOCAL_SERVER and default OpenAI settings."
                ),
                "returns": "The test AppConfig.",
                "notes": (
                    "Unlike the checked-in appsettings.ron, email verification is enabled, so "
                    "register responses contain a verification code in Dev mode."
                ),
            },
            "default_local_state": {
                "description": (
                    "Builds the AppState for a test server: opens (and migrates) the SQLite "
                    "database from the config and wires LocalFileStorage, MockEmailSender, a "
                    "real AppClock, the config and a fresh RateLimiter."
                ),
                "params": {"config": "The test configuration, usually from default_app_config."},
                "returns": "The AppState.",
                "errors": "Panics (unwrap) if the database connection cannot be opened.",
            },
            "default_test_server": {
                "description": (
                    "Creates a default config and state, builds the full app router with "
                    "app_router and spawns it with TestServer::spawn."
                ),
                "returns": "A running TestServer whose addr field is http://127.0.0.1:<port>.",
            },
            "remove_db_file": {
                "description": (
                    "Deletes the SQLite file at path, retrying up to 10 times with a 50 ms "
                    "async sleep because the file can still be locked briefly after shutdown."
                ),
                "params": {"path": "Path of the database file."},
                "notes": "Prints to stderr if the file could not be removed; never fails the test.",
            },
            "clean_up_test_server": {
                "description": (
                    "Gracefully shuts the server down (awaiting its task) and then removes its "
                    "SQLite database file."
                ),
                "params": {"server": "The TestServer to stop."},
            },
            "TestFixture": (
                "Per-test harness holding a tb_client ApiClient (public client field) "
                "connected to a private in-process TestServer. Create with TestFixture::new "
                "and end with finish(); Drop provides fallback cleanup."
            ),
            "TestFixture::new": {
                "description": "Spawns a default test server and creates an ApiClient pointed at its address.",
                "returns": "A ready TestFixture.",
            },
            "TestFixture::finish": {
                "description": (
                    "Shuts the server down and deletes its database file. Call at the end of "
                    "every test so cleanup is awaited."
                ),
                "notes": "Consumes the fixture; afterwards Drop has nothing left to clean up.",
            },
            "TestFixture::drop [Drop]": {
                "description": (
                    "Fallback cleanup when a test panics or forgets to call finish(): signals "
                    "the server to shut down without waiting and deletes the database file on "
                    "a separate OS thread (up to 10 attempts, 50 ms apart)."
                ),
                "notes": (
                    "Deliberately does not block on the tokio runtime, because blocking inside "
                    "Drop on a runtime worker thread deadlocks."
                ),
            },
        },
    },
    # ------------------------------------------------------------------
    # backend/crates/tb_client/tests (integration tests of the client crate)
    # ------------------------------------------------------------------
    "backend/crates/tb_client/tests/common/mod.rs": {
        "summary": (
            "Shared constants and helpers for the tb_client integration tests: test user "
            "credentials, user registration/verification helpers, database reset and "
            "super-admin login."
        ),
        "details": (
            "Known problems: this module was copied from another project (an \"addin "
            "manager\" server) and was never fully ported. It imports addin_server_interactor "
            "and its csharp module, which are not dependencies of tb_client, so every test "
            "binary that includes it (email, endpoint, refresh) fails to compile. It also "
            "contains Windows-only absolute paths (TEST_LOCAL_SERVER_PATH, "
            "SAMPLE_CSPROJ_PATH) and C# build helpers that have nothing to do with Leaf Freak. "
            "Unlike backend/src/tests/common.rs, the register helpers create their own "
            "ApiClient::default() instead of using the caller's client. Fixing the imports to "
            "tb_client::ApiClient and deleting the C# items would make the crate compile."
        ),
        "symbols": {
            "EMAIL": "Email of the primary test user (\"myemail@email.com\").",
            "PASSWORD": "Password of the primary test user (\"testpassword\").",
            "EMAIL2": "Email of a second test user (\"myemail2@email.com\"), used by email.rs.",
            "PASSWORD2": "Password of the second test user (\"testpassword2\"), used by email.rs.",
            "EXPIRING_EMAIL": "Email used by the verification expiry test (\"expiring.email@example.com\").",
            "TEST_LOCAL_SERVER_PATH": (
                "Leftover from another project: a hard-coded Windows path "
                "(C:\\Users\\GRieger\\...\\addinmanager2_dev\\TEST_LOCAL_SERVER) used only by "
                "clear_test_local_server. Meaningless on other machines."
            ),
            "SAMPLE_CSPROJ_PATH": (
                "Leftover from another project: a hard-coded Windows path to a C# .csproj file "
                "used only by build_sample_csharp_project. Not relevant to Leaf Freak."
            ),
            "log_in_as_super_admin": {
                "description": (
                    "Ensures EMAIL exists as a SuperAdmin and logs the client in: tries POST "
                    "/auth/register/start/superadmin and verifies the code (ignored if the "
                    "user already exists), forces the role with POST "
                    "/user/change-role/bypass, then logs in with POST /auth/login/bypass so "
                    "the client holds access and refresh tokens."
                ),
                "params": {"client": "ApiClient pointed at the running backend."},
                "errors": "Panics if verification or the bypass login fails.",
                "notes": "Requires the backend in Dev mode with email verification enabled.",
            },
            "reset_db": {
                "description": "Erases and recreates all backend tables via POST /dev/erase-db.",
                "params": {"client": "ApiClient pointed at the running backend."},
                "returns": "Ok(()) on success.",
                "errors": "ClientError if the request fails or the route is not mounted (production mode).",
                "notes": "Destructive: wipes the database of whatever backend is running at 127.0.0.1:3001.",
            },
            "register_verified_user_into_db": {
                "description": (
                    "Creates its own ApiClient::default(), registers EMAIL/PASSWORD and "
                    "verifies the email with the code from the response."
                ),
                "returns": "The VerifyEmailResponse result.",
                "errors": "Panics (unwrap) if registration fails or no code is returned.",
            },
            "register_user_into_db": {
                "description": "Registers EMAIL/PASSWORD with a new ApiClient::default() without verifying it.",
                "returns": "The RegisterAttemptedResponse result (includes the code in Dev mode).",
            },
            "register_certain_user_into_db": {
                "description": "Registers an arbitrary email/password with a new ApiClient::default() without verifying it.",
                "params": {"email": "Email to register.", "password": "Password to register."},
                "returns": "The RegisterAttemptedResponse result.",
            },
            "clear_test_local_server": {
                "description": (
                    "Leftover from another project: deletes and recreates the directory at "
                    "TEST_LOCAL_SERVER_PATH."
                ),
                "errors": "Panics on non-Windows machines (canonicalize of the missing path fails).",
                "notes": "Unused by any Leaf Freak test; should be removed.",
            },
            "build_sample_csharp_project": {
                "description": (
                    "Leftover from another project: builds the C# project at "
                    "SAMPLE_CSPROJ_PATH through addin_server_interactor::csharp."
                ),
                "returns": "BuiltCSharpProjectOutput or CSharpError (types from the missing crate).",
                "notes": "Unused and does not compile in this repository; should be removed.",
            },
        },
    },
    "backend/crates/tb_client/tests/endpoint.rs": {
        "summary": (
            "Client-side copies of the basic endpoint tests (root, bypass login, protected "
            "route, register/verify/login, resend, wrong credentials) meant to run against a "
            "live backend at 127.0.0.1:3001."
        ),
        "details": (
            _TB_CLIENT_BROKEN + " It also calls client.test_client().hello() and expects the "
            "message \"Hello from Axum\", an API that does not exist in tb_client. "
            + _DUPLICATE_OF_BACKEND
        ),
        "symbols": {
            "test_root": {
                "description": (
                    "Intended to verify the server root responds: calls "
                    "test_client().hello() and asserts the message is \"Hello from Axum\"."
                ),
                "notes": (
                    "Broken beyond the import problem: tb_client has no test_client; the "
                    "equivalent check is misc_client().ping(). " + _DUPLICATE_OF_BACKEND
                ),
            },
            "test_auth_bypass": {
                "description": (
                    "Calls POST /auth/login/bypass for EMAIL/PASSWORD and asserts success."
                ),
                "notes": (
                    "Unlike the backend copy it does not create the user first, so it only "
                    "passes if EMAIL already exists and is verified (for example after "
                    "test_log_in ran). " + _TB_CLIENT_LIVE.format(binary="endpoint") + " "
                    + _TB_CLIENT_BROKEN
                ),
            },
            "protected_route_test": {
                "description": (
                    "Calls delete_user(EMAIL) without logging in and asserts an error."
                ),
                "notes": (
                    "The error comes from tb_client itself (AuthTokenNotSet) before any "
                    "request is sent. " + _TB_CLIENT_BROKEN + " " + _DUPLICATE_OF_BACKEND
                ),
            },
            "test_register_verify_and_login": {
                "description": (
                    "Resets the database, registers EMAIL, asserts a verification code is "
                    "returned, verifies with it and asserts that a normal login succeeds."
                ),
                "notes": _TB_CLIENT_LIVE.format(binary="endpoint") + " " + _TB_CLIENT_BROKEN,
            },
            "test_resend_verification_email": {
                "description": (
                    "Resets the database, registers EMAIL, requests a new code with POST "
                    "/auth/email/resend, verifies with the new code and asserts login succeeds."
                ),
                "notes": _TB_CLIENT_LIVE.format(binary="endpoint") + " " + _TB_CLIENT_BROKEN,
            },
            "test_log_in": {
                "description": (
                    "Resets the database, creates a verified user, then asserts that the right "
                    "credentials log in while a wrong password and an unknown user are rejected."
                ),
                "notes": _TB_CLIENT_LIVE.format(binary="endpoint") + " " + _TB_CLIENT_BROKEN,
            },
        },
    },
    "backend/crates/tb_client/tests/email.rs": {
        "summary": (
            "Integration tests for email verification codes against a live backend: codes "
            "expire after 2 minutes, wrong codes fail, codes are single-use and a code only "
            "verifies the user it was issued to."
        ),
        "details": (
            _TB_CLIENT_BROKEN + " These scenarios have no equivalent in backend/src/tests, so "
            "porting them to the in-process TestFixture would add real coverage. The expiry "
            "test uses the dev clock routes (/dev/clock/advance and /dev/clock/reset) to move "
            "the server's notion of time."
        ),
        "symbols": {
            "test_expired_email_verification_code_fails": {
                "description": (
                    "Verifies verification codes and access tokens expire. Resets the database "
                    "and the dev clock, registers EXPIRING_EMAIL, advances the clock by 121 "
                    "seconds (codes are valid for 2 minutes) and asserts verification fails. "
                    "Then resets the clock, logs in as super admin, advances the clock past "
                    "the 15 minute access token lifetime (16 minutes and 1 second) and asserts "
                    "that delete_user fails with a 401. Finally resets the clock."
                ),
                "notes": (
                    "If the test panics midway the dev clock stays advanced on the server; call "
                    "POST /dev/clock/reset or restart the backend. "
                    + _TB_CLIENT_LIVE.format(binary="email") + " " + _TB_CLIENT_BROKEN
                ),
            },
            "test_wrong_email_verification_code_fails": {
                "description": (
                    "Registers EMAIL and asserts that verifying with a modified code (the real "
                    "code with a \"1\" prepended) fails."
                ),
                "notes": _TB_CLIENT_LIVE.format(binary="email") + " " + _TB_CLIENT_BROKEN,
            },
            "test_already_used_code_fails": {
                "description": (
                    "Registers EMAIL, verifies with the issued code (asserts success) and then "
                    "asserts that verifying again with the same code fails."
                ),
                "notes": _TB_CLIENT_LIVE.format(binary="email") + " " + _TB_CLIENT_BROKEN,
            },
            "test_code_cannot_verify_a_different_user": {
                "description": (
                    "Registers EMAIL and EMAIL2, asserts that each user's code fails for the "
                    "other user, and that each code then succeeds for its own user."
                ),
                "notes": (
                    "Makes four verify requests, close to the backend's limit of 5 email "
                    "verify requests per minute per IP. "
                    + _TB_CLIENT_LIVE.format(binary="email") + " " + _TB_CLIENT_BROKEN
                ),
            },
        },
    },
    "backend/crates/tb_client/tests/refresh.rs": {
        "summary": (
            "Integration tests for access/refresh token handling against a live backend: "
            "login returns both tokens, refresh rotates tokens and invalidates the old refresh "
            "token, expired access tokens can be refreshed, expired refresh tokens are "
            "rejected, and a refresh token cannot be used as an access token."
        ),
        "details": (
            _TB_CLIENT_BROKEN + " This behaviour is what the Tauri get_session command relies "
            "on, and none of it is covered by backend/src/tests, so these tests are worth "
            "porting to the in-process fixture."
        ),
        "symbols": {
            "login_verified_user": {
                "description": (
                    "Helper: registers EMAIL, verifies it with the returned code and logs in "
                    "with POST /auth/login so the client holds both tokens."
                ),
                "params": {"client": "ApiClient that should end up logged in."},
                "returns": "The LoginResponse containing access_token and refresh_token.",
                "errors": "Panics (unwrap) if any step fails.",
            },
            "test_login_returns_access_and_refresh_tokens": {
                "description": (
                    "Resets the database, logs in a verified user and asserts both the access "
                    "token and the refresh token are non-empty."
                ),
                "notes": _TB_CLIENT_LIVE.format(binary="refresh") + " " + _TB_CLIENT_BROKEN,
            },
            "test_refresh_rotates_tokens_and_invalidates_old_refresh_token": {
                "description": (
                    "Logs in, calls POST /auth/refresh and asserts new non-empty tokens are "
                    "returned with a refresh token different from the original; then asserts "
                    "that refreshing again with the original refresh token "
                    "(refresh_with_token) fails, proving rotation revokes the old token."
                ),
                "notes": _TB_CLIENT_LIVE.format(binary="refresh") + " " + _TB_CLIENT_BROKEN,
            },
            "test_expired_access_token_can_be_refreshed": {
                "description": (
                    "Resets the database and dev clock, logs in as super admin, advances the "
                    "clock 16 minutes and 1 second and asserts delete_user(EMAIL) fails with a "
                    "401; then refreshes and asserts the same call now succeeds. Resets the "
                    "clock at the end."
                ),
                "notes": (
                    "The successful delete_user deletes the super admin itself. "
                    + _TB_CLIENT_LIVE.format(binary="refresh") + " " + _TB_CLIENT_BROKEN
                ),
            },
            "test_expired_refresh_token_is_rejected": {
                "description": (
                    "Logs in, advances the dev clock by 7 days and 1 second and asserts that "
                    "refreshing with the original refresh token fails. Resets the clock at the end."
                ),
                "notes": (
                    "Known problem: the test assumes a 7 day refresh token lifetime, but "
                    "appsettings.ron and the backend test config use 15 days, so against the "
                    "default configuration the refresh succeeds and the test fails. Either "
                    "advance by more than 15 days or start the backend with "
                    "APP__auth__refresh_token_ttl=7d. "
                    + _TB_CLIENT_LIVE.format(binary="refresh") + " " + _TB_CLIENT_BROKEN
                ),
            },
            "test_refresh_token_cannot_be_used_as_access_token": {
                "description": (
                    "Logs in as super admin, replaces the client's access token with its "
                    "refresh token and asserts that delete_user(EMAIL) is rejected with a 401."
                ),
                "notes": _TB_CLIENT_LIVE.format(binary="refresh") + " " + _TB_CLIENT_BROKEN,
            },
        },
    },
    # ------------------------------------------------------------------
    # Inline #[cfg(test)] mod tests in non-test files (tests:: symbols only)
    # ------------------------------------------------------------------
    "backend/src/features/file_storage/file_storage_trait.rs": {
        "symbols": {
            "tests::unique_test_root": {
                "description": (
                    "Builds a unique temporary directory path "
                    "(<system temp>/local_file_storage_test_<nanoseconds>) so tests running in "
                    "parallel do not collide."
                ),
                "returns": "The path (not yet created).",
            },
            "tests::cleanup": {
                "description": "Recursively deletes a test root directory, ignoring errors.",
                "params": {"root": "Directory created by storage_with_root."},
            },
            "tests::storage_with_root": {
                "description": "Creates a unique temporary directory and a LocalFileStorage rooted at it.",
                "returns": "(LocalFileStorage, root path) so the test can inspect the disk and clean up.",
                "errors": "Panics if the directory cannot be created.",
            },
            "tests::create_dir_and_check_exists": {
                "description": (
                    "Verifies create_dir_all and directory_exists: creates nested/dir and "
                    "asserts it exists while nested/missing does not."
                ),
                "notes": (
                    "Pure unit test using the OS temp directory; no server or database. Run "
                    "from backend/ with cargo test file_storage_trait::tests."
                ),
            },
            "tests::write_read_and_delete_file": {
                "description": (
                    "Verifies the file round trip: writes docs/hello.txt (parent directory "
                    "created automatically), asserts file_exists is true for it and false for "
                    "a missing file, reads the bytes back and compares, deletes it and asserts "
                    "it no longer exists."
                ),
                "notes": "Run from backend/ with cargo test file_storage_trait::tests::write_read_and_delete_file.",
            },
            "tests::list_files_in_directory": {
                "description": (
                    "Writes uploads/a.txt, uploads/b.txt and uploads/.keep and asserts "
                    "get_files_in_dir returns all three, including the dotfile, sorted "
                    "alphabetically."
                ),
                "notes": "Run from backend/ with cargo test file_storage_trait::tests::list_files_in_directory.",
            },
            "tests::delete_directory_removes_nested_content": {
                "description": (
                    "Writes bundle/nested/file.bin, then delete_dir(\"bundle\") and asserts "
                    "both the directory and the nested file are gone."
                ),
                "notes": "Run from backend/ with cargo test file_storage_trait::tests::delete_directory_removes_nested_content.",
            },
            "tests::rejects_path_traversal": {
                "description": (
                    "Security check: asserts write_file_bytes(\"../escape.txt\") returns an "
                    "error, because resolve_path rejects parent-directory components."
                ),
                "notes": (
                    "Only checks that an error is returned, not which FileStorageError "
                    "variant. Run from backend/ with cargo test "
                    "file_storage_trait::tests::rejects_path_traversal."
                ),
            },
            "tests::files_are_confined_to_root_directory": {
                "description": (
                    "Writes inside/root.txt and asserts it exists under the storage root on "
                    "disk and that no outside.txt was created in the root's parent directory."
                ),
                "notes": (
                    "A weak check: nothing in the test tries to write outside.txt, so it "
                    "mainly confirms that relative paths are joined to the root. Run from "
                    "backend/ with cargo test file_storage_trait::tests::files_are_confined_to_root_directory."
                ),
            },
        },
    },
    "backend/src/features/plant_scan/service.rs": {
        "symbols": {
            "tests::reads_imageio_gps_dictionary": {
                "description": (
                    "Verifies that read_image_geolocation extracts GPS coordinates from a JPEG "
                    "whose GPS data was written by the iOS camera plugin (ImageIO GPS "
                    "dictionary). Loads the fixture fixtures/ios_gps.jpg with include_bytes! "
                    "and asserts latitude 41.8781 and longitude -87.6298 (Chicago) within "
                    "0.0001 degrees."
                ),
                "notes": (
                    "Fixture: backend/src/features/plant_scan/fixtures/ios_gps.jpg, compiled "
                    "into the test binary. No network, OpenAI or database needed. Run from "
                    "backend/ with cargo test plant_scan::service::tests. A regression here "
                    "means scans from iPhones would lose their map location."
                ),
            },
        },
    },
    "backend/crates/tb_client/src/error.rs": {
        "symbols": {
            "tests::user_message_uses_http_body": {
                "description": (
                    "Verifies that for ClientError::RequestFailed (status 401, body \"invalid "
                    "credentials\") user_message returns the body unchanged, while the Display "
                    "string keeps the technical form \"request failed with status 401: invalid "
                    "credentials\"."
                ),
                "notes": (
                    "Pure unit test. Run with cargo test -p tb_client --lib from backend/, or "
                    "cargo test --lib from backend/crates/tb_client (plain cargo test there "
                    "also builds the broken integration tests and fails). Running inside the "
                    "crate directory rewrites its out-of-date Cargo.lock; discard that change "
                    "if you did not mean to update dependencies."
                ),
            },
            "tests::user_message_falls_back_on_empty_body": {
                "description": (
                    "Verifies that a RequestFailed error whose body is only whitespace "
                    "(status 500, \"  \\n\") produces the generic message \"Something went wrong\"."
                ),
                "notes": "Pure unit test. Run with cargo test -p tb_client --lib from backend/.",
            },
        },
    },
}
