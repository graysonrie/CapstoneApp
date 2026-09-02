use crate::{ApiClient, ClientResult};

/// Handles routes that don't belong to a certain feature, like a health check
pub struct MiscClient<'a> {
    api: &'a ApiClient,
}

impl<'a> MiscClient<'a> {
    pub fn new(api: &'a ApiClient) -> Self {
        Self { api }
    }

    /// Checks to see if the server can be reached
    pub async fn ping(&self) -> ClientResult<()> {
        self.api
            .http
            .get(self.api.base_url.join("/ping")?.to_string())
            .send()
            .await
            .map(|_| Ok(()))?
    }
}
