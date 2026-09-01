use crate::{ClientError, ClientResult};

pub async fn parse_json_response<T>(response: reqwest::Response) -> ClientResult<T>
where
    T: serde::de::DeserializeOwned,
{
    let status = response.status();
    let body = response.text().await?;

    if !status.is_success() {
        return Err(ClientError::RequestFailed {
            status: status.as_u16(),
            body,
        });
    }

    serde_json::from_str(&body).map_err(|source| ClientError::JsonDecode { source, body })
}

pub async fn parse_empty_response(response: reqwest::Response) -> ClientResult<()> {
    let status = response.status();
    let body = response.text().await?;

    if !status.is_success() {
        return Err(ClientError::RequestFailed {
            status: status.as_u16(),
            body,
        });
    }

    Ok(())
}
