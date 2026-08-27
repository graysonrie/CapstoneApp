use addin_server_interactor::ApiClient;
mod common;
use common::*;

#[tokio::test]
async fn test_expired_email_verification_code_fails() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();

    client.clock_client().reset().await.unwrap();

    let response = client
        .auth_client()
        .register_start(EXPIRING_EMAIL, PASSWORD)
        .await
        .unwrap();
    let code = response.email_verification_code.unwrap();

    client.clock_client().advance(121).await.unwrap();
    let response = client
        .auth_client()
        .verify_email(EXPIRING_EMAIL, &code)
        .await;
    assert!(response.is_err());

    client.clock_client().reset().await.unwrap();
    log_in_as_super_admin(&client).await;

    client.clock_client().advance(16 * 60 + 1).await.unwrap();
    let response = client.user_client().delete_user(EXPIRING_EMAIL).await;
    let error = format!("{response:?}");
    assert!(error.contains("401"), "{error}");

    client.clock_client().reset().await.unwrap();
}

/// Ensures that wrong code fails
#[tokio::test]
async fn test_wrong_email_verification_code_fails() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();
    let response = register_user_into_db().await.unwrap();

    let code = response.email_verification_code.unwrap();

    let verify_result = client
        .auth_client()
        .verify_email(EMAIL, &format!("1{code}"))
        .await;

    assert!(verify_result.is_err())
}

#[tokio::test]
async fn test_already_used_code_fails() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();

    let response = register_user_into_db().await.unwrap();
    let code = response.email_verification_code.unwrap();

    let verify_result = client.auth_client().verify_email(EMAIL, &code).await;

    assert!(verify_result.is_ok());

    let verify_result = client.auth_client().verify_email(EMAIL, &code).await;

    assert!(verify_result.is_err())
}

#[tokio::test]
async fn test_code_cannot_verify_a_different_user() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();

    let user1 = EMAIL;
    let password1 = PASSWORD;

    let user2 = EMAIL2;
    let password2 = PASSWORD2;

    let user1_response = register_certain_user_into_db(user1, password1)
        .await
        .unwrap();
    let user1_code = user1_response.email_verification_code.unwrap();

    let user2_response = register_certain_user_into_db(user2, password2)
        .await
        .unwrap();
    let user2_code = user2_response.email_verification_code.unwrap();

    // Try to verify user1 with user2's code
    let user1_verify_result = client.auth_client().verify_email(user1, &user2_code).await;

    assert!(user1_verify_result.is_err());

    // Try to verify user2 with user1's code
    let user2_verify_result = client.auth_client().verify_email(user2, &user1_code).await;

    assert!(user2_verify_result.is_err());

    // Try to verify user1 with user1's code
    let user1_verify_result = client.auth_client().verify_email(user1, &user1_code).await;

    assert!(user1_verify_result.is_ok());

    // Try to verify user2 with user2's code
    let user2_verify_result = client.auth_client().verify_email(user2, &user2_code).await;

    assert!(user2_verify_result.is_ok());
}
