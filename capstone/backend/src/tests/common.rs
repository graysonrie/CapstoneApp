use std::path::Path;

use tb_client::{
    ApiClient,
};
use tb_client::ClientError;

use server_types::{
    auth::responses::{RegisterAttemptedResponse, VerifyEmailResponse},
    user::RoleType,
};

pub const EMAIL: &str = "myemail@email.com";
pub const PASSWORD: &str = "testpassword";

/// This is actually used, but the compiler thinks it isnt
#[allow(dead_code)]
pub const EMAIL2: &str = "myemail2@email.com";

/// This is actually used, but the compiler thinks it isnt
#[allow(dead_code)]
pub const PASSWORD2: &str = "testpassword2";

/// This is actually used, but the compiler thinks it isnt
#[allow(dead_code)]
pub const EXPIRING_EMAIL: &str = "expiring.email@example.com";

#[allow(dead_code)]
pub const TEST_LOCAL_SERVER_PATH: &str =
    "C:\\Users\\GRieger\\Desktop\\rust\\addinmanager2_dev\\TEST_LOCAL_SERVER";

#[allow(dead_code)]
pub const SAMPLE_CSPROJ_PATH: &str =
    "C:\\Users\\GRieger\\source\\repos\\RealTabColorizer\\TabColorizer\\TabColorizer.csproj";

#[allow(dead_code)]
pub async fn log_in_as_super_admin(client: &ApiClient) {
    // Login as super admin
    if let Ok(res) = client
        .auth_client()
        .register_start_as_super_admin(EMAIL, PASSWORD)
        .await
    {
        let code = res.email_verification_code.unwrap();
        client
            .auth_client()
            .verify_email(EMAIL, &code)
            .await
            .unwrap();
    }

    // Since the user may already exist, we need to ensure it has the SuperAdmin role
    if let Err(e) = client
        .user_client()
        .change_role_bypass(EMAIL, RoleType::SuperAdmin)
        .await
    {
        println!("Error changing role to SuperAdmin: {:?}", e);
    }

    // Log in as the super admin to get a token
    let _ = client
        .auth_client()
        .login_bypass(EMAIL, PASSWORD)
        .await
        .unwrap();
}

pub async fn reset_db(client: &ApiClient) -> Result<(), ClientError> {
    client.dev_client().erase_db().await
}

#[allow(dead_code)]
/// Registers a new user with EMAIL and verifies the password
pub async fn register_verified_user_into_db(
    client: &ApiClient,
) -> Result<VerifyEmailResponse, ClientError> {
    let response = client.auth_client().register_start(EMAIL, PASSWORD).await;
    println!("{:?}", response);

    // If in dev mode, the email field will be set
    let response = response?;

    // Verify  the email
    let code = response
        .email_verification_code
        .ok_or(ClientError::MissingEmailVerificationCode)?;
    client.auth_client().verify_email(EMAIL, &code).await
}

#[allow(dead_code)]
/// Registers a new user with EMAIL
pub async fn register_user_into_db(
    client: &ApiClient,
) -> Result<RegisterAttemptedResponse, ClientError> {
    register_certain_user_into_db(client, EMAIL, PASSWORD).await
}

#[allow(dead_code)]
/// Registers a new user with EMAIL
pub async fn register_certain_user_into_db(
    client: &ApiClient,
    email: &str,
    password: &str,
) -> Result<RegisterAttemptedResponse, ClientError> {
    client.auth_client().register_start(email, password).await
}

#[allow(dead_code)]
pub async fn clear_test_local_server() {
    let path = Path::new(TEST_LOCAL_SERVER_PATH).canonicalize().unwrap();
    let _ = tokio::fs::remove_dir_all(&path).await;
    let _ = tokio::fs::create_dir_all(&path).await;
}