pub async fn parse_json_response<T>(response: reqwest::Response) -> Result<T, anyhow::Error>
where
    T: serde::de::DeserializeOwned,
{
    let status = response.status();
    let body = response.text().await?;

    if !status.is_success() {
        anyhow::bail!("request failed with status {status}: {body}");
    }

    serde_json::from_str(&body).map_err(|err| {
        anyhow::anyhow!("failed to decode response body as JSON: {err}; body: {body}")
    })
}

pub async fn parse_empty_response(response: reqwest::Response) -> Result<(), anyhow::Error> {
    let status = response.status();
    let body = response.text().await?;

    if !status.is_success() {
        anyhow::bail!("request failed with status {status}: {body}");
    }

    Ok(())
}
