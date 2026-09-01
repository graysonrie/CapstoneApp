use log::warn;
use tb_client::ApiClient;

use crate::prelude::*;

type BackendApiState<'a> = State<'a, Arc<ApiClient>>;

#[tauri::command]
pub async fn log_in(
    api: BackendApiState<'_>,
    email: String,
    password: String,
) -> Result<(), String> {
    // Get inner otherwise RA fails to provide autocomplete
    let inner: &Arc<ApiClient> = api.inner();

    let response = inner
        .auth_client()
        .login(&email, &password)
        .await
        .map_err(|e| e.to_string())?;

    inner
        .set_auth_token(response.access_token)
        .map_err(|e| e.to_string())?;

    inner
        .set_refresh_token(response.refresh_token)
        .map_err(|e| e.to_string())?;

    Ok(())
}

#[tauri::command]
pub async fn sign_up(
    api: BackendApiState<'_>,
    email: String,
    password: String,
) -> Result<(), String> {
    // Get inner otherwise RA fails to provide autocomplete
    let inner: &Arc<ApiClient> = api.inner();

    let response = inner
        .auth_client()
        .register_start(&email, &password)
        .await
        .map_err(|e| e.to_string())?;

    // As long as email verification is off, then response should
    // contain the user_id here, indicating success
    if !response.user_id.is_some() {
        return Err("user_id does not exist".to_string());
    }

    log_in(api, email, password).await
}

/// Will return true if the user is currently logged in
#[tauri::command]
pub async fn is_valid_session(api: BackendApiState<'_>) -> Result<bool, String> {
    let inner: &Arc<ApiClient> = api.inner();

    match inner.auth_client().session().await {
        Ok(_) => Ok(true),
        Err(tb_client::ClientError::AuthTokenNotSet) => Ok(false),
        Err(err) => {
            warn!("Client error for is_valid_session: {err}");

            // Access may have expired — try refresh before wiping the session.
            if inner.stored_refresh_token().is_ok() {
                match inner.auth_client().refresh().await {
                    Ok(_) => match inner.auth_client().session().await {
                        Ok(_) => return Ok(true),
                        Err(retry_err) => {
                            warn!("Session still invalid after refresh: {retry_err}");
                        }
                    },
                    Err(refresh_err) => {
                        warn!("Refresh failed during is_valid_session: {refresh_err}");
                    }
                }
            }

            let _ = inner.clear_auth_token();
            let _ = inner.clear_refresh_token();
            Ok(false)
        }
    }
}

#[tauri::command]
pub async fn log_out(api: BackendApiState<'_>) -> Result<(), String> {
    let inner: &Arc<ApiClient> = api.inner();

    if let Err(err) = inner.auth_client().logout().await {
        warn!("Server logout failed (clearing local tokens anyway): {err}");
        let _ = inner.clear_auth_token();
        let _ = inner.clear_refresh_token();
    }

    Ok(())
}
