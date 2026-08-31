use super::common::*;
use crate::tests::utils::TestFixture;

#[tokio::test]
async fn test_root() {
    let fixture = TestFixture::new().await;

    let response = fixture.client.test_client().hello().await.unwrap();
    assert_eq!(response.message, "Hello from Axum");

    fixture.finish().await;
}

#[tokio::test]
async fn test_auth_bypass() {
    let fixture = TestFixture::new().await;

    let register_response = fixture
        .client
        .auth_client()
        .register_start(EMAIL, PASSWORD)
        .await
        .expect("Issue with register_response");

    let verify_response = fixture
        .client
        .auth_client()
        .verify_email(EMAIL, &register_response.email_verification_code.unwrap())
        .await;

    assert!(verify_response.is_ok());

    let response = fixture
        .client
        .auth_client()
        .login_bypass(EMAIL, PASSWORD)
        .await;

    println!("{:?}", response);
    assert!(response.is_ok());

    fixture.finish().await;
}

#[tokio::test]
async fn protected_route_test() {
    let fixture = TestFixture::new().await;

    let response = fixture.client.user_client().delete_user(EMAIL).await;
    println!("{:?}", response);
    assert!(response.is_err());

    fixture.finish().await;
}

/// Deletes the user if it exists, registers a new user, verifies the email, and logs in.
/// If in dev mode, the email field will be set.
#[tokio::test]
async fn test_register_verify_and_login() {
    let fixture = TestFixture::new().await;
    reset_db(&fixture.client).await.unwrap();

    let response = fixture
        .client
        .auth_client()
        .register_start(EMAIL, PASSWORD)
        .await;
    println!("{:?}", response);
    assert!(response.is_ok());

    // If in dev mode, the email field will be set
    let response = response.unwrap();
    assert!(response.email_verification_code.is_some());

    // Verify  the email
    let code = response.email_verification_code.unwrap();
    let response = fixture
        .client
        .auth_client()
        .verify_email(EMAIL, &code)
        .await;
    println!("{:?}", response);
    assert!(response.is_ok());

    // Login
    let response = fixture.client.auth_client().login(EMAIL, PASSWORD).await;
    println!("{:?}", response);
    assert!(response.is_ok());

    fixture.finish().await;
}

/// Deletes the user if it exists, registers a new user, verifies the email, and logs in.
/// If in dev mode, the email field will be set.
#[tokio::test]
async fn test_resend_verification_email() {
    let fixture = TestFixture::new().await;
    reset_db(&fixture.client).await.unwrap();

    let response = fixture
        .client
        .auth_client()
        .register_start(EMAIL, PASSWORD)
        .await;
    println!("{:?}", response);
    assert!(response.is_ok());

    // If in dev mode, the email field will be set
    let response = response.unwrap();
    assert!(response.email_verification_code.is_some());

    // Ignore the email code and ask for a new one
    let response = fixture
        .client
        .auth_client()
        .resend_verification_email(EMAIL)
        .await;
    println!("{:?}", response);
    assert!(response.is_ok());

    // If in dev mode, the email field will be set
    let response = response.unwrap();
    assert!(response.email_verification_code.is_some());

    // Verify  the email
    let code = response.email_verification_code.unwrap();
    let response = fixture
        .client
        .auth_client()
        .verify_email(EMAIL, &code)
        .await;
    println!("{:?}", response);
    assert!(response.is_ok());

    // Login
    let response = fixture.client.auth_client().login(EMAIL, PASSWORD).await;
    println!("{:?}", response);
    assert!(response.is_ok());

    fixture.finish().await;
}

#[tokio::test]
async fn test_log_in() {
    let fixture = TestFixture::new().await;
    reset_db(&fixture.client).await.unwrap();

    let register_result = super::common::register_verified_user_into_db(&fixture.client).await;
    assert!(register_result.is_ok());

    // Right email, right password
    let response = fixture.client.auth_client().login(EMAIL, PASSWORD).await;

    println!("{:?}", response);
    assert!(response.is_ok());

    // Right email, wrong password
    let password = "wrongpassword";
    let response = fixture.client.auth_client().login(EMAIL, password).await;

    assert!(response.is_err());

    // Right password, wrong email
    let username = "fakeuser";
    let response = fixture.client.auth_client().login(username, PASSWORD).await;

    assert!(response.is_err());

    fixture.finish().await;
}
