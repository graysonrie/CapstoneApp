use crate::{ApiClient, ClientResult, util::parse_json_response};
use server_types::prelude::*;

pub struct AuthClient<'a> {
    api: &'a ApiClient,
}

impl<'a> AuthClient<'a> {
    pub fn new(api: &'a ApiClient) -> Self {
        Self { api }
    }

    /// Register a new temp user
    pub async fn register_start(
        &self,
        email: &str,
        password: &str,
    ) -> ClientResult<RegisterAttemptedResponse> {
        let response = self
            .api
            .http
            .post(self.api.base_url.join("/auth/register/start")?.to_string())
            .json(&RegisterRequest {
                email: email.to_string(),
                password: password.to_string(),
            })
            .send()
            .await?;
        parse_json_response(response).await
    }

    pub async fn login(&self, email: &str, password: &str) -> ClientResult<LoginResponse> {
        let response = self
            .api
            .http
            .post(self.api.base_url.join("/auth/login")?.to_string())
            .json(&LoginRequest {
                email: email.to_string(),
                password: password.to_string(),
            })
            .send()
            .await?;
        let login_response: LoginResponse = parse_json_response(response).await?;
        self.api
            .set_auth_token(login_response.access_token.clone())?;
        self.api
            .set_refresh_token(login_response.refresh_token.clone())?;
        Ok(login_response)
    }

    pub async fn refresh(&self) -> ClientResult<RefreshTokenResponse> {
        let refresh_token = self.api.refresh_token()?.clone();
        let response = self
            .api
            .http
            .post(self.api.base_url.join("/auth/refresh")?.to_string())
            .json(&RefreshTokenRequest { refresh_token })
            .send()
            .await?;
        let refresh_response: RefreshTokenResponse = parse_json_response(response).await?;
        self.api
            .set_auth_token(refresh_response.access_token.clone())?;
        self.api
            .set_refresh_token(refresh_response.refresh_token.clone())?;
        Ok(refresh_response)
    }

    pub async fn refresh_with_token(
        &self,
        refresh_token: &str,
    ) -> ClientResult<RefreshTokenResponse> {
        let response = self
            .api
            .http
            .post(self.api.base_url.join("/auth/refresh")?.to_string())
            .json(&RefreshTokenRequest {
                refresh_token: refresh_token.to_string(),
            })
            .send()
            .await?;
        parse_json_response(response).await
    }

    pub async fn session(&self) -> ClientResult<SessionResponse> {
        let request = self
            .api
            .http
            .get(self.api.base_url.join("/auth/session")?.to_string());
        let response = self.api.authenticated_request(request)?.send().await?;
        parse_json_response(response).await
    }

    pub async fn verify_email(
        &self,
        email: &str,
        code: &str,
    ) -> ClientResult<VerifyEmailResponse> {
        let response = self
            .api
            .http
            .post(self.api.base_url.join("/auth/email/verify")?.to_string())
            .json(&VerifyEmailRequest {
                email: email.to_string(),
                code: code.to_string(),
            })
            .send()
            .await?;
        parse_json_response(response).await
    }

    pub async fn resend_verification_email(
        &self,
        email: &str,
    ) -> ClientResult<ResendVerificationEmailResponse> {
        let response = self
            .api
            .http
            .post(self.api.base_url.join("/auth/email/resend")?.to_string())
            .json(&ResendVerificationEmailRequest {
                email: email.to_string(),
            })
            .send()
            .await?;
        parse_json_response(response).await
    }

    #[cfg(feature = "dev")]
    /// Only works if the server is running in a dev environment
    pub async fn login_bypass(
        &self,
        email: &str,
        password: &str,
    ) -> ClientResult<LoginResponse> {
        let response = self
            .api
            .http
            .post(self.api.base_url.join("/auth/login/bypass")?.to_string())
            .json(&LoginRequest {
                email: email.to_string(),
                password: password.to_string(),
            })
            .send()
            .await?;
        let login_response: LoginResponse = parse_json_response(response).await?;
        self.api
            .set_auth_token(login_response.access_token.clone())?;
        self.api
            .set_refresh_token(login_response.refresh_token.clone())?;
        Ok(login_response)
    }

    #[cfg(feature = "dev")]
    /// Only works if the server is running in a dev environment
    pub async fn register_start_as_super_admin(
        &self,
        email: &str,
        password: &str,
    ) -> ClientResult<RegisterAttemptedResponse> {
        let response = self
            .api
            .http
            .post(
                self.api
                    .base_url
                    .join("/auth/register/start/superadmin")?
                    .to_string(),
            )
            .json(&RegisterRequest {
                email: email.to_string(),
                password: password.to_string(),
            })
            .send()
            .await?;
        parse_json_response(response).await
    }
}
