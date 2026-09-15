use crate::{ApiClient, ClientResult, util::parse_json_response};
use server_types::prelude::*;

pub struct PlantScanClient<'a> {
    api: &'a ApiClient,
}

impl<'a> PlantScanClient<'a> {
    pub fn new(api: &'a ApiClient) -> Self {
        Self { api }
    }

    pub async fn scan_plant(
        &self,
        image_bytes: Vec<u8>,
        file_name: &str,
        mime: &str,
    ) -> ClientResult<PlantScanResult> {
        let part = reqwest::multipart::Part::bytes(image_bytes)
            .file_name(file_name.to_string())
            .mime_str(mime)?;
        let form = reqwest::multipart::Form::new().part("image", part);
        let request = self
            .api
            .http
            .post(self.api.base_url.join("/plant-scan")?.to_string())
            .multipart(form);
        let response = self.api.authenticated_request(request)?.send().await?;
        parse_json_response(response).await
    }

    pub async fn get_home(&self) -> ClientResult<HomeResponse> {
        let request = self
            .api
            .http
            .get(self.api.base_url.join("/home")?.to_string());
        let response = self.api.authenticated_request(request)?.send().await?;
        parse_json_response(response).await
    }

    pub async fn get_profile(&self) -> ClientResult<ProfileResponse> {
        let request = self
            .api
            .http
            .get(self.api.base_url.join("/user/me")?.to_string());
        let response = self.api.authenticated_request(request)?.send().await?;
        parse_json_response(response).await
    }
}
