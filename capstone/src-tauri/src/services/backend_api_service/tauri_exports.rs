use log::warn;
use serde::Serialize;
use tb_client::ApiClient;

use crate::prelude::*;
use crate::services::token_store;

type BackendApiState<'a> = State<'a, Arc<ApiClient>>;

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct SessionInfo {
    pub profile_complete: bool,
    pub first_name: Option<String>,
    pub email: String,
    pub user_id: i32,
}

fn persist_refresh_token(api: &ApiClient) {
    if let Ok(token) = api.stored_refresh_token() {
        token_store::save_refresh_token(&token);
    }
}

fn clear_local_session(api: &ApiClient) {
    let _ = api.clear_auth_token();
    let _ = api.clear_refresh_token();
    token_store::clear_refresh_token();
}

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
        .map_err(|e| e.user_message())?;

    inner
        .set_auth_token(response.access_token)
        .map_err(|e| e.user_message())?;

    inner
        .set_refresh_token(response.refresh_token.clone())
        .map_err(|e| e.user_message())?;

    token_store::save_refresh_token(&response.refresh_token);

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
        .map_err(|e| e.user_message())?;

    // As long as email verification is off, then response should
    // contain the user_id here, indicating success
    if response.user_id.is_none() {
        return Err("user_id does not exist".to_string());
    }

    log_in(api, email, password).await
}

/// Returns session info if the user is currently logged in, otherwise `None`.
#[tauri::command]
pub async fn get_session(api: BackendApiState<'_>) -> Result<Option<SessionInfo>, String> {
    let inner: &Arc<ApiClient> = api.inner();

    // Hydrate in-memory refresh token from keyring if needed.
    if inner.stored_refresh_token().is_err() {
        if let Some(token) = token_store::load_refresh_token() {
            let _ = inner.set_refresh_token(token);
        }
    }

    match try_load_session(inner).await {
        Ok(info) => Ok(Some(info)),
        Err(tb_client::ClientError::AuthTokenNotSet) => {
            // No access token yet — try refreshing from a stored refresh token.
            if inner.stored_refresh_token().is_ok() {
                match inner.auth_client().refresh().await {
                    Ok(_) => {
                        persist_refresh_token(inner);
                        match try_load_session(inner).await {
                            Ok(info) => return Ok(Some(info)),
                            Err(retry_err) => {
                                warn!("Session still invalid after refresh: {retry_err}");
                            }
                        }
                    }
                    Err(refresh_err) => {
                        warn!("Refresh failed during get_session: {refresh_err}");
                    }
                }
            }
            clear_local_session(inner);
            Ok(None)
        }
        Err(err) => {
            warn!("Client error for get_session: {err}");

            // Access may have expired — try refresh before wiping the session.
            if inner.stored_refresh_token().is_ok() {
                match inner.auth_client().refresh().await {
                    Ok(_) => {
                        persist_refresh_token(inner);
                        match try_load_session(inner).await {
                            Ok(info) => return Ok(Some(info)),
                            Err(retry_err) => {
                                warn!("Session still invalid after refresh: {retry_err}");
                            }
                        }
                    }
                    Err(refresh_err) => {
                        warn!("Refresh failed during get_session: {refresh_err}");
                    }
                }
            }

            clear_local_session(inner);
            Ok(None)
        }
    }
}

async fn try_load_session(api: &ApiClient) -> tb_client::ClientResult<SessionInfo> {
    let session = api.auth_client().session().await?;
    Ok(SessionInfo {
        profile_complete: session.profile_complete,
        first_name: session.first_name,
        email: session.email,
        user_id: session.user_id,
    })
}

/// Will return true if the user is currently logged in
#[tauri::command]
pub async fn is_valid_session(api: BackendApiState<'_>) -> Result<bool, String> {
    Ok(get_session(api).await?.is_some())
}

#[tauri::command(rename_all = "camelCase")]
pub async fn complete_profile(
    api: BackendApiState<'_>,
    first_name: String,
    last_name: String,
    usage_intent: String,
) -> Result<(), String> {
    let inner: &Arc<ApiClient> = api.inner();

    inner
        .user_client()
        .complete_profile(&first_name, &last_name, &usage_intent)
        .await
        .map_err(|e| e.user_message())?;

    Ok(())
}

#[tauri::command]
pub async fn log_out(api: BackendApiState<'_>) -> Result<(), String> {
    let inner: &Arc<ApiClient> = api.inner();

    if let Err(err) = inner.auth_client().logout().await {
        warn!("Server logout failed (clearing local tokens anyway): {err}");
    }

    clear_local_session(inner);
    Ok(())
}

#[tauri::command]
pub async fn ping(api: BackendApiState<'_>) -> Result<(), String> {
    // Get inner otherwise RA fails to provide autocomplete
    let inner: &Arc<ApiClient> = api.inner();

    inner
        .misc_client()
        .ping()
        .await
        .map_err(|e| e.user_message())
}

/// Requests a password reset code. In development, may return the plaintext code.
#[tauri::command]
pub async fn request_password_reset(
    api: BackendApiState<'_>,
    email: String,
) -> Result<Option<String>, String> {
    let inner: &Arc<ApiClient> = api.inner();

    let response = inner
        .auth_client()
        .forgot_password(&email)
        .await
        .map_err(|e| e.user_message())?;

    Ok(response.password_reset_code)
}

#[tauri::command(rename_all = "camelCase")]
pub async fn confirm_password_reset(
    api: BackendApiState<'_>,
    email: String,
    code: String,
    new_password: String,
) -> Result<(), String> {
    let inner: &Arc<ApiClient> = api.inner();

    inner
        .auth_client()
        .reset_password(&email, &code, &new_password)
        .await
        .map_err(|e| e.user_message())?;

    Ok(())
}
