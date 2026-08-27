use crate::{ApiClient, util::parse_json_response};
use server_types::prelude::*;

pub struct ClockClient<'a> {
    api: &'a ApiClient,
}

impl<'a> ClockClient<'a> {
    pub fn new(api: &'a ApiClient) -> Self {
        Self { api }
    }

    #[cfg(feature = "dev")]
    pub async fn get(&self) -> Result<ClockStatusResponse, anyhow::Error> {
        let response = self
            .api
            .http
            .get(self.api.base_url.join("/dev/clock")?.to_string())
            .send()
            .await?;
        parse_json_response(response).await
    }

    #[cfg(feature = "dev")]
    pub async fn advance(&self, seconds: i64) -> Result<ClockStatusResponse, anyhow::Error> {
        let response = self
            .api
            .http
            .post(self.api.base_url.join("/dev/clock/advance")?.to_string())
            .json(&AdvanceClockRequest { seconds })
            .send()
            .await?;
        parse_json_response(response).await
    }

    #[cfg(feature = "dev")]
    pub async fn reset(&self) -> Result<ClockStatusResponse, anyhow::Error> {
        let response = self
            .api
            .http
            .post(self.api.base_url.join("/dev/clock/reset")?.to_string())
            .send()
            .await?;
        parse_json_response(response).await
    }
}
