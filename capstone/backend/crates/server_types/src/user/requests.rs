use serde::{Deserialize, Serialize};

use crate::user::RoleType;

#[derive(Debug, Serialize, Deserialize)]
pub struct DeleteUserRequest {
    pub email: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ChangeRoleRequest {
    pub email: String,
    pub role: RoleType,
}
