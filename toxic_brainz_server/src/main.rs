use axum::{Json, Router, routing::get};
use features::{auth::auth_router, clock::routes::clock_router, user::routes::user_router};
use server_types::responses::HelloResponse;
use std::{net::SocketAddr, sync::Arc};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use crate::{
    app_config::AppConfig,
    clock::AppClock,
    features::{
        dev::routes::dev_router, email_server::sender_trait::MockEmailSender,
        file_storage::file_storage_trait::LocalFileStorage,
    },
    state::AppState,
};
mod app_config;
mod clock;
mod environment;
pub mod features;
mod state;
mod test_server;

#[cfg(test)]
mod tests;

use config::{Config, Environment, File};

fn load_config() -> Result<AppConfig, config::ConfigError> {
    Config::builder()
        .add_source(File::with_name("appsettings.ron"))
        .add_source(Environment::with_prefix("APP").separator("__"))
        .build()?
        .try_deserialize()
}

fn init_tracing() {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "debug".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();
}

async fn hello_handler() -> Json<HelloResponse> {
    Json(HelloResponse {
        message: "Hello from Axum".to_string(),
    })
}

pub fn app_router(state: AppState, config: &AppConfig) -> Router {
    Router::new()
        .route("/hello", get(hello_handler))
        .merge(auth_router(config))
        .merge(clock_router())
        .merge(user_router(state.clone()))
        .merge(dev_router())
        .with_state(state)
}

#[tokio::main]
async fn main() {
    dotenv::dotenv().ok();
    init_tracing();
    let config = load_config().expect("Failed to load config");

    let db = features::db::get_database_connection(&config)
        .await
        .unwrap();

    let state = AppState {
        db,
        file_storage: Arc::new(LocalFileStorage::new_from_config(&config)),
        email_sender: Arc::new(MockEmailSender),
        clock: Arc::new(AppClock::new()),
        app_config: Arc::new(config.clone()),
    };

    let app = app_router(state, &config);

    let addr = format!("{}:{}", config.server.host, config.server.port)
        .parse::<SocketAddr>()
        .expect("Failed to parse server address");

    tracing::info!("Server running on http://{}", addr);

    if environment::is_dev() {
        tracing::warn!("APP IS RUNNING IN DEV MODE");
    }

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();

    axum::serve(listener, app).await.unwrap();
}
