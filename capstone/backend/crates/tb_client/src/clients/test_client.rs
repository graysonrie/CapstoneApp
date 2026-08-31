use crate::{ApiClient, util::parse_json_response};
use server_types::prelude::*;

pub struct TestClient<'a> {
    api: &'a ApiClient,
}

impl<'a> TestClient<'a> {
    pub fn new(api: &'a ApiClient) -> Self {
        Self { api }
    }

    pub async fn hello(&self) -> Result<HelloResponse, anyhow::Error> {
        let response = self
            .api
            .http
            .get(self.api.base_url.join("/hello")?.to_string())
            .send()
            .await?;
        let body = parse_json_response(response).await?;
        Ok(body)
    }
}
