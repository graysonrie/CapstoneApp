pub mod clients;
mod util;
use clients::{AuthClient, ClockClient, TestClient, UserClient};
use reqwest::RequestBuilder;
use std::sync::RwLock;
use url::Url;

use crate::clients::DevClient;

const DEFAULT_SERVER_ENDPOINT: &str = "http://127.0.0.1:3001";

pub struct ApiClient {
    pub http: reqwest::Client,
    base_url: Url,
    auth_token: RwLock<Option<String>>,
    refresh_token: RwLock<Option<String>>,
}

impl Default for ApiClient {
    fn default() -> Self {
        Self::new(DEFAULT_SERVER_ENDPOINT)
    }
}

impl ApiClient {
    pub fn new(server_endpoint: &str) -> Self {
        let base_url = Url::parse(server_endpoint).unwrap();
        Self {
            http: reqwest::Client::new(),
            base_url,
            auth_token: RwLock::new(None),
            refresh_token: RwLock::new(None),
        }
    }

    pub fn set_auth_token(&self, token: String) -> anyhow::Result<()> {
        let mut auth_token = self
            .auth_token
            .write()
            .map_err(|_| anyhow::anyhow!("auth token lock poisoned"))?;
        *auth_token = Some(token);
        Ok(())
    }

    pub fn clear_auth_token(&self) -> anyhow::Result<()> {
        let mut auth_token = self
            .auth_token
            .write()
            .map_err(|_| anyhow::anyhow!("auth token lock poisoned"))?;
        *auth_token = None;
        Ok(())
    }

    pub fn set_refresh_token(&self, token: String) -> anyhow::Result<()> {
        let mut refresh_token = self
            .refresh_token
            .write()
            .map_err(|_| anyhow::anyhow!("refresh token lock poisoned"))?;
        *refresh_token = Some(token);
        Ok(())
    }

    pub fn clear_refresh_token(&self) -> anyhow::Result<()> {
        let mut refresh_token = self
            .refresh_token
            .write()
            .map_err(|_| anyhow::anyhow!("refresh token lock poisoned"))?;
        *refresh_token = None;
        Ok(())
    }

    pub fn stored_refresh_token(&self) -> anyhow::Result<String> {
        self.refresh_token
            .read()
            .map_err(|_| anyhow::anyhow!("refresh token lock poisoned"))?
            .clone()
            .ok_or_else(|| anyhow::anyhow!("no refresh token has been saved; call login first"))
    }

    pub(crate) fn refresh_token(&self) -> anyhow::Result<String> {
        self.stored_refresh_token()
    }

    pub(crate) fn authenticated_request(
        &self,
        request: RequestBuilder,
    ) -> anyhow::Result<RequestBuilder> {
        let token = self
            .auth_token
            .read()
            .map_err(|_| anyhow::anyhow!("auth token lock poisoned"))?
            .clone()
            .ok_or_else(|| anyhow::anyhow!("no auth token has been saved; call login first"))?;

        Ok(request.bearer_auth(token))
    }

    pub fn test_client(&self) -> TestClient<'_> {
        TestClient::new(self)
    }

    pub fn auth_client(&self) -> AuthClient<'_> {
        AuthClient::new(self)
    }

    pub fn user_client(&self) -> UserClient<'_> {
        UserClient::new(self)
    }

    pub fn clock_client(&self) -> ClockClient<'_> {
        ClockClient::new(self)
    }

    pub fn dev_client(&self) -> DevClient<'_> {
        DevClient::new(self)
    }
}
