use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct RegisterAttemptedResponse {
    pub user_id: Option<i32>,
    /// This code is only set if in dev mode and the user was created with a temp email.
    pub email_verification_code: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct LoginResponse {
    pub access_token: String,
    pub refresh_token: String,
    pub user_id: i32,
    pub email: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct RefreshTokenResponse {
    pub access_token: String,
    pub refresh_token: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct SessionResponse {
    pub user_id: i32,
    pub email: String,
    pub profile_complete: bool,
    pub first_name: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct VerifyEmailResponse {
    pub message: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ResendVerificationEmailResponse {
    pub message: String,
    /// This code is only set if in dev mode and the user was created with a temp email.
    pub email_verification_code: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ForgotPasswordResponse {
    pub message: String,
    /// Only populated in development builds.
    pub password_reset_code: Option<String>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ResetPasswordResponse {
    pub message: String,
}
