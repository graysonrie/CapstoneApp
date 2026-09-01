use crate::{ApiClient, ClientResult, util::parse_empty_response};

pub struct DevClient<'a> {
    api: &'a ApiClient,
}
impl<'a> DevClient<'a> {
    pub fn new(api: &'a ApiClient) -> Self {
        Self { api }
    }

    pub async fn erase_db(&self) -> ClientResult<()> {
        let response = self
            .api
            .http
            .post(self.api.base_url.join("/dev/erase-db")?.to_string())
            .send()
            .await?;
        parse_empty_response(response).await
    }
}
