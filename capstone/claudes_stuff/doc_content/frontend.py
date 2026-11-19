"""Hand-written descriptions for the Next.js frontend under src/."""

FILES: dict[str, dict] = {
    # ------------------------------------------------------------------
    # src/app - routes (Next.js app router, static export)
    # ------------------------------------------------------------------
    "src/app/layout.tsx": {
        "summary": (
            "Root layout shared by every route. It loads the web fonts, sets the "
            "mobile viewport, and wraps all pages in the theme provider, the "
            "TanStack Query provider, the floating Scan button, the pending-scan "
            "recovery watcher and the toast container."
        ),
        "details": (
            "Imports globals.css and the MapTiler SDK stylesheet once for the "
            "whole app. Page content is rendered in a flex column that pads the "
            "top by the iOS safe-area inset and the bottom by 5rem plus the "
            "bottom safe-area inset so content is never hidden behind the fixed "
            "Scan button. The desktop AdaptiveWindowChrome title bar is present "
            "but commented out, so it is never rendered."
        ),
        "symbols": {
            "tangerine": (
                "Brand font registered as the CSS variable --font-brand. Despite "
                "the name it loads Fredoka, not Tangerine; the Tangerine import "
                "is unused."
            ),
            "manropeHeading": (
                "Heading font registered as --font-heading. Despite the name it "
                "also loads Fredoka, not Manrope."
            ),
            "firaSans": (
                "Fira Sans (weights 400-900) registered as --font-title; used by "
                "the LeafFreak wordmark on the login page."
            ),
            "inter": "Inter, registered as --font-sans; the default body font.",
            "viewport": (
                "Next.js viewport export. Fixes the scale at 1 and disables "
                "pinch and double-tap zoom so the WebView feels native, and uses "
                "viewportFit cover so the layout draws under the iOS status bar "
                "and home indicator."
            ),
            "RootLayout": {
                "description": (
                    "Renders the html and body elements, applies the font "
                    "variables, and nests the providers and global overlays "
                    "around the current page."
                ),
                "params": {"{ children, }": "The active route's page element."},
                "returns": "The full document tree.",
                "notes": (
                    "Global overlays rendered on every route: ScanOnlyMobileNavBar "
                    "(hides itself on some routes), ResumePendingScan (renders "
                    "nothing) and the sonner Toaster used for error toasts. "
                    "suppressHydrationWarning is set because next-themes edits "
                    "the html class before hydration."
                ),
            },
        },
    },
    "src/app/page.tsx": {
        "summary": (
            "Splash screen at route /. It is the app's entry point and decides "
            "where to send the user: /login, /setup or /home, depending on "
            "server reachability and the current session."
        ),
        "details": (
            "Calls the Tauri command ping (generated ping()), then get_session "
            "(getSession()). No session leads to /login; a session whose "
            "profileComplete flag is false leads to /setup; otherwise /home. If "
            "ping fails, useAppStore.isConfirmedOffline is set to true and the "
            "user is sent to /home anyway, where an offline notice appears. If "
            "get_session fails, the user is sent to /login. All redirects use "
            "router.replace so the splash is not kept in history. While the "
            "checks run, the page shows a placeholder 'Plant App' label and a "
            "Home button."
        ),
        "symbols": {
            "SplashScreenPage": {
                "description": (
                    "Runs the connectivity and session check on mount and "
                    "redirects accordingly; renders a minimal placeholder."
                ),
                "errors": (
                    "Failures are only logged with console.warn; the user is "
                    "routed to /home (ping failed) or /login (session lookup "
                    "failed). No toast is shown."
                ),
                "notes": (
                    "Test hint: with the backend stopped, launching the app "
                    "should land on /home with the 'You're offline' alert. The "
                    "placeholder content is visible only briefly."
                ),
            },
        },
    },
    "src/app/login/page.tsx": {
        "summary": (
            "Authentication screen at route /login. It shows an animated swirl "
            "background, the LeafFreak wordmark, and either the sign-up form "
            "(the default) or the log-in form, with a text link to toggle "
            "between them."
        ),
        "details": (
            "The forms themselves live in features/auth/components and call the "
            "log_in and sign_up Tauri commands through the auth mutation hooks. "
            "There is no link to /reset-password from this page (or anywhere "
            "else in the app), so the reset flow is only reachable by URL. The "
            "Scan button is hidden on this route."
        ),
        "symbols": {
            "Title": {
                "description": (
                    "Faded header with a leaf icon, the 'LeafFreak' wordmark and "
                    "the tagline 'Become a freak of nature'."
                ),
            },
            "LoginPage": {
                "description": (
                    "Holds a local signUp flag (initially true) and renders "
                    "SignupForm or LoginForm over a full-screen Swirl, plus the "
                    "'Already have an account? Log In' or 'New to LeafFreak? "
                    "Sign Up' toggle."
                ),
                "notes": (
                    "Email and password live in useAuthFormStore, so values typed "
                    "into one form remain filled after toggling to the other."
                ),
            },
        },
    },
    "src/app/setup/page.tsx": {
        "summary": (
            "Profile completion screen at route /setup, shown after sign-up when "
            "the session's profileComplete flag is false. The user enters first "
            "name, last name and how they plan to use the app, then taps 'Get "
            "Started'."
        ),
        "details": (
            "Submits through useCompleteProfileMutation, which calls the "
            "complete_profile Tauri command, refreshes the cached session and "
            "navigates to /home. Usage intent options come from "
            "USAGE_INTENT_OPTIONS. The Scan button is hidden on this route."
        ),
        "symbols": {
            "SetupPage": {
                "description": (
                    "Renders the three-field form with local state for each "
                    "field. The submit button is disabled while the mutation is "
                    "pending (label 'Saving...') or while no usage intent is "
                    "selected."
                ),
                "errors": (
                    "A failed complete_profile call is shown inline below the "
                    "form via FieldError and getErrorMessage."
                ),
                "notes": (
                    "First and last name are required by the browser's form "
                    "validation; there is no further client-side validation."
                ),
            },
            "SetupPage.handleSubmit": {
                "description": (
                    "Prevents the native form submit and, if a usage intent is "
                    "selected, fires the complete-profile mutation with "
                    "firstName, lastName and usageIntent."
                ),
                "params": {"event": "The form submit event."},
            },
        },
    },
    "src/app/reset-password/page.tsx": {
        "summary": (
            "Two-step password reset screen at route /reset-password. Step one "
            "asks for an email and requests a reset code; step two asks for the "
            "code plus a new password (entered twice) and confirms the reset."
        ),
        "details": (
            "Step one calls request_password_reset (requestPasswordReset), which "
            "resolves to a string or null. A non-null value is a development "
            "reset code and is displayed on step two as 'Dev code: ...', so "
            "testers can complete the flow without email delivery. Step two "
            "calls confirm_password_reset and, on success, replaces the route "
            "with /login. A 'Back to log in' link is always shown. No page links "
            "here, so it must be opened by URL. The Scan button is hidden on "
            "this route."
        ),
        "symbols": {
            "Step": "Which step of the flow is showing: \"request\" or \"confirm\".",
            "ResetPasswordPage": {
                "description": (
                    "Holds the step, form fields, dev code and a client-side "
                    "form error in local state, and renders the request or "
                    "confirm form accordingly. Uses two TanStack mutations, one "
                    "per step."
                ),
                "errors": (
                    "Backend errors from either command and client-side "
                    "validation errors are shown inline with FieldError."
                ),
                "notes": (
                    "Once on the confirm step there is no way back to the "
                    "request step except reloading the page. Submit buttons are "
                    "disabled and relabelled ('Sending...', 'Resetting...') "
                    "while pending."
                ),
            },
            "ResetPasswordPage.handleRequest": {
                "description": (
                    "Prevents the native submit, clears the form error and fires "
                    "the request-code mutation for the entered email. On success "
                    "the dev code is stored and the page moves to the confirm "
                    "step."
                ),
                "params": {"event": "The form submit event."},
            },
            "ResetPasswordPage.handleConfirm": {
                "description": (
                    "Validates that both password fields match and that the new "
                    "password is at least 8 characters, then fires the confirm "
                    "mutation with email, code and newPassword."
                ),
                "params": {"event": "The form submit event."},
                "errors": (
                    "Shows 'Passwords do not match' or 'Password must be at "
                    "least 8 characters' inline without calling the backend."
                ),
            },
        },
    },
    "src/app/home/page.tsx": {
        "summary": (
            "Home dashboard at route /home. It greets the user, shows progress "
            "on today's three daily plant quests, lists each quest as a card, "
            "and links to the leaderboard, profile, collection and community "
            "finds."
        ),
        "details": (
            "Data comes from the get_home Tauri command via useQuery with query "
            "key [\"home\"]. That key is invalidated after every successful scan "
            "so found quests update. Only first_name and quests from "
            "HomeResponse are used; level, rank_title, xp and max_xp are "
            "ignored. While loading, the greeting reads 'Good morning' with no "
            "name, the quest list is empty and the counter shows '0 of 3 found'. "
            "If the query fails, an alert asks the user to check they are signed "
            "in and that the server is running. On the first home visit of the "
            "session, if the splash screen found the server unreachable, a "
            "'You're offline' alert is latched on via useHomeStore. Navigation "
            "out: Trophy button to /leaderboard, User button to /profile, 'My "
            "Collection' to /collection, 'Community Finds' to /recent_finds."
        ),
        "symbols": {
            "RARITY_VARIANT": (
                "Maps each PlantRarity to a shadcn Badge variant: Common is "
                "outline, Uncommon is secondary, and Rare, SuperRare and Exotic "
                "are default. The same table is duplicated in plant_analysis and "
                "recent_finds."
            ),
            "HomePage": {
                "description": (
                    "Fetches the home payload, computes found/total counts and "
                    "the progress percentage, and renders the header buttons, "
                    "greeting, alerts, navigation buttons, progress bar and the "
                    "animated quest list."
                ),
                "errors": (
                    "Query failure renders an inline Alert ('Couldn't load "
                    "today's plants'); there is no retry button."
                ),
                "notes": (
                    "The greeting always says 'Good morning' regardless of time. "
                    "The total falls back to 3 when no quests are returned. An "
                    "effect flips useHomeStore.isFirstVisit to false on the "
                    "first render and, if useAppStore.isConfirmedOffline is "
                    "true, sets showOfflineNotice, which then stays visible for "
                    "the rest of the session."
                ),
            },
            "QuestCard": {
                "description": (
                    "Card for one daily quest: thumbnail (or a grey placeholder "
                    "when image_base64 is null), common name, rarity badge, "
                    "italic scientific name, XP reward, and either a 'Found' "
                    "check or 'Not found yet'."
                ),
                "params": {"{ quest }": "The DailyPlantQuest to display."},
            },
        },
    },
    "src/app/plant_screenshot/page.tsx": {
        "summary": (
            "'Analyzing plant...' screen at route /plant_screenshot. It uploads "
            "the photo the user just took for identification, shows a progress "
            "bar while waiting, and then moves on to the results page or back "
            "to where the user came from."
        ),
        "details": (
            "Reads pendingImagePath, previousPath and result from useScanStore. "
            "It calls the scan_plant Tauri command (scanPlant({ imagePath })). On "
            "success it stores the result and image data URL with "
            "setResult and invalidates the [\"home\"] and [\"profile\"] "
            "queries; a separate effect then replaces the route with "
            "/plant_analysis. Other caches such as imageLocations, "
            "recent_finds and the leaderboard are not invalidated and refresh "
            "only after their 60-second stale time. If there is no pending image "
            "(for example after the WebView was reloaded), it asks the camera "
            "plugin for a recovered photo with takePendingPhoto and goes back "
            "to previousPath (or /home) when none exists. The Scan button is "
            "hidden on this route."
        ),
        "symbols": {
            "PlantScreenshotPage": {
                "description": (
                    "Drives the scan request and renders the heading, hint text "
                    "and a simulated progress bar."
                ),
                "errors": (
                    "A failed scan logs a warning, shows the toast 'Plant scan "
                    "failed: <message>', clears the pending scan and replaces "
                    "the route with previousPath (or /home)."
                ),
                "notes": (
                    "The progress bar is not real upload progress: it starts at "
                    "8, adds 4 every 400 ms up to 90, and jumps to 100 on "
                    "success. markScanStarted guards against starting the scan "
                    "twice when React Strict Mode re-runs the effect. Test hint: "
                    "a photo with no plant still goes to /plant_analysis if the "
                    "backend returns a result."
                ),
            },
        },
    },
    "src/app/plant_analysis/page.tsx": {
        "summary": (
            "Scan result page at route /plant_analysis. It shows the plant photo "
            "with its name, rarity and confidence, any XP or daily-quest "
            "rewards, a summary, plant profile, a world map of GBIF "
            "observations, care guide, interesting facts, toxicity notes and an "
            "expandable 'How we identified this plant' section."
        ),
        "details": (
            "All scan data comes from useScanStore (result, imageSrc, "
            "previousPath); this page does not fetch the scan itself. It is "
            "reached after a new scan (from /plant_screenshot) or by tapping a "
            "plant in the collection or profile (FoundPlantComponent loads the "
            "stored scan with get_plant_scan). When no result is in the store, "
            "the page renders nothing and replaces the route with previousPath "
            "(or /home). The back button links to previousPath. The "
            "distribution map calls get_plant_geo_distribution with the "
            "scientific name. Optional sections (native range, care, facts, "
            "toxicity, identification notes) are hidden when the backend "
            "returns null or empty values."
        ),
        "symbols": {
            "RARITY_VARIANT": (
                "Badge variant per PlantRarity (Common outline, Uncommon "
                "secondary, others default); duplicate of the table in the home "
                "page."
            ),
            "PlantAnalysisPage": {
                "description": (
                    "Renders the full result layout from the stored "
                    "PlantScanResult. The rewards card appears only when XP was "
                    "awarded, a daily quest was matched, or the user leveled up, "
                    "and its text varies between 'Daily plant discovered!' and "
                    "'Scan rewards', with notes for new species, the new-species "
                    "bonus and leveling up."
                ),
                "notes": (
                    "Missing names fall back to 'Unknown plant'. When opened "
                    "from the collection the reward card is hidden because the "
                    "synthetic result has xp_awarded 0. The scan's is_plant flag "
                    "is not checked, so non-plant results render with whatever "
                    "text the backend returned. The toxicity card always ends "
                    "with a fixed safety warning."
                ),
            },
            "PlantDistributionMap": {
                "description": (
                    "Card that fetches GBIF occurrence records for a species "
                    "through the get_plant_geo_distribution command and draws "
                    "them as a MapTiler heatmap ('streets-v2' style), fitting the "
                    "view to the points."
                ),
                "params": {
                    "{ scientificName, className, }": (
                        "scientificName is the species to look up; className is "
                        "added to the card (used to span two grid columns on "
                        "large screens)."
                    ),
                },
                "errors": (
                    "Fetch failures are shown inside the card as 'Distribution "
                    "data is unavailable right now: <message>'."
                ),
                "notes": (
                    "States: 'Loading observation data...', error text, 'No "
                    "georeferenced observations were found...' when no valid "
                    "coordinates exist, and 'Preparing map...' until the heatmap "
                    "layer is added. Records with null, non-finite or "
                    "out-of-range coordinates are filtered out. The footer shows "
                    "how many points were mapped out of the total record count. "
                    "The MapTiler API key is hard-coded, and a leftover "
                    "console.log prints the raw response. The parent passes "
                    "key={scientificName} so a new species remounts the map."
                ),
            },
            "TextSection": {
                "description": (
                    "Small titled paragraph with an optional leading icon, used "
                    "throughout the page for appearance, native range, toxicity "
                    "and identification notes."
                ),
                "params": {
                    "{ title, body, icon, }": (
                        "Heading text, paragraph text and an optional icon node."
                    ),
                },
            },
            "CareItem": {
                "description": (
                    "Tile in the care guide grid showing an icon, a label "
                    "(Light, Water, Soil, Temperature) and the advice text."
                ),
                "params": {
                    "{ icon, label, body, }": "Icon node, label and advice text.",
                },
            },
        },
    },
    "src/app/collection/page.tsx": {
        "summary": (
            "'My Collection' page at route /collection. It lists every plant the "
            "user has found as a two-column grid of cards, with a search box, a "
            "sort menu and totals for scans and unique species."
        ),
        "details": (
            "Uses the get_profile Tauri command via useQuery with key "
            "[\"profile\"] (shared with the profile page and invalidated after "
            "each scan), reading found_plants and stats. Filtering and sorting "
            "happen on the client. Empty states: 'No plants yet. Scan one to "
            "start your collection!' when nothing has been found, or 'No plants "
            "match your search.' when the filter excludes everything. There is "
            "no explicit loading or error UI; while loading or on error the "
            "grid is simply empty and the stats show 0. Tapping a card opens "
            "/plant_analysis for that plant; tapping its photo opens the "
            "full-screen ImageViewer instead. The back button goes to /home."
        ),
        "symbols": {
            "SORT_OPTIONS": (
                "Sort menu choices: newest first, oldest first and name (A-Z)."
            ),
            "SortOption": "Union of the SORT_OPTIONS values: \"newest\", \"oldest\" or \"name\".",
            "CollectionSortMenu": {
                "description": (
                    "Icon button that opens a dropdown with a radio group of the "
                    "sort options."
                ),
                "params": {
                    "{ value, onChange }": (
                        "The currently selected SortOption and a callback "
                        "invoked with the new choice."
                    ),
                },
            },
            "PlantCollectionPage": {
                "description": (
                    "Fetches the profile, applies the search filter and the "
                    "chosen sort (default newest), and renders the header, "
                    "search input with a clear button, sort menu, stat tiles and "
                    "animated grid of FoundPlantComponent cards."
                ),
                "notes": (
                    "Sorting by date parses found_on with new Date. Each plant's "
                    "rarity is cast to the three-value PlantRarity from "
                    "profileTypes, so SuperRare and Exotic plants get no "
                    "matching badge style in FoundPlantComponent."
                ),
            },
            "PlantCollectionPage.applyPlantFilter": {
                "description": (
                    "Case-insensitive match of the trimmed search text against "
                    "the plant's common or scientific name."
                ),
                "params": {"plant": "The CollectionPlant to test."},
                "returns": "True when the plant should be shown.",
            },
            "StatTile": {
                "description": (
                    "Pill-shaped card showing a value next to a label. A "
                    "different StatTile with the same name exists in the "
                    "profile page."
                ),
                "params": {
                    "{ label, value, onClick }": (
                        "Label text, displayed value and an optional click "
                        "handler (unused on this page)."
                    ),
                },
            },
        },
    },
    "src/app/profile/page.tsx": {
        "summary": (
            "Profile page at route /profile. It shows the user's initials "
            "avatar, name, join month, current rank with XP progress, scan / "
            "species / streak stats, up to four most recent finds, and a Sign "
            "out button."
        ),
        "details": (
            "Uses get_profile via useQuery with key [\"profile\"]. While loading "
            "or on error the page shows fallbacks ('Plant explorer', rank "
            "'Unknown', 'Lv. 1', '0 / 30 XP', 'Next: Gardener') and no error "
            "message. Sign out opens a confirmation dialog and then runs "
            "useLogoutMutation (log_out command), which clears client state and "
            "replaces the route with /login. Navigation out: Home button to "
            "/home, Map button to /map, Scans tile to /collection, and tapping a "
            "find opens /plant_analysis."
        ),
        "symbols": {
            "ProfilePage": {
                "description": (
                    "Fetches the profile, derives initials, display name, the "
                    "'Joined <Month Year>' label and the XP percentage "
                    "(xp / xp_to_next), and renders the profile layout and the "
                    "sign-out confirmation dialog."
                ),
                "errors": (
                    "Profile load errors are not shown. A failed logout leaves "
                    "the user on the page with the button re-enabled and no "
                    "message."
                ),
                "notes": (
                    "The Scans tile navigates with window.location.href, which "
                    "triggers a full page load rather than client-side routing. "
                    "The Map button has no aria-label. The sign-out button shows "
                    "'Signing out...' and is disabled while the mutation runs."
                ),
            },
            "StatTile": {
                "description": (
                    "Card showing a large value above a small label; clickable "
                    "when onClick is given. Separate from the StatTile in the "
                    "collection page."
                ),
                "params": {
                    "{ label, value, onClick }": (
                        "Label text, displayed value and an optional click "
                        "handler."
                    ),
                },
            },
        },
    },
    "src/app/map/page.tsx": {
        "summary": (
            "Full-screen 'Plant map' at route /map. It shows the user's own "
            "geotagged plant photos on a MapTiler satellite-hybrid map, either as "
            "photo pins with popups or as a heatmap, and has a button to center "
            "on the user's current location."
        ),
        "details": (
            "Data comes from the get_user_image_locations Tauri command via "
            "useQuery with key [\"imageLocations\"]; images without a location "
            "are skipped. After loading, the map flies to a single point or fits "
            "the bounds of all points; with no located images it centers on the "
            "device location from navigator.geolocation. There is no loading or "
            "error UI: a failed or empty query just leaves the map without "
            "markers. The back button links to /profile (its aria-label says "
            "'Back to home'). The Scan button is hidden on this route. The "
            "MapTiler API key is hard-coded in the page."
        ),
        "symbols": {
            "MapLayer": "Display mode of the map: \"point\" (photo pins) or \"heatmap\".",
            "MapLayerConfig": "Describes a map mode for the layer picker: its id, label and Lucide icon.",
            "mapModes": "The two available modes: Pins (point) and Heatmap.",
            "mapHost": (
                "A detached div created once at module load (null during "
                "server rendering) that holds the WebGL map canvas. Keeping the "
                "map on this stable element means React Strict Mode remounts do "
                "not create a second WebGL map, which is costly on iOS."
            ),
            "mapSingleton": (
                "Module-level MapTiler Map instance shared across remounts; "
                "created on first mount and removed only when the page is truly "
                "unmounted."
            ),
            "MapPage": {
                "description": (
                    "Mounts or reuses the map, requests the device location, "
                    "builds markers or the heatmap layer from the image "
                    "locations, and renders the header, layer picker popover and "
                    "locate button."
                ),
                "errors": (
                    "Geolocation failures are only logged to the console; the "
                    "locate button stays disabled."
                ),
                "notes": (
                    "Pins are round 48 px buttons showing the thumbnail (or the "
                    "first letter of the plant name) and open a popup with the "
                    "photo and name. Switching layers tears down and rebuilds "
                    "markers and heatmap layers. Unmount cleanup is deferred "
                    "with setTimeout so a Strict Mode remount can reclaim the "
                    "map first. Uses several useRef handles for the container, "
                    "map and markers."
                ),
            },
            "MapPage.pointsToGeoJSON": {
                "description": "Converts [longitude, latitude] pairs into a GeoJSON FeatureCollection of points for the heatmap helper.",
                "params": {"points": "Array of [longitude, latitude] tuples."},
                "returns": "A GeoJSON FeatureCollection<Point>.",
            },
            "MapPage.centerOnUser": {
                "description": "Flies the map to the user's location at zoom 14; does nothing if the location is unknown.",
            },
        },
    },
    "src/app/leaderboard/page.tsx": {
        "summary": (
            "Leaderboard at route /leaderboard. It lists users ranked by XP, "
            "showing position, initials avatar, name, rank title, level and XP, "
            "and highlights the signed-in user's row with '(You)'."
        ),
        "details": (
            "First loads the session with get_session (query key "
            "[\"session\"]), then get_leaderboard with key "
            "[\"get_leaderboard\", userId], enabled only once a user is known. "
            "States in order of precedence: 'Loading leaderboard...', an error "
            "alert with a 'Try again' button, a 'Sign in to see the leaderboard' "
            "alert when there is no session, 'No leaderboard entries yet.' for "
            "an empty list, and finally the ranked cards. Back button goes to "
            "/home. The list is shown in the order returned by the backend."
        ),
        "symbols": {
            "LeaderboardUserProps": "Props for LeaderboardCard: the user row, its 1-based position and the signed-in SessionInfo.",
            "LeaderboardCard": {
                "description": (
                    "One leaderboard row. Builds the display name (falling back "
                    "to 'Plant explorer') and initials, and applies a tinted "
                    "background and stronger ring when the row's id matches the "
                    "session's userId."
                ),
                "params": {
                    "{user, position, loggedInUser}": (
                        "The LeaderboardUser, its displayed position and the "
                        "current session used to detect the user's own row."
                    ),
                },
            },
            "LeaderboardPage": {
                "description": "Fetches session and leaderboard and renders the header and the appropriate state or list.",
                "errors": (
                    "Either query failing shows 'Couldn't load leaderboard' with "
                    "a 'Try again' button that refetches whichever query failed."
                ),
            },
        },
    },
    "src/app/recent_finds/page.tsx": {
        "summary": (
            "'Community Finds' page at route /recent_finds. It shows the most "
            "recent plant discoveries made by other users, each with a photo, "
            "names, rarity badge, the finder's name and the date found."
        ),
        "details": (
            "Loads the session via get_session (key [\"session\"]) and then calls "
            "get_recent_finds with { count: 50, offset: 0, userExclude: userId } "
            "under key [\"recent_finds\", userId], so the signed-in user's own "
            "finds are excluded. States: spinning-leaf 'Loading community "
            "finds...', error alert with 'Try again', 'Sign in to see community "
            "finds' when there is no session, an empty state ('No community "
            "finds yet'), or the list. There is no paging beyond the first 50. "
            "Photos open full screen in ImageViewer. Back button goes to /home. "
            "The Scan button is hidden on this route."
        ),
        "symbols": {
            "RARITY_VARIANT": "Badge variant per PlantRarity; duplicate of the table in the home page.",
            "Find": {
                "description": (
                    "Card for one community find. The finder's name falls back "
                    "to 'A Leaf Freak' when both name parts are empty, and a "
                    "leaf placeholder is shown when there is no photo."
                ),
                "params": {"{ recentFind }": "The RecentFind (plant plus finder's names) to display."},
                "notes": "found_on is displayed exactly as the backend sends it, without formatting.",
            },
            "RecentFindsPage": {
                "description": "Fetches the session and recent finds and renders the header and the matching state or list.",
                "errors": (
                    "Either query failing shows 'Couldn't load community finds' "
                    "with a 'Try again' button that refetches the failed query."
                ),
            },
        },
    },
    # ------------------------------------------------------------------
    # src/components
    # ------------------------------------------------------------------
    "src/components/LocalImage.tsx": {
        "summary": (
            "Renders an image from a local file path by converting it to a "
            "Tauri asset URL with convertFileSrc. Currently not used anywhere."
        ),
        "symbols": {
            "Props": "Props for LocalImage: the absolute file path, an optional className and optional alt text.",
            "LocalImage": {
                "description": "Plain img element whose src is convertFileSrc(path).",
                "params": {"{ path, className, altText }": "File path on the device, CSS classes and alt text."},
            },
        },
    },
    "src/components/PointGridBg.tsx": {
        "summary": (
            "Decorative fixed full-screen dotted-grid background used behind "
            "most pages. The pattern is defined by the point-grid-bg class in "
            "globals.css."
        ),
        "symbols": {
            "PointGridBg": "Renders an aria-hidden, non-interactive fixed div with the point-grid-bg class.",
        },
    },
    "src/components/RepeatingBg.tsx": {
        "summary": (
            "Decorative fixed background using the scrolling repeating-bg CSS "
            "class from globals.css. Currently not used by any page."
        ),
        "symbols": {
            "RepeatingBg": "Renders an aria-hidden fixed div with the repeating-bg class behind the content (-z-10).",
        },
    },
    "src/components/QueryProvider.tsx": {
        "summary": (
            "Creates the app-wide TanStack Query client and provides it to all "
            "pages."
        ),
        "details": (
            "Default query options: staleTime 60 seconds and retry disabled, so "
            "a failed Tauri command surfaces immediately as an error state "
            "rather than being retried."
        ),
        "symbols": {
            "QueryProvider": {
                "description": "Creates one QueryClient per mount (kept in state) and wraps children in QueryClientProvider.",
                "params": {"{ children }": "The application tree."},
            },
        },
    },
    "src/components/ThemeProvider.tsx": {
        "summary": "Wraps the app in next-themes with the theme forced to light.",
        "symbols": {
            "ThemeProvider": {
                "description": (
                    "next-themes provider using the class attribute, with "
                    "forcedTheme set to light, so dark mode never activates even "
                    "though enableSystem is set."
                ),
                "params": {"{ children }": "The application tree."},
            },
        },
    },
    "src/components/ResumePendingScan.tsx": {
        "summary": (
            "Invisible global component that resumes a scan after iOS reloads "
            "the WebView while the camera was open. If the camera plugin has a "
            "saved photo, it navigates to /plant_screenshot."
        ),
        "details": (
            "Mounted once in the root layout. On every route change it awaits "
            "takePendingPhoto, which asks the native camera plugin once per app "
            "session and otherwise returns the store's pending image path."
        ),
        "symbols": {
            "ResumePendingScan": {
                "description": (
                    "Effect that pushes /plant_screenshot when a pending photo "
                    "path exists and the user is not already on "
                    "/plant_screenshot or /plant_analysis. Renders nothing."
                ),
                "notes": (
                    "Test hint: take a photo, force the WebView to reload while "
                    "the camera is open (or kill and relaunch), and the app "
                    "should continue to the analyzing screen."
                ),
            },
        },
    },
    "src/components/generic/AnimatedButton.tsx": {
        "summary": (
            "The app's main button component: a shadcn-style button with a "
            "springy scale animation (motion) that renders either as a button or, "
            "when href is given, as a Next.js Link."
        ),
        "details": (
            "Adds the custom glass and defaultGlass variants to the usual shadcn "
            "variants. The button is drawn at a reduced resting scale and scales "
            "up to 1 on hover, so the enlarged state stays crisp instead of "
            "upscaling the rendered layer."
        ),
        "symbols": {
            "HOVER_SCALE": "Relative enlargement on hover (1.2).",
            "REST_SCALE": "Resting scale, 1 / HOVER_SCALE, so the hover state renders at scale 1.",
            "TAP_SCALE": "Scale while pressed: 90 percent of the resting scale.",
            "buttonVariants": (
                "class-variance-authority definition of the button classes. "
                "Variants: default, glass, defaultGlass, outline, secondary, "
                "ghost, destructive, link. Sizes: default, xs, sm, lg (14 high, "
                "text-xl, recommended for iOS), icon, icon-xs, icon-sm, icon-lg."
            ),
            "MotionLink": "Next.js Link wrapped with motion.create so it can be animated.",
            "AnimatedButtonBase": "Props common to both forms: variant and size, className, children and disabled.",
            "AnimatedButtonAsButton": "Props for the button form: motion.button props without href.",
            "AnimatedButtonAsLink": "Props for the link form: MotionLink props with a required href.",
            "AnimatedButtonProps": "Union of the button and link prop shapes.",
            "useCanHover": {
                "description": (
                    "Tracks whether the device has a fine pointer that can hover, "
                    "using the '(hover: hover) and (pointer: fine)' media query."
                ),
                "returns": "True on mouse-driven devices, false on touch devices and before mount.",
            },
            "AnimatedButton": {
                "description": (
                    "Renders a motion.button (type defaults to \"button\") or, "
                    "if href is set, a MotionLink, with the computed variant "
                    "classes and the rest, hover and tap scale animations."
                ),
                "params": {
                    "{ className, children, size = \"default\", variant = \"default\", disabled, href, ...props }": (
                        "Variant and size keys, extra classes, content, disabled "
                        "flag, optional href (switches to link mode) and any "
                        "other button or link props."
                    ),
                },
                "notes": (
                    "Hover scaling is skipped on touch devices and when "
                    "disabled. A disabled link gets aria-disabled, is removed "
                    "from the tab order and has its click prevented."
                ),
            },
        },
    },
    "src/components/generic/ImageViewer.tsx": {
        "summary": (
            "Full-screen photo viewer. Wraps any content in a button that opens "
            "a dark dialog showing the image at full size with a 3D flip-in "
            "animation."
        ),
        "details": "Used by FoundPlantComponent and the Community Finds cards.",
        "symbols": {
            "ImageViewerProps": "Props: image src (data URL or URL), alt text (also the dialog title), trigger children and optional trigger className.",
            "ImageViewer": {
                "description": (
                    "Dialog whose trigger is a button around children. The "
                    "content fills the screen, respects safe-area insets, shows a "
                    "'Photo viewer' header with the alt text and a close button, "
                    "and displays the unoptimized image with object-contain."
                ),
                "params": {"{ src, alt, children, className, }": "Image source, alt text, trigger content and trigger classes."},
                "notes": "The flip animation is disabled when the user prefers reduced motion.",
            },
        },
    },
    "src/components/mobile-nav-bar/ScanOnlyMobileNavBar.tsx": {
        "summary": (
            "The large floating 'Scan' button pinned to the bottom of the "
            "screen. Tapping it opens the native camera and, once a photo is "
            "taken, starts the scan flow."
        ),
        "details": (
            "Mounted globally in the root layout. Hidden on /login, "
            "/reset-password, /setup, /plant_screenshot, /map and /recent_finds; "
            "visible elsewhere, including / and /plant_analysis."
        ),
        "symbols": {
            "ScanOnlyMobileNavBar": {
                "description": "Renders the Scan button unless the current route is in the hidden list.",
            },
            "ScanOnlyMobileNavBar.handleScan": {
                "description": (
                    "Calls the camera plugin's take_photo through takePhoto. If "
                    "a file path comes back, records it with "
                    "useScanStore.setPendingScan along with the current route as "
                    "previousPath, then navigates to /plant_screenshot."
                ),
                "errors": "Camera failures are logged and shown as the toast 'Camera failed: <message>'.",
                "notes": "An empty result (for example the user cancelled) does nothing.",
            },
        },
    },
    "src/components/mobile-nav-bar/index.tsx": {
        "summary": (
            "Earlier three-tab bottom navigation bar (Home, Scan, Profile). It "
            "is not imported anywhere; the app uses ScanOnlyMobileNavBar "
            "instead."
        ),
        "symbols": {
            "NAV_ITEMS": "Tabs: /home (Home), /plant_screenshot (Scan) and /profile (Profile), each with a Lucide icon.",
            "MobileNavBar": {
                "description": (
                    "Renders the tab bar with the active tab highlighted "
                    "(aria-current=\"page\"); hidden on /login."
                ),
                "notes": (
                    "Unused. Its Scan tab links straight to /plant_screenshot "
                    "without taking a photo, and session checks are commented "
                    "out."
                ),
            },
        },
    },
    "src/components/ui/canvas-effects/Swirl.tsx": {
        "summary": (
            "Animated canvas background of twisting radial colour bands, used "
            "full-screen behind the login page."
        ),
        "details": (
            "Built on useCanvasEffect. Pixels are computed in JavaScript on an "
            "offscreen canvas at one third of the resolution and then scaled up. "
            "Prop values are mirrored into refs so the running animation picks "
            "up changes without restarting."
        ),
        "symbols": {
            "hexToRgb": {
                "description": "Parses a '#rrggbb' hex colour into its red, green and blue components.",
                "params": {"hex": "Colour string, with or without the leading '#'."},
                "returns": "A [r, g, b] tuple of 0-255 integers.",
            },
            "SwirlProps": (
                "Props: colors (palette cycled around the spiral), bands (bands "
                "per revolution), twist (how sharply bands wind with radius), "
                "speed (animation multiplier), softness (0 hard edges to 1 fully "
                "blended), className and style."
            ),
            "DEFAULT_COLORS": "Default pale green and white palette.",
            "Swirl": {
                "description": "Renders a full-size canvas and draws the animated swirl into it each frame.",
                "params": {
                    "{ colors = DEFAULT_COLORS, bands = 6, twist = 2.2, speed = 1, softness = 0, className, style, }": (
                        "See SwirlProps; defaults are 6 bands, twist 2.2, speed "
                        "1 and hard edges."
                    ),
                },
                "notes": (
                    "Animation advances per 60fps-equivalent frame, so speed is "
                    "the same on 60 Hz and 120 Hz screens. It pauses offscreen, "
                    "in background tabs and under reduced motion (via "
                    "mountCanvasEffect)."
                ),
            },
        },
    },
    "src/components/window-chrome/AdaptiveWindowChrome.tsx": {
        "summary": (
            "Custom desktop title bar selector. It always returns the Windows "
            "style chrome. Its use in the root layout is commented out, so it "
            "is not rendered."
        ),
        "symbols": {
            "AdaptiveWindowChromeProps": "Props: optional app icon and title node for the Windows chrome.",
            "AdaptiveWindowChrome": {
                "description": "Renders WindowsWindowChrome with the given icon and title.",
                "params": {"{ appIconAndTitle, }": "Optional node shown at the left of the title bar."},
            },
        },
    },
    "src/components/window-chrome/MacWindowChrome.tsx": {
        "summary": (
            "Custom draggable title bar with minimize, maximize and close "
            "buttons for desktop builds. Not used anywhere."
        ),
        "symbols": {
            "MacWindowChrome": {
                "description": "Renders a data-tauri-drag-region bar with three window control buttons.",
            },
            "MacWindowChrome.handleMinimize": {"description": "Minimizes the current Tauri window."},
            "MacWindowChrome.handleMaximize": {"description": "Toggles the current Tauri window between maximized and restored."},
            "MacWindowChrome.handleClose": {"description": "Closes the current Tauri window."},
        },
    },
    "src/components/window-chrome/WindowsWindowChrome.tsx": {
        "summary": (
            "Custom draggable Windows-style title bar with an optional icon and "
            "title on the left and window controls on the right. Only reachable "
            "through the unused AdaptiveWindowChrome."
        ),
        "symbols": {
            "WindowsWindowChromeProps": "Props: optional app icon and title node.",
            "WindowsWindowChrome": {
                "description": "Renders the drag region, the icon and title slot, and minimize, maximize and close buttons.",
                "params": {"{ appIconAndTitle, }": "Optional node shown at the left of the bar."},
            },
            "WindowsWindowChrome.handleMinimize": {"description": "Minimizes the current Tauri window."},
            "WindowsWindowChrome.handleMaximize": {"description": "Toggles the current Tauri window between maximized and restored."},
            "WindowsWindowChrome.handleClose": {"description": "Closes the current Tauri window."},
        },
    },
    # ------------------------------------------------------------------
    # src/features/auth
    # ------------------------------------------------------------------
    "src/features/auth/constants.ts": {
        "summary": "Fixed answer choices for the 'How do you plan on using this app?' question on /setup.",
        "symbols": {
            "USAGE_INTENT_OPTIONS": "The options 'Just for fun', 'Learning', 'Gardening' and 'Work or school'.",
            "UsageIntent": (
                "Union of the option strings. Not referenced elsewhere; the setup "
                "page keeps the selection as a plain string."
            ),
        },
    },
    "src/features/auth/components/LoginForm.tsx": {
        "summary": "'Log In' form with email and password fields, shown on /login.",
        "details": (
            "Field values live in useAuthFormStore. Submitting calls the log_in "
            "command through useLoginMutation, which on success clears client "
            "state, reloads the session and routes to /setup or /home."
        ),
        "symbols": {
            "LoginForm": {
                "description": (
                    "Renders the animated form. The submit button reads 'Logging "
                    "in...' and is disabled while the request is pending."
                ),
                "errors": "Login failures (for example wrong credentials) appear inline below the fields via getErrorMessage.",
                "notes": "There is no 'Forgot password' link to /reset-password.",
            },
            "LoginForm.handleSubmit": {
                "description": "Prevents the native submit and fires the login mutation with the stored email and password.",
                "params": {"event": "The form submit event."},
            },
        },
    },
    "src/features/auth/components/SignupForm.tsx": {
        "summary": "'Sign Up' form with email and password fields; the default form on /login.",
        "details": (
            "Shares field values with LoginForm through useAuthFormStore. "
            "Submitting calls sign_up through useSignupMutation, which on "
            "success routes new users to /setup."
        ),
        "symbols": {
            "SignupForm": {
                "description": (
                    "Renders the animated form. The submit button reads 'Signing "
                    "up...' and is disabled while pending."
                ),
                "errors": "Sign-up failures (for example email already registered) appear inline via getErrorMessage.",
                "notes": "There is no client-side password strength check or confirm-password field; validation is left to the backend.",
            },
            "SignupForm.handleSubmit": {
                "description": "Prevents the native submit and fires the sign-up mutation with the stored email and password.",
                "params": {"event": "The form submit event."},
            },
        },
    },
    "src/features/auth/hooks/useAuthMutations.ts": {
        "summary": (
            "TanStack Query mutation hooks for logging in, signing up, "
            "completing the profile and logging out, including the navigation "
            "that follows each one."
        ),
        "details": (
            "Wraps the log_in, sign_up, complete_profile, log_out and "
            "get_session Tauri commands. After login, sign-up and logout, all "
            "cached queries, the scan store and the auth form are cleared so "
            "data from a previous account is never shown."
        ),
        "symbols": {
            "resetClientSession": {
                "description": (
                    "Clears every cached query, resets useScanStore and empties "
                    "the email and password in useAuthFormStore."
                ),
                "params": {"queryClient": "The app's QueryClient."},
            },
            "routeAfterAuth": {
                "description": (
                    "Fetches the session, writes it into the [\"session\"] query "
                    "cache, and pushes /login (no session), /setup (profile "
                    "incomplete) or /home."
                ),
                "params": {
                    "router": "The Next.js app router.",
                    "queryClient": "The app's QueryClient.",
                },
            },
            "useLoginMutation": {
                "description": "Mutation that calls log_in with { email, password } and then resets client state and routes via routeAfterAuth.",
                "returns": "The TanStack mutation object.",
                "errors": "The rejected value is stored on mutation.error for the form to display.",
            },
            "useSignupMutation": {
                "description": "Mutation that calls sign_up with { email, password } and then resets client state and routes via routeAfterAuth (normally to /setup).",
                "returns": "The TanStack mutation object.",
                "errors": "The rejected value is stored on mutation.error.",
            },
            "useCompleteProfileMutation": {
                "description": "Mutation that calls complete_profile with { firstName, lastName, usageIntent }, refreshes the cached session and pushes /home.",
                "returns": "The TanStack mutation object.",
                "errors": "The rejected value is stored on mutation.error.",
            },
            "useLogoutMutation": {
                "description": "Mutation that calls log_out, resets client state and replaces the route with /login.",
                "returns": "The TanStack mutation object.",
                "errors": "Failures leave the user signed in on the current page; the profile page shows no message.",
            },
        },
    },
    "src/features/auth/hooks/useIsValidSession.ts": {
        "summary": "Shared session query key and a hook that reports whether a session exists.",
        "symbols": {
            "sessionQueryKey": (
                "Query key [\"session\"] for the get_session result. The auth "
                "mutations write to it, and the leaderboard and recent-finds "
                "pages read the same key."
            ),
            "useIsValidSession": {
                "description": "Queries get_session and maps the result to a boolean.",
                "returns": "A TanStack query whose data is true when a session exists.",
                "notes": "Only referenced from commented-out code in the unused MobileNavBar.",
            },
        },
    },
    "src/features/auth/store/useAuthFormStore.ts": {
        "summary": (
            "Zustand store for the email and password typed into the login and "
            "sign-up forms, so both forms share the same values."
        ),
        "symbols": {
            "Store": "Shape of the store: password, email and setValues.",
            "useAuthFormStore": "Zustand hook holding the auth form fields; both start empty and are cleared after login, sign-up and logout.",
            "useAuthFormStore.setValues": {
                "description": "Merges the given fields into the store.",
                "params": {"values": "Partial store values, for example { email }."},
            },
        },
    },
    # ------------------------------------------------------------------
    # src/features/home
    # ------------------------------------------------------------------
    "src/features/home/store/useHomeStore.ts": {
        "summary": "Zustand store for one-time home page state: whether this is the first home visit and whether to show the offline notice.",
        "symbols": {
            "Store": "Shape of the store: isFirstVisit, showOfflineNotice and setValues.",
            "useHomeStore": (
                "Zustand hook. isFirstVisit starts true and is set false by the "
                "home page; showOfflineNotice starts false and is latched true "
                "if the first visit happens while offline. Neither is persisted "
                "across app launches."
            ),
            "useHomeStore.setValues": {
                "description": "Merges the given fields into the store.",
                "params": {"values": "Partial store values."},
            },
        },
    },
    "src/features/home/types/homeTypes.ts": {
        "summary": (
            "Mock home-page types and fixture data from before the backend "
            "existed. Nothing imports this file; the home page uses "
            "HomeResponse and DailyPlantQuest from features/plant_scan/types."
        ),
        "symbols": {
            "DailyPlantQuest": (
                "Mock quest shape in camelCase with a Tailwind tileClass for the "
                "placeholder tile. Duplicates the name of the real "
                "DailyPlantQuest in features/plant_scan/types, which has a "
                "different shape."
            ),
            "HomeMock": "Mock home payload: first name and a list of mock quests.",
            "FAKE_HOME": "Unused fixture with three made-up quests (Rose, Eastern Redbud, White Oak) for a user named Grayson.",
        },
    },
    # ------------------------------------------------------------------
    # src/features/plant_scan
    # ------------------------------------------------------------------
    "src/features/plant_scan/store/useScanStore.ts": {
        "summary": (
            "Zustand store that carries a scan through its lifecycle: the "
            "pending photo path, the route to return to, whether the upload has "
            "started, and the final result and image shown on /plant_analysis."
        ),
        "details": (
            "The pending image path and previous route are also mirrored into "
            "sessionStorage so a WebView reload (iOS can kill it while the "
            "camera is open) does not lose an in-flight scan. The result and "
            "image are kept in memory only, so reloading on /plant_analysis "
            "sends the user back to previousPath."
        ),
        "symbols": {
            "PENDING_IMAGE_KEY": "sessionStorage key for the pending photo path ('scan-pending-image-path').",
            "PREVIOUS_PATH_KEY": "sessionStorage key for the route to return to ('scan-previous-path').",
            "ScanStore": (
                "Store shape: previousPath, pendingImagePath, imageSrc, result, "
                "scanStarted and the actions setPendingScan, markScanStarted, "
                "setResult, clearPending and reset."
            ),
            "readStoredScan": {
                "description": "Reads the persisted previous path and pending image path from sessionStorage.",
                "returns": "{ previousPath, pendingImagePath }, defaulting to '/home' and null (always the defaults during server rendering).",
            },
            "persistPendingScan": {
                "description": "Saves the previous path and pending image path to sessionStorage.",
                "params": {
                    "previousPath": "Route the user started the scan from.",
                    "imagePath": "Device file path of the captured photo.",
                },
            },
            "clearPersistedScan": {"description": "Removes both scan keys from sessionStorage."},
            "stored": "Persisted values read once at module load and used as the store's initial state.",
            "useScanStore": "Zustand hook for the scan lifecycle state described above.",
            "useScanStore.setPendingScan": {
                "description": "Starts a new scan: persists and stores the path and return route and clears any previous result, image and started flag.",
                "params": {
                    "previousPath": "Route to return to after the scan or on failure.",
                    "imagePath": "Device file path of the photo to upload.",
                },
            },
            "useScanStore.markScanStarted": {
                "description": "Sets scanStarted if it is not already set.",
                "returns": "True the first time (caller should start the upload), false if a scan is already running.",
                "notes": "Prevents duplicate scan_plant calls when React Strict Mode runs the effect twice.",
            },
            "useScanStore.setResult": {
                "description": "Stores a finished result and its image, clears the pending path and the sessionStorage copy.",
                "params": {
                    "result": "The PlantScanResult to show on /plant_analysis.",
                    "imageSrc": "Image to display (data URL from the backend, or base64 from the collection).",
                },
            },
            "useScanStore.clearPending": {
                "description": "Drops the pending image path and started flag (used after a failed scan) and clears sessionStorage.",
            },
            "useScanStore.reset": {
                "description": "Restores every field to its initial value (previousPath '/home') and clears sessionStorage; called on login, sign-up and logout.",
            },
        },
    },
    "src/features/plant_scan/types.ts": {
        "summary": (
            "Hand-written TypeScript mirrors of the backend's response types "
            "for scans, home, collection, community finds, leaderboard, map and "
            "profile. src/generated/types.ts re-exports most of these for the "
            "generated command bindings."
        ),
        "details": (
            "Field names use snake_case to match the backend JSON, except the "
            "GBIF fields, which use GBIF's camelCase. These types must be kept "
            "in sync with the Rust structs by hand. ScanPlantPayload is also "
            "declared separately in src/generated/types.ts."
        ),
        "symbols": {
            "PlantRarity": (
                "Rarity tiers: Common, Uncommon, Rare, SuperRare, Exotic. A "
                "narrower three-value PlantRarity with the same name exists in "
                "features/profile/types/profileTypes.ts."
            ),
            "PlantConfidence": "Model confidence in the identification: High, Medium or Low.",
            "Identification": "Core identification: common name, scientific name and family (each nullable), confidence and nullable rarity.",
            "Care": "Care guide text for light, watering, soil and temperature; each may be null.",
            "Toxicity": "Toxicity notes for humans and pets; each may be null.",
            "PlantSections": "Detailed sections: appearance, nullable native range, nullable care, a list of interesting facts and nullable toxicity.",
            "IdentificationNotes": "Explanation of the identification: reasoning summary and uncertainty, both nullable.",
            "PlantScan": "Full AI identification for one photo: is_plant flag, identification, summary, sections and identification notes. Returned by get_plant_scan.",
            "PlantGeoData": "One GBIF occurrence record: species name and nullable decimal latitude and longitude.",
            "GbifResponse": "Result of get_plant_geo_distribution: occurrence records and the total record count.",
            "DailyMatch": "The daily quest a scan satisfied: quest key and common name.",
            "PlantScanResult": "Outcome of a scan: the PlantScan plus xp_awarded, is_new_species, the matched daily quest (or null) and leveled_up.",
            "DailyPlantQuest": "One of today's quests as returned by get_home: key, names, rarity, XP reward, found flag and optional base64 image.",
            "HomeResponse": "Result of get_home: first name, level, rank title, XP, max XP and the day's quests.",
            "CollectionPlant": "A plant the user has found: id, names, nullable rarity, found_on date string and optional base64 image.",
            "RecentFind": "A community find from get_recent_finds: the CollectionPlant plus the finder's first and last names (nullable).",
            "LeaderboardUser": "One leaderboard entry from get_leaderboard: user id, names, XP, level and rank title.",
            "ImageGeolocation": "Latitude and longitude of a photo.",
            "UserPlantImageLocation": "One of the user's photos for the map (get_user_image_locations): image id, common name, optional location and optional thumbnail data URL.",
            "ProfileRank": "Rank block of the profile: level, rank name, next rank name, current XP and XP needed for the next rank.",
            "ProfileStats": "Profile stats: total scans, unique species and current streak in days.",
            "ProfileResponse": "Result of get_profile: names, joined_at timestamp, rank, stats and the list of found plants.",
            "ScanPlantPayload": "Result of scan_plant: the PlantScanResult and the uploaded image as a data URL.",
        },
    },
    # ------------------------------------------------------------------
    # src/features/profile
    # ------------------------------------------------------------------
    "src/features/profile/components/FoundPlantComponent.tsx": {
        "summary": (
            "Card for one plant in the user's collection, used on /collection "
            "and /profile. Tapping the card opens that plant's full analysis; "
            "tapping the photo opens it full screen."
        ),
        "symbols": {
            "Props": "Card props: plant id, optional base64 image, common and scientific names, nullable rarity and found-on date.",
            "RARITY_VARIANT": (
                "Badge variant per rarity: Common default, Uncommon secondary, "
                "Rare outline. This is the reverse of the mapping used on the "
                "other pages, and it has no entries for SuperRare or Exotic, so "
                "those badges get an undefined variant."
            ),
            "handlePlantClick": {
                "description": (
                    "Loads the stored scan with the get_plant_scan command, "
                    "places it in useScanStore as a result with no rewards, sets "
                    "previousPath to the current route, and replaces the route "
                    "with /plant_analysis."
                ),
                "params": {
                    "id": "Plant (scan) id passed as plantId.",
                    "imageBase64": "Image to show on the analysis page; an empty string when null.",
                    "previousPath": "Current route, used by the analysis page's back button.",
                    "router": "The Next.js app router.",
                },
                "errors": "Failures are not caught; the promise rejects silently and the user stays on the page with no feedback.",
                "notes": (
                    "previousPath is assigned directly on the store's state "
                    "object instead of through set, so subscribers are not "
                    "notified; it works because the analysis page reads the "
                    "store when it mounts. router.replace means the collection "
                    "or profile entry is replaced in history."
                ),
            },
            "FoundPlantComponent": {
                "description": (
                    "Renders the card with names, image (or a grey placeholder), "
                    "rarity badge and found-on date. Clicks on the image are "
                    "stopped from reaching the card so they open the "
                    "ImageViewer only."
                ),
                "params": {
                    "{ id, imageBase64, foundOn, commonName, scientificName, rarity, }": "See Props.",
                },
                "notes": "foundOn is shown exactly as received from the backend.",
            },
        },
    },
    "src/features/profile/types/profileTypes.ts": {
        "summary": (
            "Mock profile types and fixture from before the backend existed. "
            "Only PlantRarity is still imported (by the collection and profile "
            "pages and FoundPlantComponent)."
        ),
        "symbols": {
            "PlantRarity": (
                "Three-value rarity (Common, Uncommon, Rare). It duplicates and "
                "is narrower than the five-value PlantRarity in "
                "features/plant_scan/types; pages cast real data to it."
            ),
            "FoundPlant": "Mock found-plant shape in camelCase with a Tailwind tileClass. Unused.",
            "ProfileAccountInfo": "Mock profile shape (names, joined date, rank, stats, found plants) in camelCase. Unused; the real shape is ProfileResponse.",
            "FAKE_PROFILE": "Unused mock profile fixture for 'Grayson Rieger' with made-up rank, stats and three found plants.",
        },
    },
    # ------------------------------------------------------------------
    # src/hooks
    # ------------------------------------------------------------------
    "src/hooks/use-canvas-effect.ts": {
        "summary": "React hook that mounts an animated 2D canvas effect on a canvas ref using mountCanvasEffect, and re-exports its types.",
        "symbols": {
            "useCanvasEffect": {
                "description": (
                    "Mounts the effect after render and disposes it on unmount. "
                    "The latest setup callback is kept in a ref, so an inline "
                    "function does not cause a remount on every render."
                ),
                "params": {
                    "ref": "Ref to the canvas element.",
                    "setup": "Called once the canvas has a size; returns the per-frame function.",
                    "options?": "Optional CanvasEffectOptions. They are compared by JSON value, so a new object with the same values does not remount.",
                },
                "notes": "Used only by Swirl.",
            },
        },
    },
    "src/hooks/use-mobile.ts": {
        "summary": (
            "shadcn helper hook that reports whether the viewport is narrower "
            "than 768 px. Only used by the shadcn sidebar component, which the "
            "app does not use."
        ),
        "symbols": {
            "MOBILE_BREAKPOINT": "Width in pixels (768) below which the viewport counts as mobile.",
            "useIsMobile": {
                "description": "Tracks the viewport width with a media query listener.",
                "returns": "True when the window is narrower than 768 px; false before mount.",
            },
        },
    },
    "src/hooks/useTauriEvent.ts": {
        "summary": "Hook that subscribes to a Tauri event for the lifetime of a component. Not currently used.",
        "symbols": {
            "useTauriEvent": {
                "description": "Registers a listener with @tauri-apps/api/event listen and unregisters it on unmount or when the inputs change.",
                "params": {
                    "eventName": "Name of the Tauri event.",
                    "eventCallback": "Called with each event payload. Pass a stable function, or the listener is re-registered every render.",
                },
            },
        },
    },
    "src/hooks/useTauriStore.ts": {
        "summary": (
            "Thin typed wrapper around the Tauri store plugin file store.json. "
            "Its only key is version, and nothing in the app uses it outside "
            "useTauriStoreValue."
        ),
        "symbols": {
            "TauriStore": "Typed schema of store.json; currently just version.",
            "tauriStoreDefaults": "Default values written when the store is first loaded (version '1').",
            "loadStore": {
                "description": "Loads store.json with the defaults and auto-save disabled.",
                "returns": "The plugin Store instance.",
            },
            "set": {
                "description": "Writes one key and saves the store to disk.",
                "params": {"key": "Store key.", "value": "New value for that key."},
            },
            "get": {
                "description": "Reads one key from the store.",
                "params": {"key": "Store key."},
                "returns": "The stored value, cast to the schema type.",
            },
            "useTauriStore": {
                "description": "Returns the get and set helpers.",
                "returns": "{ set, get }.",
            },
        },
    },
    "src/hooks/useTauriStoreValue.ts": {
        "summary": "useState-like hook bound to one key of the Tauri store. Not currently used.",
        "symbols": {
            "SetStoreValue": "Setter type: accepts a new value or an updater function, like React's setState.",
            "useTauriStoreValue": {
                "description": "Starts with the default value, loads the persisted value asynchronously, and returns it with a setter that also writes to disk.",
                "params": {"key": "The TauriStore key to bind."},
                "returns": "A [value, setValue] tuple.",
            },
            "useTauriStoreValue.setValue": {
                "description": "Updates local state and saves the new value to the store without waiting for the write.",
                "params": {"update": "New value or an updater function receiving the previous value."},
            },
        },
    },
    # ------------------------------------------------------------------
    # src/lib
    # ------------------------------------------------------------------
    "src/lib/camera.ts": {
        "summary": (
            "Frontend bindings for the custom native camera plugin: take a "
            "photo, and recover a photo whose scan was interrupted when iOS "
            "reloaded the WebView."
        ),
        "details": (
            "Invokes the plugin commands plugin:camera|take_photo and "
            "plugin:camera|take_pending_photo directly. The generated bindings "
            "also contain takePhoto and takePendingPhoto (calling take_photo "
            "and take_pending_photo without the plugin prefix), but the app "
            "uses these versions. TODO comments say the commands should move "
            "into the main crate and this file should be replaced by generated "
            "code."
        ),
        "symbols": {
            "pendingPhotoRecovery": (
                "Cached promise of the one-time native recovery call. It is set "
                "on first use and never reset, so the native command runs at "
                "most once per app session."
            ),
            "takePhoto": {
                "description": "Opens the native camera and waits for the user to take a photo.",
                "returns": "The device file path of the saved photo.",
                "errors": "Rejects with the plugin's error (the caller shows a 'Camera failed' toast).",
            },
            "takePendingPhoto": {
                "description": (
                    "On first call, asks the plugin for a photo saved before "
                    "the WebView reloaded and, if one exists and nothing is "
                    "pending, records it with useScanStore.setPendingScan. Every "
                    "call then resolves to the store's current pendingImagePath."
                ),
                "returns": "The pending image path, or null.",
                "errors": "Native errors are swallowed and treated as no pending photo.",
                "notes": (
                    "The native command deletes the saved path, so it can only "
                    "be recovered once. Reading the store afterwards (rather "
                    "than caching the path) ensures a failed scan, which clears "
                    "the path, does not send the user back to the analyzing "
                    "screen."
                ),
            },
        },
    },
    "src/lib/canvas-effect-core.ts": {
        "summary": (
            "Framework-independent engine for animated 2D canvas effects. It "
            "sizes the canvas to physical pixels within a pixel budget and runs "
            "a requestAnimationFrame loop that pauses offscreen, in hidden tabs "
            "and under reduced motion."
        ),
        "symbols": {
            "DEFAULT_MAX_PIXEL_COUNT": "Default cap on canvas backing-store pixels (1920 x 1080 x 2), since effects compute every pixel in JavaScript.",
            "CanvasEffectOptions": (
                "Options: maxPixelCount, minPixelRatio (supersampling floor), "
                "respectReducedMotion (default true), pauseOffscreen (default "
                "true) and coordinates ('device' or 'css' pixel space)."
            ),
            "CanvasEffectFrame": "Per-frame callback receiving dt in milliseconds (clamped to 100) and the same delta in 60fps frames.",
            "FRAME_MS_60": "Length of one 60fps frame in milliseconds.",
            "CanvasEffectSetup": "Setup callback receiving the 2D context, the canvas and an AbortSignal; returns the frame function, or nothing to draw a single frame.",
            "CanvasEffectHandle": "Handle returned by mountCanvasEffect with a dispose method.",
            "MAX_FRAME_DELTA": "Largest dt passed to a frame (100 ms), so a resumed tab does not jump.",
            "noop": "Handle with an empty dispose, returned when there is no canvas or 2D context.",
            "mountCanvasEffect": {
                "description": (
                    "Gets the 2D context, observes size, viewport intersection, "
                    "tab visibility and reduced-motion changes, runs setup once "
                    "the canvas has a real size, and drives the frame loop."
                ),
                "params": {
                    "canvas": "Canvas element; may be null or undefined, in which case nothing happens.",
                    "setup": "The effect's setup callback.",
                    "options": "CanvasEffectOptions (defaults to {}).",
                },
                "returns": "A CanvasEffectHandle; dispose stops the loop, aborts the signal and disconnects all observers.",
            },
            "mountCanvasEffect.applySize": {
                "description": (
                    "Resizes the backing store to the element's physical pixel "
                    "size, scaled down by area to fit maxPixelCount, and "
                    "re-applies the CSS scale transform in 'css' mode."
                ),
                "returns": "True if the canvas size actually changed.",
            },
            "mountCanvasEffect.renderStaticFrame": {"description": "Draws one frame with dt 0; used for the first paint, after resizes while paused, and under reduced motion."},
            "mountCanvasEffect.tick": {
                "description": "requestAnimationFrame callback: computes the clamped delta, calls the frame function and schedules the next tick.",
                "params": {"now": "Timestamp supplied by requestAnimationFrame."},
            },
            "mountCanvasEffect.shouldAnimate": {
                "description": "Checks whether the loop may run.",
                "returns": "True when not disposed, motion is allowed, the canvas is visible and the tab is visible.",
            },
            "mountCanvasEffect.syncLoop": {"description": "Starts or cancels the animation loop to match shouldAnimate."},
            "mountCanvasEffect.ensureSetUp": {"description": "Runs setup once the canvas is larger than 1 x 1, paints the first frame and starts the loop."},
            "mountCanvasEffect.handleTabVisibility": {"description": "visibilitychange handler that records whether the tab is visible and resyncs the loop."},
        },
    },
    "src/lib/error.ts": {
        "summary": "Turns any rejected value from a Tauri command into a user-facing message.",
        "symbols": {
            "FALLBACK": "Default message: 'Something went wrong'.",
            "getErrorMessage": {
                "description": (
                    "Tauri invoke rejects with a string or a { message } object "
                    "rather than an Error, so this checks for a string, an "
                    "Error, or an object with a string message, in that order."
                ),
                "params": {
                    "error": "The rejected value (for example mutation.error).",
                    "fallback": "Message used when nothing usable is found (defaults to FALLBACK).",
                },
                "returns": "The trimmed message, or the fallback if empty or unrecognised.",
                "notes": "Used by the login, sign-up, setup and reset-password forms.",
            },
        },
    },
    "src/lib/motion-core.ts": {
        "summary": (
            "Animation utilities: cached reduced-motion detection, scroll "
            "reveal, staggered delays, one-shot CSS animations and a View "
            "Transitions wrapper. Only the reduced-motion functions are used "
            "(by canvas-effect-core)."
        ),
        "details": (
            "The reveal, stagger and transition helpers rely on bk-* CSS "
            "classes and the data-bk-transition attribute, which are not "
            "defined in this project's stylesheet, so they would have no visual "
            "effect as-is."
        ),
        "symbols": {
            "isBrowser": "True when window and document exist (false during server rendering).",
            "_reducedMotion": "Cached result of the prefers-reduced-motion media query, kept current by a change listener.",
            "_reducedMotionMql": "The prefers-reduced-motion MediaQueryList, or null outside the browser.",
            "_reducedMotionListeners": "Set of subscribers notified when the reduced-motion setting changes.",
            "prefersReducedMotion": {
                "description": "Reads the cached reduced-motion preference.",
                "returns": "True if the user has asked the OS for reduced motion.",
            },
            "onReducedMotionChange": {
                "description": "Subscribes to reduced-motion setting changes.",
                "params": {"listener": "Called with the new value whenever the setting changes."},
                "returns": "An unsubscribe function.",
            },
            "RevealOptions": "Options for observeReveal: rootMargin, threshold, once and delay.",
            "DEFAULT_REVEAL_OPTS": "Default reveal options: fire slightly before entering the viewport, threshold 0, once, no delay.",
            "observeReveal": {
                "description": "Adds the bk-reveal-in class to an element when it scrolls into view; under reduced motion it reveals immediately.",
                "params": {"el": "Element already carrying the bk-reveal class.", "opts?": "Optional RevealOptions."},
                "returns": "A cleanup function that disconnects the observer.",
                "notes": "Unused.",
            },
            "StaggerOptions": "Options for staggerChildren: delay between siblings, initial delay and a child selector.",
            "staggerChildren": {
                "description": "Sets increasing animation-delay values on the direct children of an element so they animate in sequence; skipped under reduced motion.",
                "params": {"root": "Parent element.", "opts?": "Optional StaggerOptions (default 75 ms apart)."},
                "returns": "A cleanup function that clears the delays.",
                "notes": "Unused.",
            },
            "triggerAnimation": {
                "description": "Restarts a CSS animation by re-adding a class, then removes it when the animation ends.",
                "params": {"el": "Target element.", "className": "Class that applies the animation."},
                "returns": "A promise that resolves when the animation ends, or immediately under reduced motion.",
                "notes": "Unused.",
            },
            "ViewTransitionLike": "Minimal shape of a View Transition object: ready, finished and updateCallbackDone promises.",
            "PageTransition": "Names of page transition recipes: 'hard-wipe', 'color-block' or 'stamp'.",
            "startViewTransition": {
                "description": (
                    "Runs a DOM update inside document.startViewTransition when "
                    "supported, optionally tagging it with a recipe attribute "
                    "and transition types; otherwise just runs the callback."
                ),
                "params": {
                    "callback": "The DOM update to perform.",
                    "recipe?": "Optional PageTransition applied for this transition only.",
                    "options?": "Optional { types } used to tag the transition for CSS.",
                },
                "returns": "The transition object, or null when unsupported or under reduced motion.",
                "notes": "Unused.",
            },
        },
    },
    "src/lib/utils.ts": {
        "summary": "General helpers: Tailwind class merging and date formatting.",
        "symbols": {
            "cn": {
                "description": "Combines class names with clsx and resolves Tailwind conflicts with tailwind-merge.",
                "params": {"...inputs": "Class strings, arrays or conditional objects."},
                "returns": "The merged class string.",
            },
            "chronoUtcDateTimeToUserFriendlyFormat": {
                "description": "Formats an ISO timestamp from the backend as month and year in US English.",
                "params": {"dateTime": "ISO 8601 timestamp, for example '2025-03-14T18:30:00Z'."},
                "returns": "A string such as 'March 2025'.",
                "notes": "Used for the 'Joined ...' label on the profile page. Uses the device's local time zone.",
            },
        },
    },
    # ------------------------------------------------------------------
    # src/stores, src/types
    # ------------------------------------------------------------------
    "src/stores/useAppStore.ts": {
        "summary": "App-wide Zustand store (not related to the iOS App Store). It currently only records whether the server was unreachable at launch.",
        "symbols": {
            "Store": "Shape of the store: isConfirmedOffline and setValues.",
            "useAppStore": (
                "Zustand hook. isConfirmedOffline is set to true by the splash "
                "screen when ping fails and read by the home page to show the "
                "offline notice. It is never reset during the session."
            ),
            "useAppStore.setValues": {
                "description": "Merges the given fields into the store.",
                "params": {"values": "Partial store values."},
            },
        },
    },
    "src/types/motionConstants.ts": {
        "summary": "Shared motion transition settings.",
        "symbols": {
            "TRANSITION1": (
                "Default page and card entrance transition: 0.5 s with a "
                "slightly overshooting ease curve. Used across most pages."
            ),
        },
    },
    "src/types/result.ts": {
        "summary": "A small Rust-style Result type with ok and err constructors. Not currently used.",
        "symbols": {
            "Result": "Tagged union: { type: 'ok', value } or { type: 'err', error }.",
            "ok": {
                "description": "Builds a successful Result.",
                "params": {"value": "The success value."},
                "returns": "{ type: 'ok', value }.",
            },
            "err": {
                "description": "Builds a failed Result.",
                "params": {"error": "The error value."},
                "returns": "{ type: 'err', error }.",
            },
        },
    },
}
