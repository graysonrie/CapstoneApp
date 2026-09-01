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
    rate_limit::RateLimiter,
    state::AppState,
};
mod app_config;
mod clock;
mod environment;
pub mod features;
mod rate_limit;
mod state;
mod test_server;

#[cfg(test)]
mod tests;

use config::{Config, Environment, File};

const DEFAULT_JWT_SECRET: &str = "change-me";

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

fn is_weak_jwt_secret(secret: &str) -> bool {
    secret.trim().is_empty() || secret == DEFAULT_JWT_SECRET
}

fn is_loopback_host(host: &str) -> bool {
    matches!(host, "127.0.0.1" | "localhost" | "::1")
}

fn allow_insecure_dev() -> bool {
    std::env::var("APP_ALLOW_INSECURE_DEV")
        .map(|v| v == "1" || v.eq_ignore_ascii_case("true"))
        .unwrap_or(false)
}

fn validate_startup_config(config: &AppConfig) {
    if environment::is_prod() && is_weak_jwt_secret(&config.auth.jwt_secret) {
        panic!(
            "Refusing to start in production with a weak jwt_secret. \
             Set APP__auth__jwt_secret (or auth.jwt_secret) to a strong secret."
        );
    }

    if environment::is_dev() && is_weak_jwt_secret(&config.auth.jwt_secret) {
        tracing::warn!(
            "Using default/weak jwt_secret in Dev. Do not expose this server beyond localhost."
        );
    }

    if environment::is_dev() && !is_loopback_host(&config.server.host) && !allow_insecure_dev() {
        panic!(
            "Refusing to bind Dev server to non-loopback host '{}'. \
             Dev mode mounts unauthenticated bypass routes \
             (/auth/login/bypass, /auth/register/start/superadmin, /user/change-role/bypass, \
             /dev/erase-db, /dev/clock/advance). \
             Bind to 127.0.0.1 or set APP_ALLOW_INSECURE_DEV=1.",
            config.server.host
        );
    }
}

async fn hello_handler() -> Json<HelloResponse> {
    Json(HelloResponse {
        message: "Hello from Axum".to_string(),
    })
}

pub fn app_router(state: AppState, config: &AppConfig) -> Router {
    Router::new()
        .route("/hello", get(hello_handler))
        .merge(auth_router(config, state.clone()))
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
    validate_startup_config(&config);

    let db = features::db::get_database_connection(&config)
        .await
        .unwrap();

    let state = AppState {
        db,
        file_storage: Arc::new(LocalFileStorage::new_from_config(&config)),
        email_sender: Arc::new(MockEmailSender),
        clock: Arc::new(AppClock::new()),
        app_config: Arc::new(config.clone()),
        rate_limiter: Arc::new(RateLimiter::new()),
    };

    let app = app_router(state, &config);

    let addr = format!("{}:{}", config.server.host, config.server.port)
        .parse::<SocketAddr>()
        .expect("Failed to parse server address");

    tracing::info!("Server running on http://{}", addr);

    if environment::is_dev() {
        tracing::warn!(
            "APP IS RUNNING IN DEV MODE - dangerous routes may be mounted: \
             /auth/login/bypass, /auth/register/start/superadmin, /user/change-role/bypass, \
             /dev/erase-db, /dev/clock/advance (bind={})",
            addr
        );
    }

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();

    axum::serve(
        listener,
        app.into_make_service_with_connect_info::<SocketAddr>(),
    )
    .await
    .unwrap();
}
