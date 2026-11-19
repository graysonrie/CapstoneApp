"""Document-level prose: introduction, architecture, and build/run/test instructions.

Content blocks used by ``SETUP_SECTIONS`` and ``INTRODUCTION_SECTIONS``:
    ("p", text)                    paragraph
    ("bullets", [text, ...])       bulleted list
    ("steps", [text, ...])         numbered list
    ("code", text)                 monospace block
    ("table", [headers], [[row]])  table
"""

TITLE = "Leaf Freak"
SUBTITLE = "External Code Documentation"

INTRODUCTION_SECTIONS = [
    {
        "heading": "Purpose",
        "blocks": [
            (
                "p",
                "This document describes the Leaf Freak source code at the file level and at the "
                "function and method level. It explains what each part of the system does, how the "
                "parts call each other, and what inputs, outputs and errors to expect, so that "
                "programmers, support engineers and test engineers can understand and work with the "
                "code without reading all of it first.",
            ),
            (
                "p",
                "Leaf Freak is a mobile game in the spirit of Pokemon Go: instead of catching "
                "creatures, players go outside, photograph plants and earn experience points (XP). "
                "Each day the app presents a set of daily plants to find. A photo is sent to the "
                "backend, which asks an OpenAI vision model to identify the plant, stores the find, "
                "awards XP and returns a detailed description of the plant.",
            ),
        ],
    },
    {
        "heading": "Audience",
        "blocks": [
            (
                "bullets",
                [
                    "Programmers: use the Architecture Overview and Module Reference to find where "
                    "behaviour lives and how to change it safely.",
                    "Support engineers: use the HTTP API Reference and the error descriptions to map "
                    "a user-visible message or status code back to the code path that produced it.",
                    "Test engineers: use the API and Tauri command references for inputs and expected "
                    "outputs, the notes on each function for edge cases, and the Test Reference for "
                    "existing automated coverage and how to run it.",
                ],
            ),
        ],
    },
    {
        "heading": "Scope",
        "blocks": [
            (
                "p",
                "Documented in full: the Axum backend server (backend/src), the shared crates "
                "server_types and tb_client, the Tauri shell (src-tauri/src), the Rust side of the "
                "custom camera plugin, the Next.js frontend (src, except the generated shadcn/ui "
                "primitives), and the automated tests.",
            ),
            (
                "p",
                "Listed only: the shadcn/ui primitive components in src/components/ui (Appendix A). "
                "Not covered: the database migration crate, the generated Android and iOS projects, "
                "native Kotlin/Swift sources, generated TypeScript bindings (src/generated), "
                "configuration files other than those described in the setup chapter, and lockfiles.",
            ),
        ],
    },
    {
        "heading": "How to Read This Document",
        "blocks": [
            (
                "bullets",
                [
                    "All file paths are relative to the repository root.",
                    "Each file section starts with its path, language, size and purpose, followed by a "
                    "table of the types and constants it defines and then one entry per function, "
                    "method, React component, hook or store action.",
                    "Function entries show the signature exactly as written in the source, the line "
                    "number where it starts, a description, and where relevant a parameter table, "
                    "the return value, the errors it can produce and additional notes.",
                    "Rust methods are written as Type::method. Methods that implement a trait add the "
                    "trait in brackets, for example AuthError::from [From<DbErr>]. TypeScript functions "
                    "declared inside a component are written Component.inner, and zustand store "
                    "actions are written useStore.action.",
                    "Signatures, parameters, routes and Tauri commands are extracted from the source "
                    "code each time the document is generated. Items with no hand-written description "
                    "are marked Undocumented and listed in Appendix B.",
                ],
            ),
        ],
    },
]

ARCHITECTURE_INTRO = [
    (
        "p",
        "Leaf Freak is split into the layers shown in Figure 1 and the table below. The user "
        "interface is a Next.js React application that "
        "is statically exported and hosted inside a Tauri v2 native shell, which is packaged as an "
        "iOS app (desktop and Android builds also work). The frontend never calls the backend over "
        "HTTP itself: it invokes Tauri commands, and the Rust side of the shell performs the HTTP "
        "requests through the tb_client crate. The backend is an Axum web server that stores data "
        "in SQLite through SeaORM, stores uploaded photos on the local file system, and calls the "
        "OpenAI API for plant identification and the GBIF API for plant distribution data.",
    ),
]

AREA_INTROS = {
    "Backend Server": (
        "The Axum web server in backend/src. main.rs loads configuration, builds AppState and "
        "merges the feature routers. Each feature under backend/src/features keeps HTTP handlers "
        "in routes, business logic in service and database access in repo. Database entities "
        "live in features/db/models."
    ),
    "Shared Crates": (
        "server_types defines the request and response structs shared by the backend and its "
        "clients. tb_client is the typed HTTP client used by the Tauri shell and by the "
        "tb_client integration tests."
    ),
    "Tauri Shell": (
        "The native application shell in src-tauri/src. It registers plugins, creates the shared "
        "ApiClient, restores the saved session from the OS keyring and exposes the Tauri commands "
        "the frontend invokes."
    ),
    "Camera Plugin": (
        "The Rust side of the custom tauri-plugin-camera crate. On iOS/Android it forwards "
        "take_photo and take_pending_photo to the native implementation. On desktop, where there "
        "is no native camera, take_photo opens an image file picker instead and "
        "take_pending_photo always returns nothing."
    ),
    "Frontend": (
        "The Next.js application in src. Routes are folders under src/app, each with a page.tsx. "
        "Feature-specific hooks, stores, types and components live under src/features; shared "
        "components, hooks and helpers live under src/components, src/hooks and src/lib."
    ),
}

ARCHITECTURE_LAYERS = [
    (
        "Frontend (Next.js / React)",
        "src/",
        "Pages under src/app (one folder per route), feature modules under src/features, shared "
        "components, hooks and utilities. Server state is cached with TanStack React Query; local "
        "UI state lives in zustand stores. Calls the backend only through the generated bindings in "
        "src/generated/commands.ts, which wrap Tauri invoke().",
    ),
    (
        "Tauri shell (Rust)",
        "src-tauri/",
        "Creates the native window/webview, registers plugins (file system, OS, dialog, store, log, "
        "camera, iOS safe-area insets) and exposes the #[tauri::command] functions in "
        "tauri_exports.rs. Holds a single shared tb_client ApiClient and persists the refresh token "
        "in the operating system keyring so users stay signed in.",
    ),
    (
        "Camera plugin (Rust + Swift/Kotlin)",
        "src-tauri/crates/tauri-plugin-camera/",
        "A custom Tauri plugin that opens the native camera on iOS/Android and returns the path of "
        "the captured photo (on desktop it opens an image file picker instead). It can also "
        "recover a photo that was taken while the app was suspended (take_pending_photo).",
    ),
    (
        "tb_client and server_types (Rust crates)",
        "backend/crates/",
        "tb_client is a typed reqwest HTTP client for the backend, grouped into per-feature clients "
        "(auth, user, plant scan, clock, dev, misc). It manages access and refresh tokens and turns "
        "HTTP errors into ClientError values with user-facing messages. server_types holds the "
        "request and response structs shared by the backend and the client, so both sides agree on "
        "the JSON format.",
    ),
    (
        "Backend server (Axum)",
        "backend/src/",
        "Feature modules under backend/src/features (auth, user, plant_scan, email_server, "
        "file_storage, clock, db, dev), each split into routes (HTTP handlers), service (business "
        "logic) and repo (database queries). Shared state (database connection, file storage, email "
        "sender, clock, config, rate limiter) is passed to handlers through AppState.",
    ),
    (
        "External services",
        "",
        "OpenAI (plant identification via async-openai, model gpt-4o by default), GBIF occurrence "
        "search (plant distribution map data), MapTiler (map tiles, called directly by the frontend "
        "map components), SQLite database file, and the local scan image directory.",
    ),
]

# Boxes for the generated architecture diagram: (id, label, column, row).
DIAGRAM_NODES = [
    ("frontend", "Next.js frontend\n(src/)", 0, 1),
    ("tauri", "Tauri shell\n(src-tauri/)", 1, 1),
    ("camera", "Camera plugin\n(native camera)", 1, 0),
    ("client", "tb_client\n(HTTP client)", 2, 1),
    ("keyring", "OS keyring\n(refresh token)", 2, 0),
    ("backend", "Axum backend\n(backend/src/)", 3, 1),
    ("sqlite", "SQLite\n(SeaORM)", 4, 0),
    ("files", "Scan images\n(local storage)", 4, 1),
    ("openai", "OpenAI API\n(identification)", 4, 2),
    ("gbif", "GBIF API\n(distribution)", 3, 2),
    ("maptiler", "MapTiler\n(map tiles)", 0, 2),
]

DIAGRAM_EDGES = [
    ("frontend", "tauri", "invoke()"),
    ("frontend", "camera", "takePhoto()"),
    ("tauri", "client", "Rust calls"),
    ("tauri", "keyring", "save/load token"),
    ("client", "backend", "HTTP + JWT"),
    ("backend", "sqlite", ""),
    ("backend", "files", ""),
    ("backend", "openai", ""),
    ("backend", "gbif", ""),
    ("frontend", "maptiler", "HTTPS"),
]

REQUEST_EXAMPLE_HEADING = "Example: What Happens When a User Scans a Plant"
REQUEST_EXAMPLE_STEPS = [
    "The user taps Scan in the mobile navigation bar. The frontend calls takePhoto() in "
    "src/lib/camera.ts, which invokes the camera plugin and receives the local path of the photo.",
    "The path and the page the user came from are saved in the zustand scan store (useScanStore) "
    "and in sessionStorage, so the scan can resume if the webview reloads, and the user is taken to "
    "the /plant_screenshot page, which shows a progress bar while the scan runs.",
    "That page calls the scanPlant binding, which invokes the scan_plant Tauri command. The command "
    "reads the file, works out its MIME type and calls PlantScanClient::scan_plant in tb_client.",
    "tb_client sends POST /plant-scan as a multipart upload with the access token in the "
    "Authorization header (120 second timeout).",
    "The backend's require_auth middleware validates the JWT. The scan_plant handler reads the "
    "'image' field (10 MiB limit) and calls service::scan_plant_image.",
    "The service sends the image to OpenAI with a structured-output prompt, rejects images that are "
    "not plants, checks whether the species is new for the user and whether it matches one of "
    "today's daily plants, saves the image and a user_plant_finds row, and adds XP (10 for a new "
    "species, 20 for a daily plant), levelling the user up if needed.",
    "The PlantScanResult JSON travels back through tb_client and the Tauri command (which adds the "
    "image as a data URL). The frontend stores the result in useScanStore, refreshes the cached "
    "home and profile queries, and the plant analysis page shows the identification, care "
    "details, toxicity, distribution map and XP awarded. On failure a toast is shown and the user "
    "is returned to the page they started from.",
]

SETUP_SECTIONS = [
    {
        "heading": "Prerequisites",
        "blocks": [
            (
                "bullets",
                [
                    "Rust toolchain (edition 2024 support, so Rust 1.85 or newer) with cargo.",
                    "Node.js and pnpm (the repository pins pnpm 11 through the packageManager field).",
                    "Tauri v2 prerequisites for your platform; Xcode and the iOS simulator or a device "
                    "for iOS builds.",
                    "An OpenAI API key for plant identification.",
                ],
            ),
        ],
    },
    {
        "heading": "Running the Backend",
        "blocks": [
            (
                "p",
                "The backend reads backend/appsettings.ron and then applies environment variable "
                "overrides with the prefix APP and the separator __ (for example "
                "APP__server__port=4000). A .env file in the working directory is loaded first if "
                "present. Run it from the backend directory so relative paths resolve:",
            ),
            ("code", "cd backend\nOPENAI_API_KEY=sk-... cargo run"),
            (
                "p",
                "By default the server listens on 127.0.0.1:3001, uses the SQLite file "
                "backend/the_database.db (tables are created automatically on start-up) and stores "
                "scan images under TEST_LOCAL_SERVER/ at the repository root. To let a physical "
                "iPhone reach the server, bind to all interfaces; in the dev environment this also "
                "requires explicitly allowing insecure dev mode:",
            ),
            ("code", "APP__server__host=0.0.0.0 APP_ALLOW_INSECURE_DEV=1 cargo run"),
            (
                "p",
                "Unless APP_ENV=production is set, the server runs in the dev environment and mounts "
                "unauthenticated helper routes (login bypass, super-admin registration, role change, "
                "database erase and clock control). In production the server refuses to start with "
                "the default JWT secret.",
            ),
            (
                "p",
                "The default test account mentioned in the README is testuser@test.com with the "
                "password 'password' (it must exist in the database you are using).",
            ),
        ],
    },
    {
        "heading": "Running the App",
        "blocks": [
            ("p", "Install the frontend dependencies once, then start the Tauri app in development mode:"),
            ("code", "pnpm install\npnpm tauri dev"),
            (
                "p",
                "tauri dev runs pnpm dev (Next.js on port 3000) and opens a 390 x 844 window that "
                "imitates a phone. For iOS, the README recommends a production build opened in Xcode, "
                "because animations and some behaviour only work reliably in that build:",
            ),
            ("code", "pnpm tauri ios build --open"),
            (
                "p",
                "The backend URL used by the app is compiled in. It comes from the BACKEND_URL "
                "environment variable at build time; without it, iOS builds use a hardcoded LAN "
                "address (http://192.168.1.54:3001) and other platforms use http://127.0.0.1:3001. "
                "Set BACKEND_URL to your machine's address when testing on a device.",
            ),
        ],
    },
    {
        "heading": "Running the Tests",
        "blocks": [
            (
                "bullets",
                [
                    "Backend unit and integration tests: cd backend && cargo test. The integration "
                    "tests in backend/src/tests start an in-process test server with its own SQLite "
                    "file, so nothing else needs to be running. Filter with a test path, for example "
                    "cargo test tests::login::test_log_in.",
                    "tb_client unit tests: cd backend && cargo test -p tb_client --lib.",
                    "tb_client integration tests (backend/crates/tb_client/tests): these currently do "
                    "not compile, because they import addin_server_interactor, a crate left over from "
                    "another project. Once fixed, they need a backend running in the dev environment "
                    "at http://127.0.0.1:3001 with email verification enabled, they erase its "
                    "database, and they must run with --test-threads=1. Never point them at a real "
                    "server.",
                    "Frontend: pnpm test (Vitest in watch mode) or pnpm test:run. Vitest is configured "
                    "but the repository currently contains no frontend test files.",
                    "Lint: pnpm lint for the frontend; cargo clippy in backend/ or src-tauri/ for Rust.",
                ],
            ),
            ("p", "See the Test Reference chapter for what each existing test covers."),
        ],
    },
    {
        "heading": "Regenerating Bindings and This Document",
        "blocks": [
            (
                "p",
                "The TypeScript bindings in src/generated are produced by tauri-typegen from the "
                "#[tauri::command] functions. Regenerate them after changing a command signature:",
            ),
            ("code", "cd src-tauri\ncargo tauri-typegen generate"),
            (
                "p",
                "This document is produced by claudes_stuff/generate_external_code_doc.py. The script "
                "parses the source on every run, so signatures, routes and commands are always "
                "current; descriptions live in claudes_stuff/doc_content/. Use --check to list "
                "undocumented or stale items after changing code:",
            ),
            (
                "code",
                "cd claudes_stuff\n"
                "python3 -m venv env && env/bin/pip install -r requirements.txt\n"
                "env/bin/python generate_external_code_doc.py\n"
                "env/bin/python generate_external_code_doc.py --check",
            ),
        ],
    },
]

ENV_VARS_HEADERS = ["Variable", "Used by", "Default", "Description"]
ENV_VARS = [
    [
        "APP_ENV",
        "Backend",
        "(unset = dev)",
        "Set to 'production' to run in the production environment. Anything else, including "
        "unset, means dev, which mounts the dev-only routes and returns verification and reset "
        "codes in API responses.",
    ],
    [
        "APP__<section>__<key>",
        "Backend",
        "appsettings.ron",
        "Overrides any appsettings.ron value, for example APP__server__host, APP__server__port, "
        "APP__auth__jwt_secret, APP__openai__model.",
    ],
    [
        "APP_ALLOW_INSECURE_DEV",
        "Backend",
        "off",
        "Set to 1 or true to allow a dev-environment server to bind to a non-loopback host. "
        "Without it the server refuses to start, because dev routes are unauthenticated.",
    ],
    [
        "OPENAI_API_KEY",
        "Backend",
        "none",
        "OpenAI key, used when openai.api_key is not set in the config. Scans fail with a "
        "missing-key error if neither is set.",
    ],
    [
        "RUST_LOG",
        "Backend",
        "debug",
        "tracing filter for server logs (tracing_subscriber EnvFilter).",
    ],
    [
        "BACKEND_URL",
        "Tauri shell (build time)",
        "see Running the App",
        "Backend base URL compiled into the app with option_env!.",
    ],
    [
        "TAURI_DEV_HOST",
        "Next.js config",
        "localhost",
        "Host used for the dev asset prefix when developing on a physical device.",
    ],
]

CONFIG_KEYS_HEADERS = ["Key (appsettings.ron)", "Default", "Description"]
CONFIG_KEYS = [
    ["server.host / server.port", "127.0.0.1 / 3001", "Address the backend binds to."],
    [
        "auth.jwt_secret",
        "change-me",
        "Secret used to sign JWTs. Must be changed for production (start-up fails otherwise).",
    ],
    ["auth.access_token_ttl", "15m", "Lifetime of access tokens."],
    ["auth.refresh_token_ttl", "15d", "Lifetime of refresh tokens."],
    [
        "auth.require_email_verification",
        "false",
        "When true, new accounts must verify an emailed code and the /auth/email/* routes are "
        "mapped. Emails are currently only logged by MockEmailSender.",
    ],
    ["db.url", "(empty)", "Database URL used when local SQLite is disabled."],
    [
        "db.local_sqlite.enabled / db_path",
        "true / ./the_database.db",
        "Use a local SQLite file (relative to the backend working directory).",
    ],
    [
        "file_storage.use_local_file_storage / local_file_storage_directory_path",
        "true / ../TEST_LOCAL_SERVER",
        "Root directory for stored scan images (scans/<user_id>/<uuid>.<ext>).",
    ],
    ["openai.api_key", "None", "OpenAI key; falls back to OPENAI_API_KEY."],
    ["openai.model", "gpt-4o", "OpenAI model used for identification."],
]

CONFIG_NOTES = [
    "The MapTiler API key used by the map and plant analysis pages is hardcoded in "
    "src/app/map/page.tsx and src/app/plant_analysis/page.tsx rather than read from configuration.",
    "The daily plants (ficus, lantanas, rosemary) are hardcoded in "
    "backend/src/features/plant_scan/daily.rs; their reference images are loaded from "
    "backend/assets/daily_plants.",
]

API_INTRO = [
    (
        "p",
        "The backend exposes a JSON HTTP API, by default at http://127.0.0.1:3001. Request and "
        "response bodies are the structs in backend/crates/server_types; field names are snake_case "
        "unless noted. The routes below are extracted from the router definitions in the code, so "
        "the list always matches the build the document was generated from.",
    ),
    (
        "bullets",
        [
            "Authentication: protected routes require an 'Authorization: Bearer <access token>' "
            "header. Access tokens come from /auth/login (or /auth/refresh) and expire after "
            "auth.access_token_ttl (15 minutes by default). A missing, invalid or expired token "
            "returns 401 with an empty body.",
            "Errors: failures return an HTTP status code with a short plain-text body, for example "
            "400 'image is required'. The Tauri app shows that text to the user as-is "
            "(ClientError::user_message), so the message on screen identifies the backend error "
            "directly.",
            "Rate limiting: login/register (10 per minute), refresh (20 per minute), email "
            "verification (5 per minute) and password reset (5 per minute) are limited per client IP "
            "and return 429 when exceeded.",
            "Dev-only routes are mounted only when APP_ENV is not 'production'. They are "
            "unauthenticated and must never be reachable on a public network.",
        ],
    ),
]

TAURI_INTRO = [
    (
        "p",
        "The frontend talks to the backend only through Tauri commands. Each command is a Rust "
        "function marked #[tauri::command] in "
        "src-tauri/src/services/backend_api_service/tauri_exports.rs and registered in "
        "src-tauri/src/commands/tauri_registry.rs. tauri-typegen generates a typed TypeScript "
        "wrapper for each one in src/generated/commands.ts; for example getHome() calls "
        "invoke('get_home').",
    ),
    (
        "bullets",
        [
            "Arguments are passed as one object with camelCase keys, for example "
            "getRecentFinds({ count, offset, userExclude }).",
            "Every command returns a Promise. On failure the Promise rejects with a plain string "
            "that is safe to show to the user (the backend's error text, 'Unable to reach the "
            "server', or 'You are not signed in').",
            "All commands share one ApiClient instance, which holds the access token in memory and "
            "the refresh token in memory and in the OS keyring.",
            "The backend endpoints column is derived from the code: it follows each command into "
            "the tb_client methods it calls and reads the URL each method requests.",
        ],
    ),
]

TESTS_INTRO = [
    (
        "p",
        "Automated tests exist for the backend and the tb_client crate. Integration tests in "
        "backend/src/tests run against an in-process server; the tests in "
        "backend/crates/tb_client/tests are written to run against a separately started dev "
        "server but do not currently compile (see the notes on each file). Unit tests "
        "are also embedded in some source files (inline tests modules). Each test is listed below "
        "with what it verifies and any preconditions.",
    ),
]
