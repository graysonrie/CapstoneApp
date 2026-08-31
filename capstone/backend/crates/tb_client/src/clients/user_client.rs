use crate::{ApiClient, util::parse_empty_response};

use server_types::{prelude::*, user::RoleType};

pub struct UserClient<'a> {
    api: &'a ApiClient,
}

impl<'a> UserClient<'a> {
    pub fn new(api: &'a ApiClient) -> Self {
        Self { api }
    }
    pub async fn delete_user(&self, email: &str) -> Result<(), anyhow::Error> {
        let request = self
            .api
            .http
            .post(self.api.base_url.join("/user/delete")?.to_string());
        let response = self
            .api
            .authenticated_request(request)?
            .json(&DeleteUserRequest {
                email: email.to_string(),
            })
            .send()
            .await?;
        parse_empty_response(response).await
    }

    #[cfg(feature = "dev")]
    /// Only works if the server is running in a dev environment
    pub async fn change_role_bypass(
        &self,
        email: &str,
        role: RoleType,
    ) -> Result<(), anyhow::Error> {
        let response = self
            .api
            .http
            .post(
                self.api
                    .base_url
                    .join("/user/change-role/bypass")?
                    .to_string(),
            )
            .json(&ChangeRoleRequest {
                email: email.to_string(),
                role,
            })
            .send()
            .await?;
        parse_empty_response(response).await
    }
}
