use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Deserialize, Serialize, Default)]
pub struct AppConfig {
    pub server: ServerConfig,
    pub auth: AuthConfig,
    pub db: DbConfig,
    pub file_storage: FileStorageConfig,
}
#[derive(Clone, Debug, Deserialize, Serialize, Default)]
pub struct AuthConfig {
    pub enforce_email_domain: Option<String>,
    /// Will be parsed by duration-str
    pub access_token_ttl: String,
    /// Will be parsed by duration-str
    pub refresh_token_ttl: String,
    pub jwt_secret: String,
    pub require_email_verification:bool
}

#[derive(Clone, Debug, Deserialize, Serialize, Default)]
pub struct ServerConfig {
    pub port: u16,
    pub host: String,
}

#[derive(Clone, Debug, Deserialize, Serialize, Default)]
pub struct DbConfig {
    pub url: String,
    pub local_sqlite: Option<LocalSqliteConfig>,
}

#[derive(Clone, Debug, Deserialize, Serialize, Default)]
pub struct LocalSqliteConfig {
    pub enabled: bool,
    /// The path where to create the db. Ex: ./the_database.db
    pub db_path: String,
}

#[derive(Clone, Debug, Deserialize, Serialize, Default)]
pub struct FileStorageConfig {
    pub use_local_file_storage: bool,
    pub local_file_storage_directory_path: Option<String>,
}
