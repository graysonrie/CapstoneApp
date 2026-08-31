use addin_server_interactor::ApiClient;
mod common;
use common::*;

#[tokio::test]
async fn test_root() {
    let client = ApiClient::default();
    let response = client.test_client().hello().await.unwrap();
    assert_eq!(response.message, "Hello from Axum");
}

#[tokio::test]
async fn test_auth_bypass() {
    let client = ApiClient::default();

    let response = client.auth_client().login_bypass(EMAIL, PASSWORD).await;

    println!("{:?}", response);
    assert!(response.is_ok());
}

#[tokio::test]
async fn protected_route_test() {
    let client = ApiClient::default();

    let response = client.user_client().delete_user(EMAIL).await;
    println!("{:?}", response);
    assert!(response.is_err());
}

/// Deletes the user if it exists, registers a new user, verifies the email, and logs in.
/// If in dev mode, the email field will be set.
#[tokio::test]
async fn test_register_verify_and_login() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();

    let response = client.auth_client().register_start(EMAIL, PASSWORD).await;
    println!("{:?}", response);
    assert!(response.is_ok());

    // If in dev mode, the email field will be set
    let response = response.unwrap();
    assert!(response.email_verification_code.is_some());

    // Verify  the email
    let code = response.email_verification_code.unwrap();
    let response = client.auth_client().verify_email(EMAIL, &code).await;
    println!("{:?}", response);
    assert!(response.is_ok());

    // Login
    let response = client.auth_client().login(EMAIL, PASSWORD).await;
    println!("{:?}", response);
    assert!(response.is_ok());
}

/// Deletes the user if it exists, registers a new user, verifies the email, and logs in.
/// If in dev mode, the email field will be set.
#[tokio::test]
async fn test_resend_verification_email() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();

    let response = client.auth_client().register_start(EMAIL, PASSWORD).await;
    println!("{:?}", response);
    assert!(response.is_ok());

    // If in dev mode, the email field will be set
    let response = response.unwrap();
    assert!(response.email_verification_code.is_some());

    // Ignore the email code and ask for a new one
    let response = client.auth_client().resend_verification_email(EMAIL).await;
    println!("{:?}", response);
    assert!(response.is_ok());

    // If in dev mode, the email field will be set
    let response = response.unwrap();
    assert!(response.email_verification_code.is_some());

    // Verify  the email
    let code = response.email_verification_code.unwrap();
    let response = client.auth_client().verify_email(EMAIL, &code).await;
    println!("{:?}", response);
    assert!(response.is_ok());

    // Login
    let response = client.auth_client().login(EMAIL, PASSWORD).await;
    println!("{:?}", response);
    assert!(response.is_ok());
}

#[tokio::test]
async fn test_log_in() {
    let client = ApiClient::default();
    reset_db(&client).await.unwrap();

    // run this test first to get a user in the database
    let register_result = common::register_verified_user_into_db().await;
    assert!(register_result.is_ok());

    // Right email, right password
    let response = client.auth_client().login(EMAIL, PASSWORD).await;

    println!("{:?}", response);
    assert!(response.is_ok());

    // Right email, wrong password
    let password = "wrongpassword";
    let response = client.auth_client().login(EMAIL, password).await;

    assert!(response.is_err());

    // Right password, wrong email
    let username = "fakeuser";
    let response = client.auth_client().login(username, PASSWORD).await;

    assert!(response.is_err());
}
