use std::{
    collections::HashMap,
    net::SocketAddr,
    sync::Mutex,
    time::{Duration, Instant},
};

use axum::{
    extract::{ConnectInfo, Request, State},
    http::StatusCode,
    middleware::Next,
    response::{IntoResponse, Response},
};

use crate::state::AppState;

const WINDOW: Duration = Duration::from_secs(60);

#[derive(Clone, Copy, Debug)]
pub enum AuthRateBucket {
    LoginRegister,
    Refresh,
    EmailVerify,
}

impl AuthRateBucket {
    fn key(self) -> &'static str {
        match self {
            Self::LoginRegister => "login_register",
            Self::Refresh => "refresh",
            Self::EmailVerify => "email_verify",
        }
    }

    fn limit(self) -> usize {
        match self {
            Self::LoginRegister => 10,
            Self::Refresh => 20,
            Self::EmailVerify => 5,
        }
    }

    /// TODO: these paths could change, meaning this is a bit fragile
    fn from_path(path: &str) -> Option<Self> {
        match path {
            "/auth/login" | "/auth/register/start" => Some(Self::LoginRegister),
            "/auth/refresh" => Some(Self::Refresh),
            "/auth/email/verify" | "/auth/email/resend" => Some(Self::EmailVerify),
            _ => None,
        }
    }
}

#[derive(Default)]
pub struct RateLimiter {
    // (client_ip, bucket) -> timestamps of recent requests within the window
    entries: Mutex<HashMap<(String, &'static str), Vec<Instant>>>,
}

impl RateLimiter {
    pub fn new() -> Self {
        Self::default()
    }

    /// Returns true if the request is allowed.
    pub fn check(&self, client_ip: &str, bucket: AuthRateBucket) -> bool {
        let now = Instant::now();
        let key = (client_ip.to_string(), bucket.key());
        let limit = bucket.limit();

        let mut entries = self.entries.lock().unwrap_or_else(|e| e.into_inner());
        let stamps = entries.entry(key).or_default();
        stamps.retain(|t| now.duration_since(*t) < WINDOW);

        if stamps.len() >= limit {
            return false;
        }

        stamps.push(now);
        true
    }
}

pub async fn rate_limit_auth(
    State(state): State<AppState>,
    request: Request,
    next: Next,
) -> Response {
    let Some(bucket) = AuthRateBucket::from_path(request.uri().path()) else {
        return next.run(request).await;
    };

    let client_ip = request
        .extensions()
        .get::<ConnectInfo<SocketAddr>>()
        .map(|info| info.0.ip().to_string())
        .unwrap_or_else(|| "unknown".to_string());

    if !state.rate_limiter.check(&client_ip, bucket) {
        return (StatusCode::TOO_MANY_REQUESTS, "too many requests").into_response();
    }

    next.run(request).await
}
