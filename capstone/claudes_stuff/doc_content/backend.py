"""Hand-written descriptions for the Axum backend (backend/src/, excluding tests)."""

FILES: dict[str, dict] = {
    # ------------------------------------------------------------------
    # Crate root
    # ------------------------------------------------------------------
    "backend/src/main.rs": {
        "summary": (
            "Entry point of the Leaf Freak backend server. Loads configuration, validates "
            "that the configuration is safe for the current environment, opens the SQLite "
            "database, builds the shared AppState and serves the Axum router."
        ),
        "details": (
            "Declares the crate modules (app_config, clock, environment, features, prelude, "
            "rate_limit, state, test_server and the cfg(test) tests module). Configuration "
            "comes from backend/appsettings.ron, overridden by environment variables with the "
            "APP prefix and a double-underscore separator (for example APP__auth__jwt_secret). "
            "A .env file is loaded first via dotenv. The default checked-in settings bind to "
            "127.0.0.1:3001, use 15 minute access tokens and 15 day refresh tokens, and have "
            "email verification turned off. In production (APP_ENV=production) all dev-only "
            "routes are omitted; in every other case the server is in Dev mode."
        ),
        "symbols": {
            "DEFAULT_JWT_SECRET": (
                "The placeholder JWT secret \"change-me\" shipped in appsettings.ron. "
                "is_weak_jwt_secret treats this value as weak, so production refuses to start "
                "with it."
            ),
            "load_config": {
                "description": (
                    "Builds the AppConfig from appsettings.ron (resolved relative to the current "
                    "working directory) and then layers APP__-prefixed environment variables on "
                    "top, using \"__\" as the nesting separator."
                ),
                "returns": "The deserialized AppConfig.",
                "errors": (
                    "config::ConfigError when the file is missing, malformed, or a required "
                    "field is absent."
                ),
                "notes": (
                    "The server must be started from the backend/ directory (or a directory "
                    "containing appsettings.ron) for the file source to be found. main calls "
                    "expect on the result, so a bad config aborts startup."
                ),
            },
            "init_tracing": {
                "description": (
                    "Installs the global tracing subscriber with a formatting layer. The log "
                    "filter comes from RUST_LOG and falls back to \"debug\" when RUST_LOG is "
                    "unset or invalid."
                ),
            },
            "is_weak_jwt_secret": {
                "description": (
                    "Returns true when the JWT secret is empty, whitespace only, or equal to "
                    "DEFAULT_JWT_SECRET."
                ),
                "params": {"secret": "The configured auth.jwt_secret value."},
                "returns": "true if the secret should be considered unsafe.",
            },
            "is_loopback_host": {
                "description": (
                    "Returns true when the configured bind host is exactly \"127.0.0.1\", "
                    "\"localhost\" or \"::1\"."
                ),
                "params": {"host": "The configured server.host value."},
                "returns": "true for loopback hosts.",
                "notes": "Other loopback forms such as 127.0.0.2 are not recognised.",
            },
            "allow_insecure_dev": {
                "description": (
                    "Reads the APP_ALLOW_INSECURE_DEV environment variable. Returns true when it "
                    "is \"1\" or \"true\" (case-insensitive)."
                ),
                "returns": "true if a Dev server may bind to a non-loopback host.",
            },
            "validate_startup_config": {
                "description": (
                    "Startup safety checks. In production it refuses to start with a weak JWT "
                    "secret. In Dev it logs a warning about a weak secret, and refuses to bind "
                    "to a non-loopback host unless APP_ALLOW_INSECURE_DEV is set, because Dev "
                    "mode mounts unauthenticated bypass routes (/auth/login/bypass, "
                    "/auth/register/start/superadmin, /user/change-role/bypass, /dev/erase-db, "
                    "/dev/clock/advance)."
                ),
                "params": {"config": "The loaded application configuration."},
                "errors": (
                    "Panics (does not return a Result) on a weak production secret or an "
                    "unsafe Dev bind address."
                ),
                "notes": (
                    "Testing a phone on the same Wi-Fi network against a Dev server requires "
                    "binding to 0.0.0.0 and setting APP_ALLOW_INSECURE_DEV=1."
                ),
            },
            "ping": {
                "description": (
                    "Handler for GET /ping. Always returns 200 OK with an empty body; used as a "
                    "health check."
                ),
                "returns": "Ok(()), which Axum renders as an empty 200 response.",
            },
            "app_router": {
                "description": (
                    "Builds the full application router: /ping plus the merged auth, clock, "
                    "user, plant_scan and dev routers, with the shared AppState attached."
                ),
                "params": {
                    "state": "The shared application state cloned into each feature router.",
                    "config": (
                        "Configuration used by auth_router to decide whether the email "
                        "verification routes are mounted."
                    ),
                },
                "returns": "A ready-to-serve Router with state applied.",
                "notes": (
                    "Public so integration tests can build the same router and run it with "
                    "TestServer."
                ),
            },
            "main": {
                "description": (
                    "Tokio entry point. Loads .env, initialises tracing, loads and validates "
                    "config, connects to the SQLite database (running migrations and creating "
                    "missing tables), builds AppState with LocalFileStorage, MockEmailSender, a "
                    "fresh AppClock and a RateLimiter, then serves the router on "
                    "server.host:server.port with connect info so the rate limiter can see "
                    "client IPs."
                ),
                "notes": (
                    "Uses expect/unwrap for config loading, DB connection, address parsing and "
                    "binding, so any of those failures terminate the process with a panic. "
                    "Logs a loud warning listing the dangerous routes when running in Dev mode. "
                    "Emails are never actually sent because MockEmailSender is always used."
                ),
            },
        },
    },
    "backend/src/app_config.rs": {
        "summary": (
            "Serde-deserializable configuration structs that mirror backend/appsettings.ron. "
            "Every value can be overridden with APP__section__field environment variables."
        ),
        "details": (
            "Several fields are declared but not read anywhere in the server code at the "
            "moment: AuthConfig.enforce_email_domain, DbConfig.url, LocalSqliteConfig.enabled "
            "and FileStorageConfig.use_local_file_storage. The server always uses local SQLite "
            "and local file storage."
        ),
        "symbols": {
            "AppConfig": (
                "Root configuration. Fields: server (ServerConfig), auth (AuthConfig), db "
                "(DbConfig), file_storage (FileStorageConfig) and openai (OpenAiConfig, "
                "defaults to empty when the section is omitted)."
            ),
            "OpenAiConfig": (
                "OpenAI settings. api_key: optional key; when missing or blank the "
                "OPENAI_API_KEY environment variable is used instead. model: optional model "
                "name; defaults to gpt-4o when unset or blank."
            ),
            "AuthConfig": (
                "Authentication settings. enforce_email_domain: optional domain restriction "
                "(currently unused). access_token_ttl and refresh_token_ttl: duration strings "
                "parsed by duration-str such as \"15m\" or \"15d\" (an unparsable value panics "
                "when a token is issued). jwt_secret: HS256 signing secret. "
                "require_email_verification: when true, registration sends a 6-digit code and "
                "the /auth/email/verify and /auth/email/resend routes are mounted; when false "
                "new accounts are marked verified immediately."
            ),
            "ServerConfig": (
                "Bind address. port: TCP port (3001 in the default settings). host: bind host "
                "(127.0.0.1 by default; Dev mode refuses non-loopback hosts unless "
                "APP_ALLOW_INSECURE_DEV is set)."
            ),
            "DbConfig": (
                "Database settings. url: reserved for a future non-SQLite database (unused). "
                "local_sqlite: required in practice, because get_database_connection unwraps it."
            ),
            "LocalSqliteConfig": (
                "Local SQLite settings. enabled: currently not checked. db_path: path of the "
                "database file, for example ./the_database.db."
            ),
            "FileStorageConfig": (
                "File storage settings. use_local_file_storage: currently not checked. "
                "local_file_storage_directory_path: root directory for uploaded scan images "
                "(../TEST_LOCAL_SERVER in the default settings); required, startup panics "
                "without it."
            ),
        },
    },
    "backend/src/clock.rs": {
        "summary": (
            "Application clock abstraction. All time-sensitive logic (token expiry, code expiry, "
            "the \"today\" used for daily quests and streaks) reads time through the Clock trait "
            "so that Dev builds and tests can shift time forward."
        ),
        "details": (
            "AppClock stores an offset in seconds in an atomic, added to the real UTC time. "
            "The offset is controlled through the Dev-only /dev/clock routes. Note that "
            "TestServer and the rate limiter use std::time::Instant and are not affected by "
            "the offset."
        ),
        "symbols": {
            "MAX_OFFSET_SECONDS": (
                "Upper bound on the absolute clock offset: 100 years expressed in seconds "
                "(100 * 365 * 24 * 60 * 60). Advancing beyond this fails with "
                "ClockError::OffsetOutOfRange."
            ),
            "Clock": (
                "Trait (Send + Sync) for a source of the current time. Implementors provide "
                "now_utc; now_db has a default implementation."
            ),
            "Clock::now_utc": {
                "description": "Returns the current time in UTC as seen by this clock.",
                "returns": "DateTime<Utc>.",
            },
            "Clock::now_db": {
                "description": (
                    "Default method returning now_utc converted to a fixed-offset "
                    "DateTimeWithTimeZone, the type SeaORM uses for timestamp columns."
                ),
                "returns": "DateTimeWithTimeZone with a +00:00 offset.",
            },
            "AppClock": (
                "The production Clock implementation: real system time plus an adjustable "
                "offset_seconds (AtomicI64, starts at 0). Shared through AppState as "
                "Arc<AppClock>."
            ),
            "ClockError": (
                "Error for clock adjustments. Variants: OffsetOutOfRange - the requested "
                "offset would overflow i64 or exceed MAX_OFFSET_SECONDS."
            ),
            "AppClock::new": {
                "description": "Creates a clock with a zero offset (real time).",
                "returns": "A new AppClock.",
            },
            "AppClock::offset_seconds": {
                "description": "Returns the current offset from real time, in seconds.",
                "returns": "The offset (may be negative).",
            },
            "AppClock::advance_seconds": {
                "description": (
                    "Atomically adds seconds to the offset. The update is rejected if the "
                    "addition overflows or the resulting absolute offset exceeds "
                    "MAX_OFFSET_SECONDS."
                ),
                "params": {
                    "seconds": "Number of seconds to move the clock (negative moves it back).",
                },
                "returns": "The new total offset in seconds.",
                "errors": "ClockError::OffsetOutOfRange when the new offset is out of range.",
                "notes": "On error the offset is left unchanged.",
            },
            "AppClock::reset": {
                "description": "Sets the offset back to 0 so the clock returns real time.",
            },
            "AppClock::now_utc [Clock]": {
                "description": "Returns Utc::now() plus the current offset.",
                "returns": "The shifted current time in UTC.",
            },
        },
    },
    "backend/src/environment.rs": {
        "summary": (
            "Determines whether the server runs in Dev or Prod mode from the APP_ENV "
            "environment variable."
        ),
        "details": (
            "Only the exact value APP_ENV=production selects Prod; anything else (including "
            "unset) is Dev. Dev mode mounts unauthenticated bypass routes and returns "
            "verification/reset codes in API responses, so production deployments must set "
            "APP_ENV=production. The variable is read on every call, not cached."
        ),
        "symbols": {
            "AppEnvironment": (
                "Runtime environment. Variants: Dev - development (default, dangerous helper "
                "routes enabled); Prod - production (APP_ENV=production)."
            ),
            "get_environment": {
                "description": (
                    "Reads APP_ENV and returns Prod when it equals \"production\", otherwise Dev."
                ),
                "returns": "The current AppEnvironment.",
            },
            "is_dev": {
                "description": "Returns true when get_environment() is Dev.",
                "returns": "true in Dev mode.",
            },
            "is_prod": {
                "description": "Returns true when get_environment() is Prod.",
                "returns": "true in production.",
            },
        },
    },
    "backend/src/prelude.rs": {
        "summary": (
            "Crate-wide prelude re-exporting commonly used items so most modules only need "
            "`use crate::prelude::*;`."
        ),
        "details": (
            "Re-exports std Path/PathBuf/Arc, Axum routing and extractor types (Json, Router, "
            "Request, State, StatusCode, IntoResponse, Response, get, post), chrono "
            "DateTime/Utc, SeaORM traits and types, serde derive macros, thiserror::Error, "
            "the shared server_types prelude (request/response DTOs) and RoleType, plus crate "
            "items AppConfig, AppClock, Clock, environment helpers, Role, UserIdType and "
            "AppState."
        ),
    },
    "backend/src/rate_limit.rs": {
        "summary": (
            "In-memory, per-IP sliding-window rate limiter applied to the public "
            "authentication routes."
        ),
        "details": (
            "Each (client IP, bucket) pair keeps the timestamps of requests in the last 60 "
            "seconds. Limits per minute: login/register 10, refresh 20, email verify/resend 5, "
            "password forgot/reset 5. Exceeding a limit returns 429 Too Many Requests with the "
            "body \"too many requests\". State is process-local and lost on restart, and old "
            "keys are never removed from the map (only their timestamps are pruned). The Dev "
            "bypass routes are not rate limited because they are added after the layer."
        ),
        "symbols": {
            "WINDOW": "Length of the sliding window: 60 seconds.",
            "AuthRateBucket": (
                "Groups of auth endpoints that share a limit. Variants: LoginRegister "
                "(/auth/login, /auth/register/start; 10 per minute), Refresh (/auth/refresh; "
                "20 per minute), EmailVerify (/auth/email/verify, /auth/email/resend; 5 per "
                "minute), PasswordReset (/auth/password/forgot, /auth/password/reset; 5 per "
                "minute)."
            ),
            "AuthRateBucket::key": {
                "description": (
                    "Returns the stable string key for the bucket (\"login_register\", "
                    "\"refresh\", \"email_verify\", \"password_reset\") used in the limiter map."
                ),
                "returns": "A static string identifying the bucket.",
            },
            "AuthRateBucket::limit": {
                "description": (
                    "Returns the maximum number of requests allowed per WINDOW for the bucket: "
                    "10, 20, 5 or 5 respectively."
                ),
                "returns": "The per-minute request limit.",
            },
            "AuthRateBucket::from_path": {
                "description": (
                    "Maps a request path to its bucket by exact string match. Paths not listed "
                    "return None and are not limited."
                ),
                "params": {"path": "The request URI path, without query string."},
                "returns": "Some(bucket) for rate-limited auth paths, otherwise None.",
                "notes": (
                    "The paths are hard-coded, so renaming an auth route silently removes its "
                    "rate limit (flagged with a TODO in the code)."
                ),
            },
            "RateLimiter": (
                "Thread-safe limiter state: a Mutex-protected HashMap from (client IP, bucket "
                "key) to the Instants of recent requests. Stored in AppState as "
                "Arc<RateLimiter>."
            ),
            "RateLimiter::new": {
                "description": "Creates an empty limiter.",
                "returns": "A new RateLimiter.",
            },
            "RateLimiter::check": {
                "description": (
                    "Prunes timestamps older than WINDOW for the (IP, bucket) key, rejects the "
                    "request if the remaining count has reached the bucket limit, otherwise "
                    "records the current request and allows it."
                ),
                "params": {
                    "client_ip": "Client IP address as a string (or \"unknown\").",
                    "bucket": "The bucket the request belongs to.",
                },
                "returns": "true if the request is allowed, false if it should be rejected.",
                "notes": (
                    "Rejected requests are not recorded, so a client that keeps retrying is "
                    "allowed again as soon as the oldest timestamp leaves the window. A "
                    "poisoned mutex is recovered rather than panicking."
                ),
            },
            "rate_limit_auth": {
                "description": (
                    "Axum middleware. Looks up the bucket for the request path; if there is "
                    "none the request passes through. Otherwise it reads the client IP from "
                    "ConnectInfo<SocketAddr> and calls RateLimiter::check."
                ),
                "params": {
                    "state": "Application state holding the shared RateLimiter.",
                    "request": "The incoming request.",
                    "next": "The rest of the middleware chain.",
                },
                "returns": (
                    "The downstream response, or 429 Too Many Requests with body \"too many "
                    "requests\"."
                ),
                "notes": (
                    "If ConnectInfo is missing (router not served with "
                    "into_make_service_with_connect_info) all clients share the \"unknown\" "
                    "key. Behind a reverse proxy every client would share the proxy IP, since "
                    "X-Forwarded-For is not consulted."
                ),
            },
        },
    },
    "backend/src/state.rs": {
        "summary": "Defines AppState, the shared state handed to every Axum handler.",
        "symbols": {
            "AppState": (
                "Cloneable application state. Fields: db (SeaORM DatabaseConnection), "
                "email_sender (Arc<dyn EmailSender>, MockEmailSender in practice), file_storage "
                "(Arc<dyn FileStorage>, LocalFileStorage in practice), clock (Arc<AppClock>, the "
                "offsettable clock), app_config (Arc<AppConfig>) and rate_limiter "
                "(Arc<RateLimiter>)."
            ),
        },
    },
    "backend/src/test_server.rs": {
        "summary": (
            "Test helper that runs an Axum router on a random local port in a background task "
            "so integration tests can make real HTTP requests."
        ),
        "details": (
            "Compiled into the main binary but only used by tests (items are marked "
            "allow(dead_code)). Uses unwrap when binding, so a bind failure panics the test."
        ),
        "symbols": {
            "TestServer": (
                "A running test server. Fields: addr (base URL such as http://127.0.0.1:54321), "
                "a private oneshot shutdown sender, the JoinHandle of the serving task, and the "
                "AppConfig the test built the app with."
            ),
            "TestServer::spawn": {
                "description": (
                    "Binds 127.0.0.1:0 (an OS-assigned free port), spawns axum::serve with "
                    "connect info and graceful shutdown wired to a oneshot channel, and returns "
                    "the handle."
                ),
                "params": {
                    "app": "The router to serve, typically from app_router.",
                    "config": "The config the router was built with; stored for the test's use.",
                },
                "returns": "A TestServer whose addr is ready to accept requests.",
            },
            "TestServer::signal_shutdown": {
                "description": (
                    "Sends the graceful shutdown signal if it has not been sent yet. Safe to "
                    "call more than once."
                ),
            },
            "TestServer::shutdown": {
                "description": (
                    "Signals shutdown and waits for the serving task to finish. Consumes the "
                    "TestServer."
                ),
            },
        },
    },
    # ------------------------------------------------------------------
    # features (root)
    # ------------------------------------------------------------------
    "backend/src/features/mod.rs": {
        "summary": (
            "Declares the feature modules of the backend: auth, clock, db, dev, email_server, "
            "file_storage, user and plant_scan."
        ),
    },
    # ------------------------------------------------------------------
    # auth
    # ------------------------------------------------------------------
    "backend/src/features/auth/mod.rs": {
        "summary": (
            "Authentication feature root. Declares the middleware, password, "
            "password_reset_repo, repo, routes, service and tokens submodules, re-exports "
            "AuthenticatedUser, require_auth and auth_router, and defines the Role enum stored "
            "on users."
        ),
        "symbols": {
            "Role": (
                "User role stored as text in the users.role column. Variants: User "
                "(\"user\", default for normal registrations), Admin (\"admin\"), SuperAdmin "
                "(\"superadmin\", required for /user/delete). Can be parsed from those strings "
                "or converted from the shared RoleType."
            ),
            "InvalidRoleError": (
                "Error returned when parsing a string that is not \"user\", \"admin\" or "
                "\"superadmin\" into a Role. Holds the rejected string."
            ),
            "Role::from_str [FromStr]": {
                "description": (
                    "Parses \"user\", \"admin\" or \"superadmin\" (case-sensitive) into a Role."
                ),
                "params": {"s": "The role string."},
                "returns": "The matching Role.",
                "errors": "InvalidRoleError for any other string.",
            },
            "Role::from [From<RoleType>]": {
                "description": (
                    "Converts the shared server_types RoleType (used in request bodies such as "
                    "ChangeRoleRequest) into the database Role."
                ),
                "params": {"role": "The shared role type."},
                "returns": "The equivalent Role.",
            },
        },
    },
    "backend/src/features/auth/middleware.rs": {
        "summary": (
            "Axum middleware that authenticates requests using a Bearer access token, plus the "
            "AuthenticatedUser extractor that handlers use to get the caller's id and role."
        ),
        "details": (
            "require_auth honours auth.require_email_verification; the admin and super-admin "
            "variants always require a verified email. All authentication failures return a "
            "bare 401 status with no body; role failures return 403."
        ),
        "symbols": {
            "AuthenticatedUser": (
                "The authenticated caller, inserted into request extensions by the auth "
                "middleware. Fields: user_id (i32) and role (Role, read from the database on "
                "each request)."
            ),
            "AuthenticatedUser::from_request_parts [FromRequestParts<S>]": {
                "description": (
                    "Extractor implementation. Reads the AuthenticatedUser that a require_* "
                    "middleware placed in the request extensions."
                ),
                "params": {"parts": "Request parts whose extensions are inspected."},
                "returns": "A clone of the AuthenticatedUser.",
                "errors": (
                    "401 Unauthorized if no middleware ran (for example a route that forgot "
                    "the require_auth layer)."
                ),
            },
            "require_auth": {
                "description": (
                    "Middleware for normal authenticated routes. Extracts the Bearer token, "
                    "validates it and loads the user (see authenticated_user_from_token), "
                    "requiring a verified email only when auth.require_email_verification is "
                    "true, then stores the AuthenticatedUser in the request extensions."
                ),
                "params": {
                    "state": "Application state (JWT secret, clock, database, config).",
                    "request": "The incoming request.",
                    "next": "The rest of the chain.",
                },
                "returns": "The downstream response.",
                "errors": "401 Unauthorized when the header is missing or the token/user is invalid.",
            },
            "require_admin_auth": {
                "description": (
                    "Like require_auth but always requires a verified email and additionally "
                    "requires the user's role to be Admin or SuperAdmin."
                ),
                "params": {
                    "state": "Application state.",
                    "request": "The incoming request.",
                    "next": "The rest of the chain.",
                },
                "returns": "The downstream response.",
                "errors": [
                    "401 Unauthorized - missing, invalid or expired token, or unverified email",
                    "403 Forbidden - role is User",
                ],
                "notes": "Not currently attached to any route. Logs the caller's role at info level.",
            },
            "require_super_admin_auth": {
                "description": (
                    "Like require_admin_auth but only allows the SuperAdmin role. Used for "
                    "POST /user/delete."
                ),
                "params": {
                    "state": "Application state.",
                    "request": "The incoming request.",
                    "next": "The rest of the chain.",
                },
                "returns": "The downstream response.",
                "errors": [
                    "401 Unauthorized - missing, invalid or expired token, or unverified email",
                    "403 Forbidden - role is not SuperAdmin",
                ],
            },
            "authenticated_user_from_token": {
                "description": (
                    "Validates an access token with service::user_id_from_token (signature, "
                    "typ must be \"access\", expiry checked against the app clock), loads the "
                    "user from the database and optionally checks email_verified."
                ),
                "params": {
                    "state": "Application state providing the JWT secret, clock and database.",
                    "token": "The raw JWT from the Authorization header.",
                    "require_email_verified": "Whether an unverified user should be rejected.",
                },
                "returns": "AuthenticatedUser with the user's id and current role.",
                "errors": (
                    "401 Unauthorized for any token problem, a deleted user, a database error, "
                    "or an unverified email when required."
                ),
                "notes": (
                    "Because the user row is loaded every time, deleting a user or changing "
                    "their role takes effect immediately even for already-issued tokens."
                ),
            },
            "bearer_token": {
                "description": (
                    "Extracts the token from an Authorization header value of the form "
                    "\"Bearer <token>\"."
                ),
                "params": {"header": "The Authorization header value, if present."},
                "returns": (
                    "The token string, or None if the header is missing, not valid ASCII, or "
                    "does not start with exactly \"Bearer \" (the prefix is case-sensitive)."
                ),
            },
        },
    },
    "backend/src/features/auth/password.rs": {
        "summary": (
            "Password hashing helpers built on bcrypt with an additional per-user random salt "
            "appended to the password."
        ),
        "details": (
            "Security notes: each user gets a 64-character hex salt stored in users.salt, which "
            "is concatenated after the password before bcrypt (DEFAULT_COST). bcrypt already "
            "salts internally, and it only uses the first 72 bytes of input, so for longer "
            "passwords part or all of the appended salt is ignored. Despite the function name "
            "\"peppered\", there is no server-side secret pepper."
        ),
        "symbols": {
            "generate_salt": {
                "description": (
                    "Generates 32 random bytes from the OS random number generator and returns "
                    "them hex-encoded."
                ),
                "returns": "A 64-character lowercase hex string.",
            },
            "peppered_password": {
                "description": (
                    "Concatenates the password and the salt (password first). If the salt is "
                    "empty the password is returned unchanged, which keeps compatibility with "
                    "accounts created without a salt."
                ),
                "params": {
                    "password": "The plaintext password.",
                    "salt": "The user's stored salt.",
                },
                "returns": "The string that is actually passed to bcrypt.",
            },
            "hash_password": {
                "description": "Hashes password + salt with bcrypt at DEFAULT_COST.",
                "params": {
                    "password": "The plaintext password.",
                    "salt": "The salt from generate_salt.",
                },
                "returns": "The bcrypt hash string to store in users.password_hash.",
                "errors": "bcrypt::BcryptError if hashing fails.",
            },
            "verify_password": {
                "description": "Checks a plaintext password against a stored bcrypt hash and salt.",
                "params": {
                    "password": "The plaintext password supplied at login.",
                    "salt": "The user's stored salt.",
                    "password_hash": "The user's stored bcrypt hash.",
                },
                "returns": "true if the password matches.",
                "errors": "bcrypt::BcryptError if the stored hash is malformed.",
            },
        },
    },
    "backend/src/features/auth/password_reset_repo.rs": {
        "summary": (
            "Database access for the password_reset table, which holds at most one pending "
            "password reset code per user."
        ),
        "details": (
            "Codes are stored as bcrypt hashes, never in plaintext. Expiry (15 minutes) and the "
            "5-attempt limit are enforced by auth::service."
        ),
        "symbols": {
            "create_reset": {
                "description": "Hashes the code with bcrypt and inserts a new reset row with attempts = 0.",
                "params": {
                    "db": "Database connection or transaction.",
                    "user_id": "The user requesting the reset.",
                    "plain_text_code": "The 6-digit code that will be emailed.",
                    "created_at": "Creation timestamp (from the app clock).",
                    "expires_at": "Expiry timestamp.",
                },
                "returns": "The inserted password_reset::Model.",
                "errors": (
                    "DbErr on insert failure (including the unique user_id constraint if an "
                    "old row was not deleted first); bcrypt failures are wrapped as "
                    "DbErr::Custom."
                ),
            },
            "find_by_user_id": {
                "description": "Finds the pending reset for a user.",
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "The reset row, or None.",
                "errors": "DbErr on query failure.",
            },
            "delete_by_user_id": {
                "description": "Deletes any pending reset for the user.",
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "The DeleteResult (rows affected).",
                "errors": "DbErr on failure.",
            },
            "delete_expired": {
                "description": "Deletes every reset row (for all users) whose expires_at is before now.",
                "params": {"db": "Database connection.", "now": "The current time from the app clock."},
                "returns": "The DeleteResult.",
                "errors": "DbErr on failure.",
            },
            "increment_attempts": {
                "description": "Sets attempts to current_attempts + 1 (saturating) on the given reset row.",
                "params": {
                    "db": "Database connection.",
                    "id": "Primary key of the reset row.",
                    "current_attempts": "The attempts value the caller read earlier.",
                },
                "returns": "The updated row.",
                "errors": "DbErr::Custom(\"password reset not found\") if the row is gone, or other DbErr.",
                "notes": (
                    "Not atomic: concurrent wrong guesses based on the same read value can "
                    "each write the same incremented count."
                ),
            },
        },
    },
    "backend/src/features/auth/repo.rs": {
        "summary": (
            "Database access for user rows needed by the auth flow: lookup by email/id, "
            "creating a pending user and updating verification, refresh-token and last-login "
            "columns."
        ),
        "symbols": {
            "find_by_email": {
                "description": "Finds a user by exact email match.",
                "params": {"db": "Database connection.", "email": "Email (callers trim it first)."},
                "returns": "The user, or None.",
                "errors": "DbErr on query failure.",
                "notes": "The comparison is case-sensitive at the SQL level, so Foo@x.com and foo@x.com are different accounts.",
            },
            "find_by_id": {
                "description": "Finds a user by primary key.",
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "The user, or None.",
                "errors": "DbErr on query failure.",
            },
            "is_email_registered": {
                "description": (
                    "Despite the name, returns whether the user's email has been verified "
                    "(the email_verified column)."
                ),
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "users.email_verified for that user.",
                "errors": "DbErr::Custom(\"User not found\") if the user does not exist, or other DbErr.",
            },
            "create_pending_user": {
                "description": (
                    "Inserts a new user with email_verified = false, no refresh token, empty "
                    "profile fields, level 1, xp 0, max_xp for level 1 (30), rank title "
                    "\"Weed Eater\" and empty friend lists."
                ),
                "params": {
                    "db": "Database connection.",
                    "email": "Trimmed email.",
                    "password_hash": "bcrypt hash of password + salt.",
                    "salt": "The per-user salt.",
                    "role": "Role to assign (User, or SuperAdmin via the Dev route).",
                    "created_at": "Creation timestamp from the app clock.",
                },
                "returns": "The inserted user::Model.",
                "errors": "DbErr, including a unique-constraint violation on email.",
            },
            "set_email_verified": {
                "description": "Sets users.email_verified for one user.",
                "params": {"db": "Database connection.", "user_id": "The user's id.", "value": "New value."},
                "returns": "UpdateResult (0 rows affected if the user does not exist).",
                "errors": "DbErr on failure.",
            },
            "set_refresh_token_hash": {
                "description": (
                    "Stores (or clears with None) the bcrypt hash of the user's current "
                    "refresh-token jti. Only one refresh token per user is valid at a time."
                ),
                "params": {
                    "db": "Database connection.",
                    "user_id": "The user's id.",
                    "refresh_token_hash": "bcrypt hash of the jti, or None to revoke.",
                },
                "returns": "UpdateResult.",
                "errors": "DbErr on failure.",
            },
            "set_last_login_at": {
                "description": "Sets users.last_login_at; called whenever tokens are issued (login and refresh).",
                "params": {
                    "db": "Database connection.",
                    "user_id": "The user's id.",
                    "last_login_at": "Timestamp from the app clock.",
                },
                "returns": "UpdateResult.",
                "errors": "DbErr on failure.",
            },
        },
    },
    "backend/src/features/auth/routes/mod.rs": {
        "summary": (
            "HTTP handlers and router for /auth/*: registration, login, token refresh, logout, "
            "email verification, password reset and the session check."
        ),
        "details": (
            "Public routes are wrapped in the rate_limit_auth middleware. /auth/email/verify and "
            "/auth/email/resend are only mounted when auth.require_email_verification is true "
            "(false in the default settings, so those routes return 404). /auth/session "
            "requires a Bearer access token. Dev-only routes are added by dev::map_routes_if_in_dev. "
            "In Dev mode, verification and password reset codes are echoed back in the JSON "
            "responses so testers do not need a mailbox; in production they are omitted."
        ),
        "symbols": {
            "auth_router": {
                "description": (
                    "Builds the auth router: session route behind require_auth, public routes "
                    "behind rate_limit_auth, optional email routes, then Dev routes."
                ),
                "params": {
                    "config": "Used to decide whether email verification routes are mounted.",
                    "state": "Application state for the middleware layers.",
                },
                "returns": "Router<AppState> for all /auth routes.",
            },
            "session": {
                "description": (
                    "GET /auth/session. Returns the caller's user id, email, first name and "
                    "whether their profile is complete (first name, last name and usage intent "
                    "set). Used by the app to restore a session and decide whether to show "
                    "onboarding."
                ),
                "params": {"user": "The authenticated caller.", "state": "Application state."},
                "returns": "200 with SessionResponse JSON.",
                "errors": "401 if the token is invalid or the user no longer exists.",
            },
            "register_start": {
                "description": (
                    "POST /auth/register/start. Creates a pending User-role account. If email "
                    "verification is disabled the account is immediately marked verified and "
                    "the user id is returned. Otherwise a 6-digit code (valid 2 minutes) is "
                    "generated and sent through the EmailSender."
                ),
                "params": {"state": "Application state.", "body": "RegisterRequest with email and password."},
                "returns": (
                    "200 with RegisterAttemptedResponse. user_id is always returned when "
                    "verification is disabled; when enabled, user_id and "
                    "email_verification_code are only returned in Dev."
                ),
                "errors": [
                    "400 - invalid email or password shorter than 8 characters",
                    "409 - email already taken",
                    "500 - failure creating or sending the verification code",
                    "429 - rate limit (10 per minute per IP, shared with login)",
                ],
                "notes": "Does not issue tokens; the client must call /auth/login afterwards.",
            },
            "login": {
                "description": "POST /auth/login. Verifies email/password and issues an access + refresh token pair.",
                "params": {"state": "Application state.", "body": "LoginRequest with email and password."},
                "returns": "200 with LoginResponse (access_token, refresh_token, user_id, email).",
                "errors": [
                    "401 \"invalid credentials\" - unknown email, wrong password, or unverified email",
                    "429 - rate limit",
                    "500 - database/hash/token errors",
                ],
            },
            "refresh": {
                "description": (
                    "POST /auth/refresh. Exchanges a valid refresh token for a new access + "
                    "refresh pair; the old refresh token is revoked (rotation)."
                ),
                "params": {"state": "Application state.", "body": "RefreshTokenRequest."},
                "returns": "200 with RefreshTokenResponse.",
                "errors": [
                    "401 \"invalid or expired refresh token\"",
                    "429 - rate limit (20 per minute per IP)",
                ],
            },
            "logout": {
                "description": (
                    "POST /auth/logout. Revokes the given refresh token if it is the user's "
                    "current one. Idempotent: invalid or already-revoked tokens still succeed."
                ),
                "params": {"state": "Application state.", "body": "RefreshTokenRequest."},
                "returns": "204 No Content.",
                "errors": "500 only on database or bcrypt errors.",
                "notes": (
                    "Access tokens are stateless and remain valid until they expire (15 minutes "
                    "by default) after logout. /auth/logout is not in a rate-limit bucket."
                ),
            },
            "verify_email": {
                "description": "POST /auth/email/verify. Verifies the 6-digit code and marks the email verified.",
                "params": {"state": "Application state.", "body": "VerifyEmailRequest with email and code."},
                "returns": "200 with VerifyEmailResponse { message: \"Email verified.\" }.",
                "errors": [
                    "400 - invalid email format, already verified, or invalid/expired code",
                    "429 - rate limit (5 per minute per IP)",
                ],
                "notes": "Only mounted when auth.require_email_verification is true.",
            },
            "resend_verification_email": {
                "description": (
                    "POST /auth/email/resend. If an unverified account exists, generates a new "
                    "code (replacing the old one) and sends it. Always returns the same generic "
                    "message to avoid revealing whether the account exists."
                ),
                "params": {"state": "Application state.", "body": "ResendVerificationEmailRequest."},
                "returns": (
                    "200 with ResendVerificationEmailResponse; email_verification_code is "
                    "populated only in Dev."
                ),
                "errors": ["500 - email sender failure", "429 - rate limit"],
                "notes": "Only mounted when auth.require_email_verification is true.",
            },
            "forgot_password": {
                "description": (
                    "POST /auth/password/forgot. If the account exists, creates a 6-digit reset "
                    "code valid for 15 minutes and sends it. Always returns a generic message."
                ),
                "params": {"state": "Application state.", "body": "ForgotPasswordRequest with email."},
                "returns": (
                    "200 with ForgotPasswordResponse; password_reset_code is populated only "
                    "in Dev."
                ),
                "errors": ["500 - email sender or database failure", "429 - rate limit (5 per minute per IP)"],
            },
            "reset_password": {
                "description": "POST /auth/password/reset. Sets a new password using a reset code.",
                "params": {"state": "Application state.", "body": "ResetPasswordRequest (email, code, new_password)."},
                "returns": "200 with ResetPasswordResponse message.",
                "errors": [
                    "400 - invalid email, password shorter than 8 characters, or invalid/expired code",
                    "429 - rate limit",
                ],
                "notes": "Revokes the user's refresh token, forcing a fresh login on other devices once access tokens expire.",
            },
        },
    },
    "backend/src/features/auth/routes/dev.rs": {
        "summary": (
            "Dev-only auth routes: password-less login and registration of a SuperAdmin "
            "account. They are not mounted when APP_ENV=production."
        ),
        "details": (
            "These routes are unauthenticated and not rate limited. They exist so that testers "
            "and automated tests can log in as any user and create privileged accounts quickly."
        ),
        "symbols": {
            "map_routes_if_in_dev": {
                "description": (
                    "Adds POST /auth/login/bypass and POST /auth/register/start/superadmin to "
                    "the router when is_dev() is true; otherwise returns the router unchanged."
                ),
                "params": {"router": "The auth router built so far."},
                "returns": "The router, possibly with Dev routes added.",
            },
            "login_bypass": {
                "description": (
                    "POST /auth/login/bypass. Issues tokens for the user with the given email "
                    "without checking the password or email verification."
                ),
                "params": {"state": "Application state.", "body": "LoginRequest; the password is ignored."},
                "returns": "200 with LoginResponse.",
                "errors": "401 \"invalid credentials\" if the email is unknown (or always, in production).",
            },
            "register_start_as_super_admin": {
                "description": (
                    "POST /auth/register/start/superadmin. Same flow as register_start but "
                    "creates the account with the SuperAdmin role."
                ),
                "params": {"state": "Application state.", "body": "RegisterRequest."},
                "returns": "200 with RegisterAttemptedResponse.",
                "errors": ["400 - invalid email or weak password", "409 - email taken", "500 - email failure"],
                "notes": "Duplicates the body of register_start rather than sharing it.",
            },
        },
    },
    "backend/src/features/auth/routes/errors.rs": {
        "summary": "Maps AuthError values to HTTP status codes and plain-text response bodies.",
        "symbols": {
            "AuthHttpError": (
                "Wrapper around a (StatusCode, String) pair returned by auth handlers. Rendered "
                "as a plain-text body with that status."
            ),
            "AuthHttpError::from [From<AuthError>]": {
                "description": (
                    "Maps each AuthError to a status and message: EmailTaken -> 409 \"email "
                    "already taken\"; InvalidCredentials and EmailNotVerified -> 401 \"invalid "
                    "credentials\"; InvalidRefreshToken -> 401 \"invalid or expired refresh "
                    "token\"; WeakPassword -> 400 \"password must be at least 8 characters\"; "
                    "InvalidEmail -> 400; EmailAlreadyVerified -> 400; InvalidVerificationCode "
                    "-> 400 \"invalid or expired verification code\"; InvalidPasswordResetCode "
                    "-> 400 \"invalid or expired password reset code\"; Token, Hash and "
                    "Database -> 500 \"internal server error\" (logged at error level)."
                ),
                "params": {"err": "The service-layer error."},
                "returns": "The corresponding AuthHttpError.",
                "notes": (
                    "The InvalidEmail message (\"email must be 3-64 chars (letters, digits, "
                    "underscore)\") does not describe the actual validation rule, which is a "
                    "standard email regex. EmailNotVerified deliberately returns the same 401 "
                    "as a wrong password, so the client cannot tell the user why login failed."
                ),
            },
            "AuthHttpError::into_response [IntoResponse]": {
                "description": "Renders the status code with the message as a plain-text body.",
                "returns": "An Axum Response.",
            },
        },
    },
    "backend/src/features/auth/service.rs": {
        "summary": (
            "Business logic for authentication: registration, login, JWT access/refresh token "
            "issuing with refresh-token rotation, logout, email verification and password reset."
        ),
        "details": (
            "Tokens are HS256 JWTs. Only one refresh token per user is valid at a time: the "
            "bcrypt hash of its jti is stored in users.refresh_token_hash and replaced on every "
            "login or refresh, so logging in on a second device invalidates the first device's "
            "refresh token. Email addresses are trimmed but not lower-cased. Password reset and "
            "email verification codes are 6-digit numbers, hashed with bcrypt, limited to 5 "
            "wrong attempts. All times come from the injectable Clock."
        ),
        "symbols": {
            "AccessTokenIssueSettings": (
                "Token settings derived from AuthConfig. Fields: jwt_secret, access_token_ttl "
                "and refresh_token_ttl (chrono Durations)."
            ),
            "AccessTokenIssueSettings::new_from_config": {
                "description": "Parses the TTL strings from the config with duration-str and copies the JWT secret.",
                "params": {"config": "The application configuration."},
                "returns": "The settings.",
                "errors": "Panics if either TTL string cannot be parsed.",
                "notes": "Called on every login/refresh/logout request rather than once at startup.",
            },
            "AuthError": (
                "Auth service error. Variants: EmailTaken, InvalidCredentials, "
                "InvalidRefreshToken, WeakPassword (shorter than 8 characters), InvalidEmail, "
                "Token (jsonwebtoken error), Database (DbErr), Hash (bcrypt error), "
                "EmailNotVerified, EmailAlreadyVerified, InvalidVerificationCode, "
                "InvalidPasswordResetCode. Mapped to HTTP by AuthHttpError."
            ),
            "AuthError::from [From<DbErr>]": {
                "description": "Wraps a database error as AuthError::Database.",
                "params": {"value": "The database error."},
                "returns": "AuthError::Database.",
            },
            "AuthError::from [From<bcrypt::BcryptError>]": {
                "description": "Wraps a bcrypt error as AuthError::Hash.",
                "params": {"value": "The bcrypt error."},
                "returns": "AuthError::Hash.",
            },
            "AuthError::from [From<jsonwebtoken::errors::Error>]": {
                "description": "Wraps a JWT error as AuthError::Token.",
                "params": {"value": "The JWT error."},
                "returns": "AuthError::Token.",
            },
            "AuthError::from [From<EmailVerificationError>]": {
                "description": (
                    "Converts email verification errors: Database and Hash are passed through; "
                    "NotFound, Expired and InvalidCode all become InvalidVerificationCode."
                ),
                "params": {"value": "The email verification error."},
                "returns": "The corresponding AuthError.",
            },
            "AuthTokenPair": "Private pair of freshly issued access_token and refresh_token strings.",
            "valid_email": {
                "description": (
                    "Checks the trimmed email against a simple case-insensitive regex "
                    "(local@domain.tld with a TLD of at least 2 letters) and a 320-character "
                    "maximum length."
                ),
                "params": {"email": "The email to check."},
                "returns": "true if the email looks valid.",
                "notes": "The regex is compiled on every call.",
            },
            "register_pending": {
                "description": (
                    "Validates the email and password length, checks the email is not taken, "
                    "generates a salt, hashes the password and creates an unverified user."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock for created_at.",
                    "body": "RegisterRequest with email and password.",
                    "role": "Role for the new account.",
                },
                "returns": "The new user's id.",
                "errors": [
                    "AuthError::InvalidEmail - email fails valid_email",
                    "AuthError::WeakPassword - password shorter than 8 bytes",
                    "AuthError::EmailTaken - an account with that exact email exists",
                    "AuthError::Hash / AuthError::Database - internal failures",
                ],
                "notes": "Writes a row to the users table. Does not send any email itself.",
            },
            "login_bypass": {
                "description": (
                    "Dev-only login that issues tokens for any existing email without checking "
                    "the password or verification status. Returns InvalidCredentials in "
                    "production as a second line of defence."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock.",
                    "body": "LoginRequest; password ignored.",
                    "settings": "Token settings.",
                },
                "returns": "LoginResponse with tokens.",
                "errors": "AuthError::InvalidCredentials if the email is unknown or in production.",
                "notes": "Rotates the stored refresh token hash and updates last_login_at like a normal login.",
            },
            "login": {
                "description": (
                    "Looks up the user by trimmed email, verifies the password, checks the email "
                    "is verified, then issues a new token pair."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock.",
                    "body": "LoginRequest.",
                    "settings": "Token settings.",
                },
                "returns": "LoginResponse (access_token, refresh_token, user_id, email).",
                "errors": [
                    "AuthError::InvalidCredentials - unknown email or wrong password",
                    "AuthError::EmailNotVerified - email not verified (shown to clients as 401 invalid credentials)",
                    "AuthError::Hash / Token / Database - internal failures",
                ],
                "notes": (
                    "Always requires a verified email, regardless of "
                    "require_email_verification; with verification disabled, registration "
                    "marks accounts verified so this passes. Replaces any previous refresh "
                    "token."
                ),
            },
            "refresh_tokens": {
                "description": (
                    "Validates a refresh token: non-empty, valid signature, typ \"refresh\", "
                    "not expired according to the app clock, user exists, and its jti matches "
                    "the stored bcrypt hash. Then clears the stored hash and issues a new pair "
                    "(refresh-token rotation)."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock.",
                    "body": "RefreshTokenRequest.",
                    "settings": "Token settings.",
                },
                "returns": "RefreshTokenResponse with the new tokens.",
                "errors": [
                    "AuthError::InvalidRefreshToken - any validation failure, including reuse of an already rotated token",
                    "AuthError::Hash / Token / Database - internal failures",
                ],
                "notes": (
                    "Reusing an old refresh token fails, but does not revoke the current one. "
                    "Test hint: advance the Dev clock past refresh_token_ttl to test expiry."
                ),
            },
            "logout": {
                "description": (
                    "Revokes the refresh token if it is valid and matches the stored hash. Any "
                    "invalid, expired, mismatched or empty token returns Ok without changes."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock.",
                    "body": "RefreshTokenRequest.",
                    "settings": "Token settings.",
                },
                "returns": "Ok(()) in all non-internal-error cases.",
                "errors": "AuthError::Database or AuthError::Hash on internal failures.",
            },
            "verify_email": {
                "description": (
                    "Validates the email format, finds the user, and if not yet verified checks "
                    "the code via email_server::service::verify_pending_email and sets "
                    "email_verified = true."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock.",
                    "body": "VerifyEmailRequest (email, code).",
                },
                "returns": "VerifyEmailResponse { message: \"Email verified.\" }.",
                "errors": [
                    "AuthError::InvalidEmail - bad email format",
                    "AuthError::InvalidVerificationCode - unknown user, no pending code, expired, or wrong code",
                    "AuthError::EmailAlreadyVerified - already verified",
                ],
            },
            "force_verify_email": {
                "description": "Marks the user's email verified without a code. Used when verification is disabled.",
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "Ok(()).",
                "errors": "AuthError::Database on failure.",
            },
            "prepare_verification_email_resend": {
                "description": (
                    "For a valid email belonging to an unverified user, creates a fresh "
                    "verification code (replacing any previous one). Returns None for invalid "
                    "emails, unknown users and already verified users (anti-enumeration)."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock.",
                    "body": "ResendVerificationEmailRequest.",
                },
                "returns": "Some(PendingEmailVerificationResponse) with the plaintext code, or None.",
                "errors": "AuthError::Database on failure.",
            },
            "user_id_from_token": {
                "description": (
                    "Decodes an access token, checks typ is \"access\" and that it has not "
                    "expired according to the app clock, and parses the subject as a user id."
                ),
                "params": {
                    "jwt_secret": "HS256 secret.",
                    "clock": "App clock (so the Dev clock offset affects expiry).",
                    "token": "The JWT.",
                },
                "returns": "The user id from the sub claim.",
                "errors": [
                    "AuthError::Token - bad signature or malformed token",
                    "AuthError::InvalidCredentials - wrong token type, expired, or non-numeric subject",
                ],
            },
            "issue_auth_tokens": {
                "description": (
                    "Issues an access and a refresh token, stores the bcrypt hash of the refresh "
                    "token's jti on the user (replacing any previous one) and updates "
                    "last_login_at."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock.",
                    "user": "The user to issue tokens for.",
                    "settings": "Token settings.",
                },
                "returns": "AuthTokenPair.",
                "errors": "AuthError::Token, Hash or Database.",
            },
            "login_response": {
                "description": "Builds a LoginResponse from a user and a token pair.",
                "params": {"user": "The logged-in user.", "tokens": "The issued tokens."},
                "returns": "LoginResponse.",
            },
            "generate_reset_code": {
                "description": "Generates a uniformly random 6-digit numeric code (zero padded) from the OS RNG.",
                "returns": "A string such as \"042917\".",
            },
            "prepare_password_reset": {
                "description": (
                    "For a valid, existing email: deletes expired resets, deletes the user's "
                    "previous reset, and stores a new hashed 6-digit code that expires in 15 "
                    "minutes. Returns None for invalid or unknown emails so the caller can "
                    "respond identically in both cases."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock.",
                    "body": "ForgotPasswordRequest.",
                },
                "returns": "Some(plaintext code) when a reset was created, otherwise None.",
                "errors": "AuthError::Database on failure.",
                "notes": "Works for unverified accounts too.",
            },
            "reset_password": {
                "description": (
                    "Validates the email and new password length, finds the pending reset, "
                    "checks expiry and the code. On a wrong code it increments attempts and "
                    "deletes the reset after 5 failures. On success it stores a new salt and "
                    "hash, clears the refresh token hash and deletes the reset."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock.",
                    "body": "ResetPasswordRequest (email, code, new_password).",
                },
                "returns": "ResetPasswordResponse with a success message.",
                "errors": [
                    "AuthError::InvalidEmail - bad email format",
                    "AuthError::WeakPassword - new password shorter than 8 characters",
                    "AuthError::InvalidPasswordResetCode - unknown user, no reset, expired, wrong code, or attempts exhausted",
                    "AuthError::Hash / Database - internal failures",
                ],
            },
        },
    },
    "backend/src/features/auth/tokens.rs": {
        "summary": "JWT creation and decoding, plus hashing of refresh-token ids for storage.",
        "details": (
            "Tokens are signed with HS256 using auth.jwt_secret. jsonwebtoken's own expiry "
            "check is disabled; callers compare exp to the app clock instead so the Dev clock "
            "offset applies. Each token carries a random 64-hex-character jti."
        ),
        "symbols": {
            "TOKEN_TYPE_ACCESS": "Value of the typ claim for access tokens: \"access\".",
            "TOKEN_TYPE_REFRESH": "Value of the typ claim for refresh tokens: \"refresh\".",
            "Claims": (
                "JWT payload. Fields: sub (user id as a string), exp (Unix expiry in seconds), "
                "typ (\"access\" or \"refresh\") and jti (random token id so tokens issued in "
                "the same second differ)."
            ),
            "generate_jti": {
                "description": "Generates 32 random bytes from the OS RNG, hex-encoded.",
                "returns": "A 64-character hex string.",
            },
            "decode_claims": {
                "description": "Verifies the HS256 signature and decodes the claims without checking exp.",
                "params": {"jwt_secret": "Signing secret.", "token": "The JWT string."},
                "returns": "The decoded Claims.",
                "errors": "jsonwebtoken error for malformed tokens or bad signatures.",
                "notes": "Callers must check exp and typ themselves.",
            },
            "issue_access_token": {
                "description": "Issues a token with typ \"access\".",
                "params": {
                    "jwt_secret": "Signing secret.",
                    "user_id": "Subject user id.",
                    "clock": "App clock used to compute exp.",
                    "ttl": "Lifetime (15 minutes in the default settings).",
                },
                "returns": "The encoded JWT.",
                "errors": "jsonwebtoken error on encoding failure.",
            },
            "issue_refresh_token": {
                "description": "Issues a token with typ \"refresh\".",
                "params": {
                    "jwt_secret": "Signing secret.",
                    "user_id": "Subject user id.",
                    "clock": "App clock used to compute exp.",
                    "ttl": "Lifetime (15 days in the default settings).",
                },
                "returns": "The encoded JWT.",
                "errors": "jsonwebtoken error on encoding failure.",
            },
            "issue_token": {
                "description": "Shared implementation: builds Claims with exp = now + ttl and a new jti, then signs them.",
                "params": {
                    "jwt_secret": "Signing secret.",
                    "user_id": "Subject user id.",
                    "clock": "App clock.",
                    "ttl": "Token lifetime.",
                    "typ": "Token type string.",
                },
                "returns": "The encoded JWT.",
                "errors": "jsonwebtoken error on encoding failure.",
            },
            "hash_refresh_token_jti": {
                "description": (
                    "bcrypt-hashes a refresh token's jti for storage. Only the jti is hashed, "
                    "because bcrypt ignores input past 72 bytes and full JWTs share long "
                    "identical prefixes."
                ),
                "params": {"jti": "The jti claim."},
                "returns": "The bcrypt hash.",
                "errors": "bcrypt::BcryptError.",
            },
            "verify_refresh_token_jti": {
                "description": "Checks a jti against the stored bcrypt hash.",
                "params": {
                    "jti": "The jti from the presented refresh token.",
                    "refresh_token_hash": "users.refresh_token_hash.",
                },
                "returns": "true if they match.",
                "errors": "bcrypt::BcryptError for a malformed stored hash.",
            },
        },
    },
    # ------------------------------------------------------------------
    # clock feature
    # ------------------------------------------------------------------
    "backend/src/features/clock/mod.rs": {
        "summary": "Clock feature root; declares the routes submodule for the Dev clock endpoints.",
    },
    "backend/src/features/clock/routes/mod.rs": {
        "summary": "Exposes clock_router, which contains only Dev-mode clock routes.",
        "symbols": {
            "clock_router": {
                "description": "Returns a router with the Dev clock routes in Dev mode, or an empty router in production.",
                "returns": "Router<AppState>.",
            },
        },
    },
    "backend/src/features/clock/routes/dev.rs": {
        "summary": (
            "Dev-only, unauthenticated endpoints to inspect, advance and reset the server's "
            "AppClock offset. Useful for testing token expiry, code expiry, daily quests and "
            "streaks without waiting."
        ),
        "details": (
            "The offset is global for the whole server process, so advancing it affects every "
            "user and every concurrent test. It is reset when the server restarts."
        ),
        "symbols": {
            "map_routes_if_in_dev": {
                "description": (
                    "Adds GET /dev/clock, POST /dev/clock/advance and POST /dev/clock/reset in "
                    "Dev mode; returns the router unchanged in production."
                ),
                "params": {"router": "The router to extend."},
                "returns": "The router.",
            },
            "get_clock": {
                "description": "GET /dev/clock. Returns the current shifted time and offset.",
                "params": {"state": "Application state."},
                "returns": "200 with ClockStatusResponse { now_utc (RFC 3339), offset_seconds }.",
            },
            "advance_clock": {
                "description": "POST /dev/clock/advance. Adds body.seconds to the clock offset.",
                "params": {"state": "Application state.", "body": "AdvanceClockRequest { seconds } (may be negative)."},
                "returns": "200 with the new ClockStatusResponse.",
                "errors": "400 Bad Request if the resulting offset exceeds 100 years or overflows.",
            },
            "reset_clock": {
                "description": "POST /dev/clock/reset. Sets the offset back to 0.",
                "params": {"state": "Application state."},
                "returns": "200 with ClockStatusResponse.",
            },
            "clock_status": {
                "description": "Builds a ClockStatusResponse from the state's clock.",
                "params": {"state": "Application state."},
                "returns": "ClockStatusResponse.",
            },
        },
    },
    # ------------------------------------------------------------------
    # db
    # ------------------------------------------------------------------
    "backend/src/features/db/mod.rs": {
        "summary": (
            "Database bootstrap: connects to the local SQLite database, runs SeaORM migrations "
            "and creates any missing tables from the entity models. Also contains the Dev-only "
            "database wipe."
        ),
        "details": (
            "Tables are created with CREATE TABLE IF NOT EXISTS from the entities; existing "
            "tables are never altered. After adding a column to a model, developers must "
            "delete the local SQLite file (backend/the_database.db by default) or the server "
            "will fail at query time. Only SQLite is supported."
        ),
        "symbols": {
            "ensure_user_table": {
                "description": "Creates the users table if missing.",
                "params": {"db": "Database connection."},
                "errors": "DbErr on failure.",
            },
            "ensure_email_verification_table": {
                "description": "Creates the email_verification table if missing.",
                "params": {"db": "Database connection."},
                "errors": "DbErr on failure.",
            },
            "ensure_user_plant_finds_table": {
                "description": "Creates the user_plant_finds table if missing.",
                "params": {"db": "Database connection."},
                "errors": "DbErr on failure.",
            },
            "ensure_table": {
                "description": "Generates a CREATE TABLE IF NOT EXISTS statement from a SeaORM entity and executes it.",
                "params": {"db": "Database connection.", "entity": "The entity to create a table for."},
                "errors": "DbErr on failure.",
                "notes": "Does not add new columns to an existing table.",
            },
            "ensure_password_reset_table": {
                "description": "Creates the password_reset table if missing.",
                "params": {"db": "Database connection."},
                "errors": "DbErr on failure.",
            },
            "ensure_tables": {
                "description": "Creates users, email_verification, password_reset and user_plant_finds tables if missing.",
                "params": {"db": "Database connection."},
                "errors": "DbErr on the first failure.",
            },
            "get_local_sqlite_database_connection": {
                "description": (
                    "Creates the SQLite file if it does not exist, connects with mode=rwc, runs "
                    "Migrator::up and then ensure_tables."
                ),
                "params": {"db_file_path": "Path of the SQLite file."},
                "returns": "The open DatabaseConnection.",
                "errors": "DbErr from migrations or table creation.",
                "notes": (
                    "Panics if the path has no file name, the file cannot be created, or the "
                    "connection fails. The connection URL is built from the file name only "
                    "(sqlite://<file name>), so the database is opened relative to the current "
                    "working directory even if db_path points to another directory."
                ),
            },
            "get_database_connection": {
                "description": "Opens the database described by config.db.local_sqlite.db_path.",
                "params": {"config": "Application configuration."},
                "returns": "The open DatabaseConnection.",
                "errors": "DbErr from get_local_sqlite_database_connection.",
                "notes": "Panics if db.local_sqlite is missing from the config.",
            },
            "erase_and_recreate_all_tables": {
                "description": (
                    "Dev-only: deletes all rows from user_plant_finds, password_reset, "
                    "email_verification and users (in that order). Despite the name, tables are "
                    "not dropped or recreated."
                ),
                "params": {"db": "Database connection."},
                "returns": "Ok(()) after all deletes.",
                "errors": "DbErr::Custom(\"Can't do that\") when not in Dev; other DbErr on failure.",
                "notes": "Scan image files in file storage are not deleted.",
            },
        },
    },
    "backend/src/features/db/models/mod.rs": {
        "summary": (
            "Declares the SeaORM entity modules: email_verification, password_reset, user and "
            "user_plant_finds."
        ),
    },
    "backend/src/features/db/models/email_verification.rs": {
        "summary": "SeaORM entity for the email_verification table holding pending email verification codes.",
        "symbols": {
            "Model": (
                "Row of email_verification. Fields: id (auto-increment primary key), user_id "
                "(unique, so at most one pending code per user), code_hash (bcrypt hash of the "
                "6-digit code), expires_at (2 minutes after creation), attempts (wrong guesses, "
                "max 5) and created_at."
            ),
            "Relation": "Empty relation enum; no SeaORM relations are declared for this table.",
        },
    },
    "backend/src/features/db/models/password_reset.rs": {
        "summary": "SeaORM entity for the password_reset table holding pending password reset codes.",
        "symbols": {
            "Model": (
                "Row of password_reset. Fields: id (auto-increment primary key), user_id "
                "(unique, one pending reset per user), code_hash (bcrypt hash of the 6-digit "
                "code), expires_at (15 minutes after creation), attempts (wrong guesses, max 5) "
                "and created_at."
            ),
            "Relation": "Empty relation enum; no SeaORM relations are declared for this table.",
        },
    },
    "backend/src/features/db/models/user.rs": {
        "summary": (
            "SeaORM entity for the users table, plus the level/XP curve and rank title helpers "
            "used by the XP system."
        ),
        "details": (
            "XP needed per level is level * 30 (30 for level 1, 60 for level 2, and so on). "
            "xp holds progress within the current level, not lifetime XP. The friend list "
            "columns exist but no friend feature is implemented yet."
        ),
        "symbols": {
            "UserIdType": "Type alias for user ids: i32.",
            "max_xp_needed_for_level": {
                "description": "Returns the XP required to finish the given level: level * 30.",
                "params": {"level": "The current level."},
                "returns": "XP threshold for leveling up from that level.",
            },
            "rank_title_for_level": {
                "description": (
                    "Maps a level to a rank title: 0 -> \"Hacker\", 1 -> \"Weed Eater\", 2-3 -> "
                    "\"Gardener\", 4 and above -> \"Plant Master\"."
                ),
                "params": {"level": "The level."},
                "returns": "The rank title string.",
            },
            "Model": (
                "Row of users. Fields: id (auto-increment primary key), email (unique), "
                "password_hash (bcrypt), created_at, email_verified, role (Role), salt "
                "(per-user hex salt), refresh_token_hash (bcrypt of the current refresh jti, or "
                "null when logged out), username (unused), first_name, last_name, usage_intent "
                "(one of USAGE_INTENT_OPTIONS after onboarding), last_login_at, level, "
                "rank_title, xp (progress within the level), max_xp (XP needed for the next "
                "level), friend_user_ids and pending_friend_user_ids (JSON arrays of user ids)."
            ),
            "Relation": "Relations of users. Variants: UserPlantFinds - has_many relation to user_plant_finds.",
            "Entity::to [Related<super::user_plant_finds::Entity>]": {
                "description": "SeaORM relation definition linking a user to their plant finds.",
                "returns": "The UserPlantFinds RelationDef.",
            },
            "StringVec": "JSON-serialized Vec<String> column wrapper. Currently not used by any column.",
            "UserIdVec": "JSON-serialized Vec<UserIdType> column wrapper used for the friend id lists.",
        },
    },
    "backend/src/features/db/models/user_plant_finds.rs": {
        "summary": (
            "SeaORM entity for the user_plant_finds table: one row per successful plant scan, "
            "with the stored OpenAI response and the image path."
        ),
        "symbols": {
            "Rarity": (
                "Database copy of the shared Rarity enum, stored as text. Variants: Common "
                "(\"common\"), Uncommon (\"uncommon\"), Rare (\"rare\"), SuperRare "
                "(\"super_rare\"), Exotic (\"exotic\")."
            ),
            "Rarity::from [From<RarityType>]": {
                "description": "Converts the shared server_types Rarity into the database Rarity.",
                "params": {"rarity": "The shared rarity."},
                "returns": "The database Rarity.",
            },
            "RarityType::from [From<Rarity>]": {
                "description": "Converts the database Rarity back into the shared server_types Rarity for API responses.",
                "params": {"rarity": "The database rarity."},
                "returns": "The shared Rarity.",
            },
            "Model": (
                "Row of user_plant_finds. Fields: id (auto-increment primary key, used as "
                "plant_id in /plant-scan/{plant_id}), user_id (owner), name (common name, or "
                "\"Unknown plant\"), scientific_name (may be empty), rarity (optional, as "
                "reported by the model), found_on (UTC calendar date of the scan), image_path "
                "(relative storage path such as scans/{user_id}/{uuid}.jpg) and scan_response "
                "(full PlantScan JSON from OpenAI)."
            ),
            "Relation": "Relations of user_plant_finds. Variants: User - belongs_to users via user_id.",
            "Entity::to [Related<super::user::Entity>]": {
                "description": "SeaORM relation definition linking a find to its user.",
                "returns": "The User RelationDef.",
            },
        },
    },
    # ------------------------------------------------------------------
    # dev
    # ------------------------------------------------------------------
    "backend/src/features/dev/mod.rs": {
        "summary": "Dev feature root; declares the routes submodule with general Dev-only endpoints.",
    },
    "backend/src/features/dev/routes.rs": {
        "summary": "Dev-only router containing the unauthenticated database wipe endpoint.",
        "symbols": {
            "dev_router": {
                "description": "Returns a router with POST /dev/erase-db in Dev mode, or an empty router in production.",
                "returns": "Router<AppState>.",
            },
            "erase_db": {
                "description": (
                    "POST /dev/erase-db. Deletes all rows from every table via "
                    "erase_and_recreate_all_tables."
                ),
                "params": {"state": "Application state."},
                "returns": "200 with an empty body on success.",
                "errors": "500 with the body \"I am error\" on failure.",
                "notes": (
                    "No authentication. Uploaded images remain on disk. Useful to reset state "
                    "between manual test runs."
                ),
            },
        },
    },
    # ------------------------------------------------------------------
    # email_server
    # ------------------------------------------------------------------
    "backend/src/features/email_server/mod.rs": {
        "summary": (
            "Email feature root. Declares the private repo module and the public sender_trait "
            "and service modules."
        ),
    },
    "backend/src/features/email_server/repo.rs": {
        "summary": "Database access for the email_verification table.",
        "details": "Mirrors auth::password_reset_repo. Codes are stored as bcrypt hashes.",
        "symbols": {
            "create_email": {
                "description": "Hashes the verification code with bcrypt and inserts a new row with attempts = 0.",
                "params": {
                    "db": "Database connection.",
                    "user_id": "The user to verify.",
                    "plain_text_code": "The 6-digit code.",
                    "created_at": "Creation timestamp.",
                    "expires_at": "Expiry timestamp.",
                },
                "returns": "The inserted email_verification::Model.",
                "errors": "DbErr (bcrypt failures are wrapped in DbErr::Custom).",
            },
            "find_by_user_id": {
                "description": "Finds the pending verification for a user.",
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "The row, or None.",
                "errors": "DbErr on failure.",
            },
            "delete_by_user_id": {
                "description": "Deletes any pending verification for the user.",
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "DeleteResult.",
                "errors": "DbErr on failure.",
            },
            "delete_expired": {
                "description": "Deletes all verification rows (for all users) with expires_at before now.",
                "params": {"db": "Database connection.", "now": "Current time from the app clock."},
                "returns": "DeleteResult.",
                "errors": "DbErr on failure.",
            },
            "increment_attempts": {
                "description": "Sets attempts to current_attempts + 1 (saturating).",
                "params": {
                    "db": "Database connection.",
                    "id": "Primary key of the row.",
                    "current_attempts": "Previously read attempts value.",
                },
                "returns": "The updated row.",
                "errors": "DbErr::Custom(\"email verification not found\") if missing, or other DbErr.",
            },
        },
    },
    "backend/src/features/email_server/sender_trait.rs": {
        "summary": (
            "Abstraction over sending emails, with a mock implementation that only logs. No "
            "real email provider is integrated yet."
        ),
        "details": (
            "main.rs always installs MockEmailSender, so verification and reset codes are only "
            "visible in the server log (warn level) and, in Dev, in the API responses."
        ),
        "symbols": {
            "EmailSenderStateType": "Alias for Arc<dyn EmailSender + Send + Sync>, the form stored in AppState.",
            "EmailSenderResult": "Alias for Result<T, EmailSenderError>.",
            "EmailSenderError": "Email sending error. Variants: SendFailed - the email could not be sent.",
            "EmailSender": "Async trait implemented by email backends; sends verification and password reset codes.",
            "EmailSender::send_verification_code": {
                "description": "Sends a 6-digit email verification code.",
                "params": {"to": "Recipient email.", "code": "The plaintext code."},
                "errors": "EmailSenderError::SendFailed.",
            },
            "EmailSender::send_password_reset_code": {
                "description": "Sends a 6-digit password reset code.",
                "params": {"to": "Recipient email.", "code": "The plaintext code."},
                "errors": "EmailSenderError::SendFailed.",
            },
            "MockEmailSender": "EmailSender that logs the code instead of sending it. Always succeeds.",
            "MockEmailSender::send_verification_code [EmailSender]": {
                "description": "Logs \"sent verification code {code} to {to} (not really)\" at warn level.",
                "params": {"to": "Recipient email.", "code": "The plaintext code."},
                "returns": "Ok(()).",
                "notes": "The plaintext code appears in the server logs.",
            },
            "MockEmailSender::send_password_reset_code [EmailSender]": {
                "description": "Logs \"sent password reset code {code} to {to} (not really)\" at warn level.",
                "params": {"to": "Recipient email.", "code": "The plaintext code."},
                "returns": "Ok(()).",
                "notes": "The plaintext code appears in the server logs.",
            },
        },
    },
    "backend/src/features/email_server/service.rs": {
        "summary": "Creates and checks email verification codes.",
        "details": (
            "Codes are 6 random digits, valid for 2 minutes, and invalidated after 5 wrong "
            "attempts. Creating a new code replaces the user's previous one."
        ),
        "symbols": {
            "EmailVerificationError": (
                "Verification error. Variants: Database (DbErr), Hash (bcrypt error), NotFound "
                "(no pending code), Expired (code past expires_at), InvalidCode (wrong code)."
            ),
            "EmailVerificationError::from [From<DbErr>]": {
                "description": "Wraps a database error as EmailVerificationError::Database.",
                "params": {"value": "The database error."},
                "returns": "EmailVerificationError::Database.",
            },
            "EmailVerificationError::from [From<bcrypt::BcryptError>]": {
                "description": "Wraps a bcrypt error as EmailVerificationError::Hash.",
                "params": {"value": "The bcrypt error."},
                "returns": "EmailVerificationError::Hash.",
            },
            "add_pending_email_verification": {
                "description": (
                    "Generates a new code, deletes expired verifications and the user's previous "
                    "one, and stores the hashed code with a 2 minute expiry."
                ),
                "params": {"db": "Database connection.", "clock": "App clock.", "user_id": "The user to verify."},
                "returns": "PendingEmailVerificationResponse containing the plaintext code (for sending).",
                "errors": "DbErr on failure.",
                "notes": "The 2 minute window is short; testers using a real inbox may need to resend.",
            },
            "verify_pending_email": {
                "description": (
                    "Deletes expired rows, loads the user's pending code, checks expiry and "
                    "compares the code with bcrypt. A wrong code increments attempts and deletes "
                    "the row once attempts reach 5. A correct code deletes the row."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock.",
                    "user_id": "The user's id.",
                    "plaintext_code": "The code the user entered (already trimmed by the caller).",
                },
                "returns": "Ok(()) when the code is correct.",
                "errors": [
                    "EmailVerificationError::NotFound - no pending code (including after expiry cleanup)",
                    "EmailVerificationError::Expired - code expired",
                    "EmailVerificationError::InvalidCode - wrong code",
                    "EmailVerificationError::Database / Hash - internal failures",
                ],
                "notes": "Does not itself set users.email_verified; auth::service::verify_email does that.",
            },
            "generate_verification_code": {
                "description": "Generates a random 6-digit, zero-padded numeric code from the OS RNG.",
                "returns": "The code as a string.",
            },
        },
    },
    # ------------------------------------------------------------------
    # file_storage
    # ------------------------------------------------------------------
    "backend/src/features/file_storage/mod.rs": {
        "summary": (
            "File storage feature root. Declares the errors, file_storage_trait and util "
            "modules and re-exports FileStorageError and FileStorageResult."
        ),
    },
    "backend/src/features/file_storage/errors.rs": {
        "summary": "Error and result types for file storage operations.",
        "symbols": {
            "FileStorageResult": "Alias for Result<T, FileStorageError>.",
            "FileStorageError": (
                "File storage error. Variants: EmptyPath - the relative path was empty; "
                "AbsolutePathNotAllowed - an absolute path was given; InvalidPathComponent { "
                "path } - the path contained \"..\", a root or a drive prefix (path traversal "
                "protection); Io - underlying std::io::Error."
            ),
        },
    },
    "backend/src/features/file_storage/file_storage_trait.rs": {
        "summary": (
            "The FileStorage trait for storing uploaded files by relative path, and "
            "LocalFileStorage, the local-disk implementation used by the server."
        ),
        "details": (
            "All paths are relative to a root directory configured by "
            "file_storage.local_file_storage_directory_path. resolve_path rejects empty paths, "
            "absolute paths and any \"..\" component, so callers cannot read or write outside "
            "the root. Symlinks inside the root are not checked. Scan images are stored under "
            "scans/{user_id}/{uuid}.{ext}."
        ),
        "symbols": {
            "FileStorageStateType": "Alias for Arc<dyn FileStorage + Send + Sync>, the form stored in AppState.",
            "FileStorage": "Async trait for a simple file store addressed by relative paths.",
            "FileStorage::create_dir_all": {
                "description": "Creates a directory and all missing parents.",
                "params": {"relative_path": "Directory path relative to the storage root."},
                "errors": "FileStorageError for invalid paths or IO failures.",
            },
            "FileStorage::directory_exists": {
                "description": "Returns whether a directory exists at the path.",
                "params": {"relative_path": "Path relative to the root."},
                "returns": "true if it exists and is a directory.",
                "errors": "FileStorageError for invalid paths or IO failures other than not-found.",
            },
            "FileStorage::file_exists": {
                "description": "Returns whether a regular file exists at the path.",
                "params": {"relative_path": "Path relative to the root."},
                "returns": "true if it exists and is a file.",
                "errors": "FileStorageError for invalid paths or IO failures other than not-found.",
            },
            "FileStorage::get_files_in_dir": {
                "description": "Lists the names of regular files (not directories) directly in a directory, sorted.",
                "params": {"relative_path": "Directory path relative to the root."},
                "returns": "Sorted file names.",
                "errors": "FileStorageError, including Io if the directory does not exist.",
            },
            "FileStorage::get_files_and_directories_in_dir": {
                "description": "Lists the names of all entries directly in a directory, sorted.",
                "params": {"relative_path": "Directory path relative to the root."},
                "returns": "Sorted entry names.",
                "errors": "FileStorageError, including Io if the directory does not exist.",
            },
            "FileStorage::delete_dir": {
                "description": "Recursively deletes a directory. Succeeds if it does not exist.",
                "params": {"relative_path": "Directory path relative to the root."},
                "errors": "FileStorageError for invalid paths or IO failures.",
            },
            "FileStorage::write_file_bytes": {
                "description": "Writes (overwrites) a file, creating parent directories.",
                "params": {"relative_path": "File path relative to the root.", "bytes": "Contents."},
                "errors": "FileStorageError for invalid paths or IO failures.",
            },
            "FileStorage::append_file_bytes": {
                "description": "Appends to a file, creating it and parent directories if needed.",
                "params": {"relative_path": "File path relative to the root.", "bytes": "Bytes to append."},
                "errors": "FileStorageError for invalid paths or IO failures.",
            },
            "FileStorage::delete_file": {
                "description": "Deletes a file. Succeeds if it does not exist.",
                "params": {"relative_path": "File path relative to the root."},
                "errors": "FileStorageError for invalid paths or IO failures.",
            },
            "FileStorage::read_file_bytes": {
                "description": "Reads a whole file into memory.",
                "params": {"relative_path": "File path relative to the root."},
                "returns": "The file contents.",
                "errors": "FileStorageError, including Io if the file does not exist.",
            },
            "LocalFileStorage": "FileStorage implementation backed by the local filesystem under a root directory (field root).",
            "LocalFileStorage::new": {
                "description": "Creates storage rooted at the given directory. The directory is not created or checked.",
                "params": {"root": "Root directory."},
                "returns": "LocalFileStorage.",
            },
            "LocalFileStorage::new_from_config": {
                "description": "Creates storage rooted at file_storage.local_file_storage_directory_path.",
                "params": {"config": "Application configuration."},
                "returns": "LocalFileStorage.",
                "errors": "Panics if local_file_storage_directory_path is not set.",
                "notes": "A relative root is resolved against the server's working directory.",
            },
            "LocalFileStorage::root": {
                "description": "Returns the root directory.",
                "returns": "The root path.",
            },
            "LocalFileStorage::resolve_path": {
                "description": (
                    "Validates a relative path and joins it to the root. Rejects empty paths, "
                    "absolute paths, and paths containing \"..\", a root or a Windows prefix "
                    "component."
                ),
                "params": {"relative_path": "Caller-supplied relative path."},
                "returns": "The absolute path inside the root.",
                "errors": [
                    "FileStorageError::EmptyPath",
                    "FileStorageError::AbsolutePathNotAllowed",
                    "FileStorageError::InvalidPathComponent",
                ],
                "notes": "This is the path traversal protection for all storage operations.",
            },
            "LocalFileStorage::create_dir_all [FileStorage]": {
                "description": "Resolves the path and calls tokio::fs::create_dir_all.",
                "params": {"relative_path": "Directory path relative to the root."},
                "errors": "FileStorageError.",
            },
            "LocalFileStorage::directory_exists [FileStorage]": {
                "description": "Resolves the path and checks metadata; not-found returns false.",
                "params": {"relative_path": "Path relative to the root."},
                "returns": "true if it is a directory.",
                "errors": "FileStorageError.",
            },
            "LocalFileStorage::file_exists [FileStorage]": {
                "description": "Resolves the path and checks metadata; not-found returns false.",
                "params": {"relative_path": "Path relative to the root."},
                "returns": "true if it is a regular file.",
                "errors": "FileStorageError.",
            },
            "LocalFileStorage::get_files_and_directories_in_dir [FileStorage]": {
                "description": "Reads the directory and returns all entry names that are valid UTF-8, sorted.",
                "params": {"relative_path": "Directory path relative to the root."},
                "returns": "Sorted names.",
                "errors": "FileStorageError.",
            },
            "LocalFileStorage::get_files_in_dir [FileStorage]": {
                "description": "Reads the directory and returns names of regular files that are valid UTF-8, sorted (hidden files included).",
                "params": {"relative_path": "Directory path relative to the root."},
                "returns": "Sorted file names.",
                "errors": "FileStorageError.",
            },
            "LocalFileStorage::delete_dir [FileStorage]": {
                "description": "Recursively removes the directory; not-found is treated as success.",
                "params": {"relative_path": "Directory path relative to the root."},
                "errors": "FileStorageError.",
            },
            "LocalFileStorage::write_file_bytes [FileStorage]": {
                "description": "Creates parent directories and writes the file, replacing existing contents.",
                "params": {"relative_path": "File path relative to the root.", "bytes": "Contents."},
                "errors": "FileStorageError.",
            },
            "LocalFileStorage::append_file_bytes [FileStorage]": {
                "description": "Creates parent directories, opens the file in create+append mode and writes the bytes.",
                "params": {"relative_path": "File path relative to the root.", "bytes": "Bytes to append."},
                "errors": "FileStorageError.",
            },
            "LocalFileStorage::delete_file [FileStorage]": {
                "description": "Removes the file; not-found is treated as success.",
                "params": {"relative_path": "File path relative to the root."},
                "errors": "FileStorageError.",
            },
            "LocalFileStorage::read_file_bytes [FileStorage]": {
                "description": "Reads the whole file.",
                "params": {"relative_path": "File path relative to the root."},
                "returns": "The file contents.",
                "errors": "FileStorageError (Io with NotFound if missing).",
            },
        },
    },
    "backend/src/features/file_storage/util/mod.rs": {
        "summary": "Helper for streaming a multipart upload field directly into file storage.",
        "details": "Not currently used by the plant scan route, which buffers the image in memory instead.",
        "symbols": {
            "MultipartReaderError": (
                "Error while streaming a multipart field. Variants: Axum (MultipartError while "
                "reading), IncorrectMultipartFormat (unused), Io (std::io::Error), Storage "
                "(FileStorageError)."
            ),
            "stream_field_to_storage": {
                "description": (
                    "Reads the field chunk by chunk; the first chunk is written with "
                    "write_file_bytes (overwriting any existing file) and later chunks are "
                    "appended."
                ),
                "params": {
                    "storage": "The file storage.",
                    "field": "The multipart field to read.",
                    "relative_path": "Destination path relative to the storage root.",
                },
                "returns": "Total number of bytes written.",
                "errors": "MultipartReaderError on read or storage failures.",
                "notes": (
                    "No size limit is enforced here. If the field is empty, no file is created. "
                    "A failure mid-stream leaves a partial file."
                ),
            },
        },
    },
    # ------------------------------------------------------------------
    # plant_scan
    # ------------------------------------------------------------------
    "backend/src/features/plant_scan/mod.rs": {
        "summary": (
            "Plant scan feature root. Declares the private daily, openai and repo modules and "
            "the public errors, routes and service modules, and re-exports plant_scan_router."
        ),
    },
    "backend/src/features/plant_scan/daily.rs": {
        "summary": (
            "The three hard-coded daily plant quests (MVP), XP reward constants and helpers for "
            "matching scan results to quests and comparing species."
        ),
        "details": (
            "XP rules: a scan of a species the user has never found before earns 10 XP; "
            "scanning one of today's daily plants earns a 20 XP bonus (once per daily plant per "
            "UTC day). Both can apply to the same scan (30 XP). Reference images for the quests "
            "live in backend/assets/daily_plants/ (ficus.jpg, lantanas.jpg, rosemary.jpg; png "
            "and webp also work). The daily list is the same every day."
        ),
        "symbols": {
            "NEW_SPECIES_XP": "XP awarded when a user scans a species they have not found before: 10.",
            "DAILY_BONUS_XP": "Bonus XP for finding one of the daily plants, at most once per plant per day: 20.",
            "DailyPlantDef": (
                "Definition of a daily quest plant. Fields: key (stable id and image file "
                "name), common_name, scientific_name and aliases (lower-case substrings that "
                "count as a match)."
            ),
            "DAILY_PLANTS": (
                "The three daily quest plants: ficus (Ficus Tree, Ficus benjamina, alias "
                "\"ficus\"), lantanas (Lantanas, Lantana camara, alias \"lantana\") and rosemary "
                "(Rosemary, Salvia rosmarinus, aliases \"rosemary\", \"rosmarinus\", \"salvia "
                "rosmarinus\")."
            ),
            "normalize_name": {
                "description": (
                    "Lower-cases ASCII letters, removes characters that are not alphanumeric "
                    "or whitespace, and collapses runs of whitespace to single spaces."
                ),
                "params": {"value": "Any plant name."},
                "returns": "The normalized name, possibly empty.",
            },
            "match_daily_plant": {
                "description": (
                    "Normalizes \"common_name scientific_name\" and returns the first daily plant "
                    "whose alias appears as a substring."
                ),
                "params": {
                    "common_name": "Common name from the scan, if any.",
                    "scientific_name": "Scientific name from the scan, if any.",
                },
                "returns": "The matching DailyPlantDef, or None.",
                "notes": (
                    "Substring matching is generous: any Ficus species (for example Ficus "
                    "elastica) or any Lantana species counts as the daily plant."
                ),
            },
            "species_key": {
                "description": (
                    "Returns the normalized scientific name, or the normalized common name when "
                    "the scientific name is empty. Used to decide whether a find is a new species."
                ),
                "params": {"common_name": "Common name.", "scientific_name": "Scientific name."},
                "returns": "The comparison key.",
            },
            "daily_plants_dir": {
                "description": "Returns <crate dir>/assets/daily_plants, using the compile-time CARGO_MANIFEST_DIR.",
                "returns": "The directory path.",
                "notes": "Because the path is baked in at compile time, a binary moved to another machine will not find the images.",
            },
            "find_daily_image_path": {
                "description": "Looks for {key}.jpg, .jpeg, .png or .webp (in that order) in daily_plants_dir.",
                "params": {"key": "The daily plant key."},
                "returns": "The first existing file, or None.",
            },
            "image_mime_from_path": {
                "description": "Guesses an image MIME type from the file extension: png, webp, gif, otherwise image/jpeg.",
                "params": {"path": "The file path."},
                "returns": "A MIME type string.",
            },
        },
    },
    "backend/src/features/plant_scan/errors.rs": {
        "summary": "Error type for the plant scan feature and its mapping to HTTP responses.",
        "symbols": {
            "PlantScanError": (
                "Plant scan error. Variants: MissingApiKey (no OpenAI key configured), "
                "MissingImage (empty upload), ImageTooLarge (over 10 MiB), NotAPlant (model "
                "said is_plant false, or returned no names), NotFound (no find with that id for "
                "this user), ScanResponseNotFound (find has no stored response), OpenAi(String) "
                "(request/timeout failure - also used for GBIF failures), InvalidModelResponse "
                "(model output was not valid PlantScan JSON), InvalidStoredResponse(String), "
                "Database, Storage and Io."
            ),
            "PlantScanHttpError": "Wrapper around a (StatusCode, String) pair, rendered as a plain-text response.",
            "PlantScanHttpError::from [From<PlantScanError>]": {
                "description": (
                    "Logs the error and maps it: MissingApiKey -> 503 \"plant scanning is not "
                    "configured\"; MissingImage -> 400 \"image is required\"; ImageTooLarge -> "
                    "400 \"image is too large\"; NotAPlant -> 422 \"could not identify a plant "
                    "in that photo\"; NotFound and ScanResponseNotFound -> 404 \"plant scan not "
                    "found\"; InvalidStoredResponse -> 500; InvalidModelResponse and OpenAi -> "
                    "502 \"failed to analyze the plant\"; Database, Storage, Io -> 500 "
                    "\"internal server error\"."
                ),
                "params": {"err": "The service error."},
                "returns": "The PlantScanHttpError.",
                "notes": "Every plant scan error is logged at error level, including expected ones like NotAPlant and NotFound.",
            },
            "PlantScanHttpError::into_response [IntoResponse]": {
                "description": "Renders the status code with the message as a plain-text body.",
                "returns": "An Axum Response.",
            },
        },
    },
    "backend/src/features/plant_scan/openai.rs": {
        "summary": (
            "Calls the OpenAI Chat Completions API (via the async-openai crate) with the photo "
            "and a system prompt, and parses the JSON identification result."
        ),
        "symbols": {
            "SYSTEM_PROMPT": (
                "System prompt instructing the model to identify the most prominent plant, "
                "avoid overclaiming certainty, set is_plant false for non-plant photos, and "
                "return only a JSON object with is_plant, identification (common_name, "
                "scientific_name, family, confidence High/Medium/Low, rarity "
                "Common/Uncommon/Rare/SuperRare/Exotic), summary, sections (appearance, "
                "native_range, care, interesting_facts, toxicity) and identification_notes. "
                "This schema must stay in sync with the PlantScan type in server_types."
            ),
            "identify_plant": {
                "description": (
                    "Base64-encodes the image into a data URL, sends a chat completion request "
                    "with JSON-object response format, the system prompt and the image (detail "
                    "auto), waits up to 90 seconds, and deserializes the first choice's content "
                    "into PlantScan."
                ),
                "params": {
                    "api_key": "OpenAI API key.",
                    "model": "Model name, gpt-4o by default.",
                    "image_bytes": "Raw image bytes.",
                    "mime": "Image MIME type from the upload, used in the data URL.",
                },
                "returns": "The parsed PlantScan.",
                "errors": [
                    "PlantScanError::OpenAi - request build failure, API error, network error, or 90 second timeout",
                    "PlantScanError::InvalidModelResponse - no content, or JSON that does not match PlantScan",
                ],
                "notes": (
                    "Makes a paid external API call. The raw model output is logged at error "
                    "level when parsing fails. A new HTTP client is created for every call."
                ),
            },
        },
    },
    "backend/src/features/plant_scan/repo.rs": {
        "summary": "Database queries for plant finds, the recent-finds feed and the leaderboard.",
        "symbols": {
            "RecentFindUser": (
                "Partial user model joined into the recent finds query. Fields: id (used to "
                "tell a user with no names from a missing joined row), first_name, last_name."
            ),
            "insert_find": {
                "description": "Serializes the PlantScan to JSON and inserts a user_plant_finds row.",
                "params": {
                    "db": "Database connection.",
                    "user_id": "Owner of the find.",
                    "name": "Common name.",
                    "scientific_name": "Scientific name (may be empty).",
                    "rarity": "Rarity from the model, if any.",
                    "found_on": "UTC date of the scan.",
                    "image_path": "Relative storage path of the image.",
                    "scan": "The full model response to store.",
                },
                "returns": "The inserted row.",
                "errors": "DbErr (JSON serialization failures wrapped as DbErr::Custom).",
            },
            "list_by_user": {
                "description": "Lists all finds for a user, newest first (by found_on, then id).",
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "The finds.",
                "errors": "DbErr on failure.",
            },
            "list_by_user_on_date": {
                "description": "Lists a user's finds on a specific date.",
                "params": {"db": "Database connection.", "user_id": "The user's id.", "found_on": "The date."},
                "returns": "The finds (unordered).",
                "errors": "DbErr on failure.",
            },
            "find_by_id": {
                "description": "Finds a find by id, only if it belongs to the given user.",
                "params": {"db": "Database connection.", "user_id": "The owner.", "plant_id": "The find's id."},
                "returns": "The find, or None (also None for other users' finds).",
                "errors": "DbErr on failure.",
            },
            "list_recent": {
                "description": (
                    "Lists finds from all users, newest first (found_on, then id), with "
                    "offset/limit paging, joined with the owner's first and last name. "
                    "Optionally excludes one user's finds."
                ),
                "params": {
                    "db": "Database connection.",
                    "count": "Maximum rows (LIMIT).",
                    "offset": "Rows to skip (OFFSET).",
                    "user_exclude": "User id whose finds should be excluded, typically the caller.",
                },
                "returns": "Pairs of (find, optional user name info).",
                "errors": "DbErr on failure.",
                "notes": "Uses manual A_/B_ column aliases so SeaORM can split the joined row into two models.",
            },
            "get_users_by_xp": {
                "description": "Lists all users ordered by the xp column, descending.",
                "params": {"db": "Database connection."},
                "returns": "All user rows.",
                "errors": "DbErr on failure.",
                "notes": (
                    "Ordering uses xp, which is progress within the current level and resets on "
                    "level-up, so a higher-level user can rank below a lower-level one. The "
                    "columns() call does not restrict the selection, so full rows (including "
                    "password hashes) are loaded, although only safe fields are returned to "
                    "clients. There is no limit and users without names are included."
                ),
            },
        },
    },
    "backend/src/features/plant_scan/routes.rs": {
        "summary": (
            "HTTP handlers for scanning plants, the home screen, collection details, map "
            "locations, recent finds, the leaderboard and GBIF distribution lookups. All routes "
            "require a Bearer access token."
        ),
        "symbols": {
            "MAX_IMAGE_BYTES": (
                "Maximum upload size for POST /plant-scan: 10 MiB (10 * 1024 * 1024). Used as "
                "the request body limit and to check the image field."
            ),
            "RecentFindsQuery": (
                "Query parameters for GET /recent-finds. Fields: count (required, page size), "
                "offset (required), user_exclude (optional user id to omit)."
            ),
            "plant_scan_router": {
                "description": (
                    "Builds the router for /plant-scan (POST, 10 MiB body limit), "
                    "/plant-scan/{plant_id}, /plant-image-locations, /home, "
                    "/plant-geo-distribution/{scientific_name}, /recent-finds and /leaderboard, "
                    "all behind require_auth."
                ),
                "params": {"state": "Application state for the auth middleware."},
                "returns": "Router<AppState>.",
            },
            "get_plant_geo_distribution": {
                "description": (
                    "GET /plant-geo-distribution/{scientific_name}. Proxies a GBIF occurrence "
                    "search for the species and returns the parsed response."
                ),
                "params": {"scientific_name": "URL path segment with the scientific name."},
                "returns": "200 with GbifResponse JSON.",
                "errors": "502 \"failed to analyze the plant\" on any GBIF failure (mapped through PlantScanError::OpenAi).",
            },
            "retrieve_find": {
                "description": "GET /plant-scan/{plant_id}. Returns the stored identification for one of the caller's finds.",
                "params": {"user": "Authenticated caller.", "state": "Application state.", "plant_id": "Find id."},
                "returns": "200 with PlantScan JSON.",
                "errors": ["404 - not found or owned by another user", "500 - stored JSON invalid"],
            },
            "plant_image_locations": {
                "description": (
                    "GET /plant-image-locations. Returns, for each of the caller's finds with "
                    "an image, the GPS location from EXIF (if any) and a thumbnail."
                ),
                "params": {"user": "Authenticated caller.", "state": "Application state."},
                "returns": "200 with a list of UserPlantImageLocation.",
                "errors": "500 on database or storage failures.",
            },
            "home": {
                "description": "GET /home. Returns the home screen data: name, level, XP and the daily quests.",
                "params": {"user": "Authenticated caller.", "state": "Application state."},
                "returns": "200 with HomeResponse JSON.",
                "errors": "500 on database errors (including a deleted user).",
            },
            "get_recent_finds": {
                "description": "GET /recent-finds?count=&offset=&user_exclude=. Returns a page of recent finds from all users.",
                "params": {"state": "Application state.", "params": "Parsed RecentFindsQuery."},
                "returns": "200 with a list of RecentFind (find with base64 image plus the finder's name).",
                "errors": "400 if count or offset is missing or not a number; 500 on database errors.",
                "notes": "count is not capped, and every image is embedded as base64, so large pages produce large responses.",
            },
            "scan_plant": {
                "description": (
                    "POST /plant-scan (multipart). Reads the first field named \"image\", taking "
                    "the file extension from its file name (default jpg) and its content type "
                    "(default image/jpeg), then calls service::scan_plant_image."
                ),
                "params": {
                    "user": "Authenticated caller.",
                    "state": "Application state.",
                    "multipart": "The multipart body; other fields are ignored.",
                },
                "returns": "200 with PlantScanResult (scan, xp_awarded, is_new_species, daily_match, leveled_up).",
                "errors": [
                    "400 - invalid multipart body, unreadable field, image too large, or no image field",
                    "413 - body exceeds the 10 MiB limit before the handler runs",
                    "422 - not a plant",
                    "502 - OpenAI failure or invalid model output",
                    "503 - OpenAI API key not configured",
                ],
                "notes": (
                    "Because the body limit includes multipart overhead, an image just under "
                    "10 MiB can still be rejected. Can take tens of seconds (OpenAI timeout is 90s)."
                ),
            },
            "get_leaderboard": {
                "description": "GET /leaderboard. Returns all users ordered by xp descending.",
                "params": {"state": "Application state."},
                "returns": "200 with a list of LeaderboardUser (id, first_name, last_name, xp, level, rank_title).",
                "errors": "500 on database errors.",
            },
        },
    },
    "backend/src/features/plant_scan/service.rs": {
        "summary": (
            "Core plant scan logic: identifying an uploaded photo with OpenAI, saving the find "
            "and image, awarding XP and levels, and building the home, profile, map, recent "
            "finds and leaderboard data."
        ),
        "details": (
            "Depends on openai.rs for identification, daily.rs for quests and XP constants, "
            "repo.rs for persistence and FileStorage for images. \"Today\" is the UTC date from "
            "the app clock, so quests reset at midnight UTC rather than local midnight. Images "
            "are returned to clients as base64 data URLs inline in JSON."
        ),
        "symbols": {
            "MAX_IMAGE_BYTES": "Service-level image size limit: 10 MiB. Duplicates the constant in routes.rs.",
            "resolve_openai_settings": {
                "description": (
                    "Returns the OpenAI API key (config openai.api_key, else the OPENAI_API_KEY "
                    "environment variable; blank counts as missing) and the model (openai.model, "
                    "else gpt-4o)."
                ),
                "params": {"config": "Application configuration."},
                "returns": "(api_key, model).",
                "errors": "PlantScanError::MissingApiKey if no non-blank key is available.",
            },
            "scan_plant_image": {
                "description": (
                    "End-to-end scan. Steps: 1) reject empty or over-10-MiB images; 2) resolve "
                    "OpenAI settings and call identify_plant; 3) reject results with is_plant "
                    "false or with no names; 4) use the common name (default \"Unknown plant\") "
                    "and scientific name; 5) decide whether the species is new for the user "
                    "(species_key against all previous finds); 6) check whether it matches a "
                    "daily plant not already found today; 7) compute XP (10 for a new species "
                    "plus 20 for a daily match); 8) save the image to "
                    "scans/{user_id}/{uuid}.{ext}; 9) insert the find row; 10) apply XP and "
                    "level-ups."
                ),
                "params": {
                    "db": "Database connection.",
                    "clock": "App clock (determines today's date).",
                    "storage": "File storage for the image.",
                    "config": "Configuration for OpenAI settings.",
                    "user_id": "The scanning user.",
                    "image_bytes": "Raw image bytes.",
                    "mime": "Image MIME type.",
                    "extension": "File extension for the stored file (leading dot stripped).",
                },
                "returns": "PlantScanResult with scan, xp_awarded, is_new_species, daily_match and leveled_up.",
                "errors": [
                    "PlantScanError::MissingImage - no bytes",
                    "PlantScanError::ImageTooLarge - over 10 MiB",
                    "PlantScanError::MissingApiKey - OpenAI not configured",
                    "PlantScanError::OpenAi / InvalidModelResponse - identification failed",
                    "PlantScanError::NotAPlant - not a plant",
                    "PlantScanError::Storage / Database - persistence failures",
                ],
                "notes": (
                    "Writes an image file and a database row on every successful scan, even "
                    "when 0 XP is awarded (repeat species). The steps are not transactional: if "
                    "the insert fails after the image is written, the file is orphaned. Rejected "
                    "scans (not a plant) save nothing."
                ),
            },
            "retrieve_find": {
                "description": "Loads one of the user's finds and deserializes its stored scan_response.",
                "params": {"db": "Database connection.", "user_id": "Owner.", "plant_id": "Find id."},
                "returns": "The stored PlantScan.",
                "errors": [
                    "PlantScanError::NotFound - no such find for this user",
                    "PlantScanError::ScanResponseNotFound - find has no stored response",
                    "PlantScanError::InvalidStoredResponse - stored JSON no longer parses",
                ],
            },
            "apply_xp": {
                "description": (
                    "Adds XP to the user and levels up while xp >= max_xp, carrying the "
                    "remainder over (max_xp = level * 30). Updates xp, level, max_xp and "
                    "rank_title."
                ),
                "params": {"db": "Database connection.", "user_id": "The user.", "awarded": "XP to add."},
                "returns": "true if the user's level increased.",
                "errors": "PlantScanError::Database (including user not found).",
                "notes": "A stored level of 0 is treated as 1. Read-modify-write without a transaction.",
            },
            "get_home": {
                "description": (
                    "Builds the home screen: first name, level, rank title, xp, max_xp and one "
                    "quest per daily plant with found (matched a find today), xp_reward 20 and "
                    "the reference image as a data URL."
                ),
                "params": {
                    "db": "Database connection.",
                    "storage": "File storage (currently unused).",
                    "clock": "App clock (today's date).",
                    "user_id": "The user.",
                },
                "returns": "HomeResponse.",
                "errors": "PlantScanError::Database.",
                "notes": "Quest rarity is always Common. Reference images are read from disk on every request.",
            },
            "load_daily_image_base64": {
                "description": "Reads a daily plant's reference image from assets/daily_plants and returns it as a data URL.",
                "params": {"plant": "The daily plant."},
                "returns": "A data:<mime>;base64,... string, or None if the image is missing or unreadable.",
            },
            "get_profile": {
                "description": (
                    "Builds the profile: names, joined date (RFC 3339), rank (level, current "
                    "and next rank title, xp, xp_to_next), stats (scan count, unique species, "
                    "streak days) and the full collection with base64 images."
                ),
                "params": {
                    "db": "Database connection.",
                    "storage": "File storage for images.",
                    "clock": "App clock for the streak.",
                    "user_id": "The user.",
                },
                "returns": "ProfileResponse.",
                "errors": "PlantScanError::Database.",
                "notes": (
                    "Used by GET /user/me. Missing image files are logged and returned as null "
                    "images. Every image is loaded on each call, so large collections make this "
                    "response heavy."
                ),
            },
            "get_user_plant_image_locations": {
                "description": (
                    "For each of the user's finds with an existing image file, reads EXIF GPS "
                    "coordinates and, when present, generates a 320x240 JPEG thumbnail."
                ),
                "params": {"db": "Database connection.", "storage": "File storage.", "user_id": "The user."},
                "returns": "List of UserPlantImageLocation (image_id, common_name, location or null, thumbnail or null).",
                "errors": "PlantScanError::Storage or Database.",
                "notes": "Finds without GPS data are still returned, with location and thumbnail set to null.",
            },
            "get_plant_geo_distributition": {
                "description": (
                    "Queries GBIF (https://api.gbif.org/v1/occurrence/search) for up to 300 "
                    "occurrences of the scientific name that have coordinates, and parses the "
                    "JSON into GbifResponse."
                ),
                "params": {"scientific_name": "Scientific name to search for."},
                "returns": "GbifResponse.",
                "errors": "PlantScanError::OpenAi for every failure (network, HTTP status, body or JSON).",
                "notes": (
                    "The function name is misspelled (distributition). GBIF errors reuse the "
                    "OpenAi variant, so they show up as 502 \"failed to analyze the plant\" and "
                    "as \"openai request failed\" in logs. No timeout is set on the request."
                ),
            },
            "get_recent_finds": {
                "description": "Loads a page of recent finds from all users and attaches base64 images and the finder's names.",
                "params": {
                    "db": "Database connection.",
                    "storage": "File storage.",
                    "count": "Page size.",
                    "offset": "Rows to skip.",
                    "user_exclude": "Optional user id to exclude.",
                },
                "returns": "List of RecentFind.",
                "errors": "PlantScanError::Database.",
            },
            "get_leaderboard": {
                "description": "Maps all users (ordered by xp) to LeaderboardUser; missing names become empty strings.",
                "params": {"db": "Database connection."},
                "returns": "List of LeaderboardUser.",
                "errors": "PlantScanError::Database.",
            },
            "image_thumbnail_data_url": {
                "description": "Decodes the image, scales it to fit within 320x240 and re-encodes it as JPEG.",
                "params": {"image_bytes": "Original image bytes."},
                "returns": "A data:image/jpeg;base64,... string, or None if decoding or encoding fails.",
            },
            "read_image_geolocation": {
                "description": (
                    "Reads EXIF GPS latitude/longitude (tolerating partially corrupt EXIF) and "
                    "converts them to signed decimal degrees."
                ),
                "params": {"image_bytes": "Image bytes."},
                "returns": "ImageGeolocation, or None if GPS data is missing or invalid.",
                "notes": "Covered by an inline unit test using an iOS photo fixture located in Chicago.",
            },
            "read_exif_coordinate": {
                "description": (
                    "Reads one coordinate and its reference tag (N/S or E/W), applies the sign "
                    "and validates the range."
                ),
                "params": {
                    "exif": "Parsed EXIF data.",
                    "coordinate_tag": "GPSLatitude or GPSLongitude.",
                    "reference_tag": "GPSLatitudeRef or GPSLongitudeRef.",
                    "positive_reference": "Reference value for positive degrees (N or E).",
                    "negative_reference": "Reference value for negative degrees (S or W).",
                    "maximum_degrees": "90 for latitude, 180 for longitude.",
                },
                "returns": "Signed decimal degrees, or None if missing, malformed or out of range.",
            },
            "absolute_degrees_from_exif": {
                "description": (
                    "Converts an EXIF value to degrees: three rationals as degrees/minutes/"
                    "seconds (rejecting zero denominators or minutes/seconds >= 60), a single "
                    "rational, a single float or a single double."
                ),
                "params": {"value": "The EXIF value."},
                "returns": "Unsigned degrees, or None.",
            },
            "trim_exif_ascii": {
                "description": "Strips a trailing NUL byte from an EXIF ASCII value.",
                "params": {"value": "Raw ASCII bytes."},
                "returns": "The bytes without the trailing NUL.",
            },
            "format_found_on": {
                "description": "Formats a date as full month name and zero-padded day, for example \"July 04\".",
                "params": {"date": "The find date."},
                "returns": "The formatted string (no year).",
            },
            "compute_streak": {
                "description": (
                    "Counts consecutive days with at least one find, ending today and going "
                    "backwards. Future-dated finds are skipped."
                ),
                "params": {"finds": "All of the user's finds.", "today": "Today's date from the app clock."},
                "returns": "The streak length in days.",
                "notes": "If the user has not scanned anything today the streak is 0, even if they scanned every previous day.",
            },
        },
    },
    # ------------------------------------------------------------------
    # user
    # ------------------------------------------------------------------
    "backend/src/features/user/mod.rs": {
        "summary": (
            "User feature root. Declares the private errors and repo modules and the public "
            "routes and service modules."
        ),
    },
    "backend/src/features/user/errors.rs": {
        "summary": "Maps user service errors and database errors to HTTP responses.",
        "symbols": {
            "UserHttpError": "Wrapper around a (StatusCode, String) pair, rendered as a plain-text response.",
            "UserHttpError::from [From<DbErr>]": {
                "description": "Maps DbErr::RecordNotFound to 404 \"user not found\" and every other DbErr to 500 \"internal server error\".",
                "params": {"err": "The database error."},
                "returns": "The UserHttpError.",
            },
            "UserHttpError::from [From<UserError>]": {
                "description": "Maps InvalidProfile to 400 \"invalid profile data\", NotFound to 404 \"user not found\", and Database via the DbErr mapping.",
                "params": {"err": "The service error."},
                "returns": "The UserHttpError.",
            },
            "UserHttpError::into_response [IntoResponse]": {
                "description": "Renders the status code with the message as a plain-text body.",
                "returns": "An Axum Response.",
            },
        },
    },
    "backend/src/features/user/repo.rs": {
        "summary": "Basic CRUD queries on the users table for the user feature.",
        "symbols": {
            "find_by_email": {
                "description": "Finds a user by exact email.",
                "params": {"db": "Database connection.", "email": "The email."},
                "returns": "The user, or None.",
                "errors": "DbErr on failure.",
            },
            "get_all_users": {
                "description": "Returns every user row. Currently unused.",
                "params": {"db": "Database connection."},
                "returns": "All users.",
                "errors": "DbErr on failure.",
            },
            "create_user": {
                "description": "Inserts a user from an ActiveModel. Currently unused; registration uses auth::repo.",
                "params": {"db": "Database connection.", "user": "The ActiveModel to insert."},
                "returns": "The inserted user.",
                "errors": "DbErr on failure.",
            },
            "update_user": {
                "description": "Saves the changed fields of a user ActiveModel.",
                "params": {"db": "Database connection.", "user": "The ActiveModel with changes set."},
                "returns": "The updated user.",
                "errors": "DbErr on failure.",
            },
            "delete_user": {
                "description": "Deletes a user by id.",
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "DeleteResult.",
                "errors": "DbErr on failure.",
            },
            "find_by_id": {
                "description": "Finds a user by id.",
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "The user, or None.",
                "errors": "DbErr on failure.",
            },
        },
    },
    "backend/src/features/user/routes/mod.rs": {
        "summary": (
            "HTTP handlers for /user/*: completing the onboarding profile, fetching the "
            "caller's profile, and the super-admin delete endpoint."
        ),
        "symbols": {
            "user_router": {
                "description": (
                    "Builds the user router: /user/profile/complete and /user/me behind "
                    "require_auth, /user/delete behind require_super_admin_auth, plus Dev routes."
                ),
                "params": {"state": "Application state for the middleware."},
                "returns": "Router<AppState>.",
            },
            "delete_user": {
                "description": "POST /user/delete. Deletes the user with the given email. SuperAdmin only.",
                "params": {"state": "Application state.", "body": "DeleteUserRequest { email }."},
                "returns": "200 with an empty body.",
                "errors": ["401/403 - not a verified SuperAdmin", "404 - no user with that email", "500 - database error"],
            },
            "complete_profile": {
                "description": "POST /user/profile/complete. Saves the caller's first name, last name and usage intent.",
                "params": {
                    "user": "Authenticated caller.",
                    "state": "Application state.",
                    "body": "CompleteProfileRequest.",
                },
                "returns": "200 with CompleteProfileResponse { success: true }.",
                "errors": ["400 - empty names or unknown usage intent", "404 - user not found"],
            },
            "me": {
                "description": "GET /user/me. Returns the caller's full profile via plant_scan::service::get_profile.",
                "params": {"user": "Authenticated caller.", "state": "Application state."},
                "returns": "200 with ProfileResponse JSON.",
                "errors": "500 on database errors (errors use the plant scan error mapping).",
            },
        },
    },
    "backend/src/features/user/routes/dev.rs": {
        "summary": "Dev-only user route for changing any account's role without authentication.",
        "symbols": {
            "map_routes_if_in_dev": {
                "description": "Adds POST /user/change-role/bypass in Dev mode; returns the router unchanged in production.",
                "params": {"router": "The router to extend."},
                "returns": "The router.",
            },
            "change_role_bypass": {
                "description": "POST /user/change-role/bypass. Sets the role of the user with the given email.",
                "params": {"state": "Application state.", "body": "ChangeRoleRequest { email, role }."},
                "returns": "200 with ChangeRoleResponse { success: true }.",
                "errors": ["404 - no user with that email", "500 - database error"],
                "notes": "Unauthenticated; useful for testing the super-admin delete route.",
            },
        },
    },
    "backend/src/features/user/service.rs": {
        "summary": "User business logic: profile completion rules, lookups, role changes and deletion.",
        "symbols": {
            "USAGE_INTENT_OPTIONS": (
                "Allowed values for usage_intent during onboarding (exact, case-sensitive): "
                "\"Just for fun\", \"Learning\", \"Gardening\", \"Work or school\"."
            ),
            "UserError": (
                "User service error. Variants: Database (DbErr), InvalidProfile (empty names "
                "or usage intent not in USAGE_INTENT_OPTIONS), NotFound (user does not exist)."
            ),
            "UserError::from [From<DbErr>]": {
                "description": "Wraps a database error as UserError::Database.",
                "params": {"value": "The database error."},
                "returns": "UserError::Database.",
            },
            "is_profile_complete": {
                "description": "Returns true when first_name, last_name and usage_intent are all non-blank.",
                "params": {"user": "The user row."},
                "returns": "Whether onboarding is complete.",
            },
            "delete_user_with_email": {
                "description": "Finds a user by trimmed email and deletes the row.",
                "params": {"db": "Database connection.", "email": "Email of the account to delete."},
                "returns": "Ok(()).",
                "errors": "DbErr::RecordNotFound if no such user, or other DbErr.",
                "notes": (
                    "Only the users row is deleted explicitly. Related rows in user_plant_finds, "
                    "email_verification and password_reset, and the user's image files, are not "
                    "cleaned up by this function."
                ),
            },
            "get_user_by_id": {
                "description": "Loads a user by id, treating a missing user as an error.",
                "params": {"db": "Database connection.", "user_id": "The user's id."},
                "returns": "The user row.",
                "errors": "DbErr::RecordNotFound(\"User not found\") or other DbErr.",
                "notes": "Used by the auth middleware on every authenticated request.",
            },
            "change_role": {
                "description": "Finds a user by trimmed email and sets their role.",
                "params": {"db": "Database connection.", "email": "Target email.", "role": "New role."},
                "returns": "Ok(()).",
                "errors": "DbErr::RecordNotFound if no such user, or other DbErr.",
            },
            "complete_profile": {
                "description": (
                    "Trims and validates the onboarding fields (non-empty names, usage intent in "
                    "USAGE_INTENT_OPTIONS) and saves them on the user."
                ),
                "params": {
                    "db": "Database connection.",
                    "user_id": "The caller.",
                    "body": "CompleteProfileRequest (first_name, last_name, usage_intent).",
                },
                "returns": "CompleteProfileResponse { success: true }.",
                "errors": [
                    "UserError::InvalidProfile - empty name or unknown usage intent",
                    "UserError::NotFound - user missing",
                    "UserError::Database - database failure",
                ],
                "notes": "Can be called again later to change the values; there is no length limit on names.",
            },
        },
    },
}
