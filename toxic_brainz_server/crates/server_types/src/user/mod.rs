use serde::{Deserialize, Serialize};

pub mod requests;
pub mod responses;

#[derive(Debug, Serialize, Deserialize)]
pub enum RoleType {
    User,
    Admin,
    SuperAdmin,
}
