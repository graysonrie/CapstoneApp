use std::sync::Arc;

use sea_orm::DatabaseConnection;

use crate::{
    app_config::AppConfig,
    clock::AppClock,
    features::{
        email_server::sender_trait::EmailSender, file_storage::file_storage_trait::FileStorage,
    },
};

#[derive(Clone)]
pub struct AppState {
    pub db: DatabaseConnection,
    pub email_sender: Arc<dyn EmailSender + Send + Sync>,
    pub file_storage: Arc<dyn FileStorage + Send + Sync>,
    pub clock: Arc<AppClock>,
    pub app_config: Arc<AppConfig>,
}
