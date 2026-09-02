pub mod clients;
mod error;
mod util;

pub use clients::{AuthClient, ClockClient, DevClient, UserClient};
pub use error::{ClientError, ClientResult};
use reqwest::RequestBuilder;
use std::sync::RwLock;
use url::Url;

use crate::{clients::MiscClient, error::ClientError::*};

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

    pub fn set_auth_token(&self, token: String) -> ClientResult<()> {
        let mut auth_token = self.auth_token.write().map_err(|_| AuthTokenLockPoisoned)?;
        *auth_token = Some(token);
        Ok(())
    }

    pub fn clear_auth_token(&self) -> ClientResult<()> {
        let mut auth_token = self.auth_token.write().map_err(|_| AuthTokenLockPoisoned)?;
        *auth_token = None;
        Ok(())
    }

    pub fn set_refresh_token(&self, token: String) -> ClientResult<()> {
        let mut refresh_token = self
            .refresh_token
            .write()
            .map_err(|_| RefreshTokenLockPoisoned)?;
        *refresh_token = Some(token);
        Ok(())
    }

    pub fn clear_refresh_token(&self) -> ClientResult<()> {
        let mut refresh_token = self
            .refresh_token
            .write()
            .map_err(|_| RefreshTokenLockPoisoned)?;
        *refresh_token = None;
        Ok(())
    }

    pub fn stored_refresh_token(&self) -> ClientResult<String> {
        self.refresh_token
            .read()
            .map_err(|_| RefreshTokenLockPoisoned)?
            .clone()
            .ok_or(RefreshTokenNotSet)
    }

    pub(crate) fn refresh_token(&self) -> ClientResult<String> {
        self.stored_refresh_token()
    }

    pub(crate) fn authenticated_request(
        &self,
        request: RequestBuilder,
    ) -> ClientResult<RequestBuilder> {
        let token = self
            .auth_token
            .read()
            .map_err(|_| AuthTokenLockPoisoned)?
            .clone()
            .ok_or(AuthTokenNotSet)?;

        Ok(request.bearer_auth(token))
    }

    pub fn misc_client(&self) -> MiscClient<'_> {
        MiscClient::new(self)
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
