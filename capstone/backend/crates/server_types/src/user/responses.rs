use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct UserResponse {
    username: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct ChangeRoleResponse {
    pub success: bool,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct CompleteProfileResponse {
    pub success: bool,
}
