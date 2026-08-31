use addin_server_interactor::ApiClient;
mod common;
use common::*;
use server_types::prelude::LoginResponse;

async fn login_verified_user(client: &ApiClient) -> LoginResponse {
    let register_response = register_user_into_db().await.unwrap();
    let code = register_response.email_verification_code.unwrap();
    client
        .auth_client()
        .verify_email(EMAIL, &code)
        .await
        .unwrap();
    client.auth_client().login(EMAIL, PASSWORD).await.unwrap()
}

#[tokio::test]
async fn test_login_returns_access_and_refresh_tokens() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();

    let login_response = login_verified_user(&client).await;

    assert!(!login_response.access_token.is_empty());
    assert!(!login_response.refresh_token.is_empty());
}

#[tokio::test]
async fn test_refresh_rotates_tokens_and_invalidates_old_refresh_token() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();

    let login_response = login_verified_user(&client).await;
    let old_refresh_token = login_response.refresh_token.clone();

    let refresh_response = client.auth_client().refresh().await.unwrap();
    assert!(!refresh_response.access_token.is_empty());
    assert!(!refresh_response.refresh_token.is_empty());
    assert_ne!(refresh_response.refresh_token, old_refresh_token);

    let reuse_result = client
        .auth_client()
        .refresh_with_token(&old_refresh_token)
        .await;
    assert!(reuse_result.is_err());
}

#[tokio::test]
async fn test_expired_access_token_can_be_refreshed() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();
    client.clock_client().reset().await.unwrap();

    log_in_as_super_admin(&client).await;

    client.clock_client().advance(16 * 60 + 1).await.unwrap();

    let expired_access_response = client.user_client().delete_user(EMAIL).await;
    let error = format!("{expired_access_response:?}");
    assert!(error.contains("401"), "{error}");

    client.auth_client().refresh().await.unwrap();

    let refreshed_access_response = client.user_client().delete_user(EMAIL).await;
    assert!(refreshed_access_response.is_ok());

    client.clock_client().reset().await.unwrap();
}

#[tokio::test]
async fn test_expired_refresh_token_is_rejected() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();
    client.clock_client().reset().await.unwrap();

    let login_response = login_verified_user(&client).await;

    client
        .clock_client()
        .advance(7 * 24 * 60 * 60 + 1)
        .await
        .unwrap();

    let refresh_result = client
        .auth_client()
        .refresh_with_token(&login_response.refresh_token)
        .await;
    assert!(refresh_result.is_err());

    client.clock_client().reset().await.unwrap();
}

#[tokio::test]
async fn test_refresh_token_cannot_be_used_as_access_token() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();

    log_in_as_super_admin(&client).await;
    let refresh_token = client.stored_refresh_token().unwrap();

    client.clear_auth_token().unwrap();
    client.set_auth_token(refresh_token).unwrap();

    let response = client.user_client().delete_user(EMAIL).await;
    let error = format!("{response:?}");
    assert!(error.contains("401"), "{error}");
}
