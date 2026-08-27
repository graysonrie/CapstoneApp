use std::{fs, sync::Arc, time::Duration};

use tb_client::ApiClient;

use crate::{
    app_config::{
        AppConfig, AuthConfig, DbConfig, FileStorageConfig, LocalSqliteConfig, ServerConfig,
    },
    app_router,
    clock::AppClock,
    features::{
        self, email_server::sender_trait::MockEmailSender,
        file_storage::file_storage_trait::LocalFileStorage,
    },
    state::AppState,
    test_server::TestServer,
};

pub fn default_app_config() -> AppConfig {
    let db_id = uuid::Uuid::new_v4();

    AppConfig {
        server: ServerConfig {
            port: 0,
            host: "127.0.0.1".to_string(),
        },
        auth: AuthConfig {
            enforce_email_domain: None,
            jwt_secret: "change-me".to_string(),
            access_token_ttl: "15m".to_string(),
            refresh_token_ttl: "15d".to_string(),
            require_email_verification: true,
        },
        db: DbConfig {
            url: "".to_string(),
            local_sqlite: Some(LocalSqliteConfig {
                enabled: true,
                db_path: format!("./{db_id}.db"),
            }),
        },
        file_storage: FileStorageConfig {
            use_local_file_storage: true,
            local_file_storage_directory_path: Some("../TEST_LOCAL_SERVER".to_string()),
        },
    }
}

pub async fn default_local_state(config: AppConfig) -> AppState {
    let db = features::db::get_database_connection(&config)
        .await
        .unwrap();

    AppState {
        db,
        file_storage: Arc::new(LocalFileStorage::new_from_config(&config)),
        email_sender: Arc::new(MockEmailSender),
        clock: Arc::new(AppClock::new()),
        app_config: Arc::new(config.clone()),
    }
}

pub async fn default_test_server() -> TestServer {
    let config = default_app_config();
    let state = default_local_state(config.clone()).await;

    let routes = app_router(state, &config.clone());
    TestServer::spawn(routes, config).await
}

async fn remove_db_file(path: &str) {
    for _ in 0..10 {
        if fs::remove_file(path).is_ok() {
            return;
        }
        tokio::time::sleep(Duration::from_millis(50)).await;
    }
    eprintln!("Error cleaning up SQLite DB file at {path}");
}

pub async fn clean_up_test_server(server: TestServer) {
    let db_path = server
        .config
        .db
        .local_sqlite
        .as_ref()
        .map(|db_config| db_config.db_path.clone());

    server.shutdown().await;

    if let Some(db_path) = db_path {
        remove_db_file(&db_path).await;
    }
}

pub struct TestFixture {
    pub client: ApiClient,
    server: Option<TestServer>,
}

impl TestFixture {
    pub async fn new() -> Self {
        let test_server = default_test_server().await;
        let client = ApiClient::new(&test_server.addr);

        Self {
            client,
            server: Some(test_server),
        }
    }

    pub async fn finish(mut self) {
        if let Some(server) = self.server.take() {
            clean_up_test_server(server).await;
        }
    }
}

impl Drop for TestFixture {
    fn drop(&mut self) {
        let Some(mut server) = self.server.take() else {
            return;
        };

        // Best-effort cleanup when a test panics before `finish()`.
        // Must not block the tokio runtime worker (that causes a deadlock).
        let db_path = server
            .config
            .db
            .local_sqlite
            .as_ref()
            .map(|db_config| db_config.db_path.clone());
        server.signal_shutdown();

        if let Some(db_path) = db_path {
            std::thread::spawn(move || {
                for _ in 0..10 {
                    if fs::remove_file(&db_path).is_ok() {
                        return;
                    }
                    std::thread::sleep(Duration::from_millis(50));
                }
                eprintln!("Error cleaning up SQLite DB file at {db_path}");
            });
        }
    }
}
