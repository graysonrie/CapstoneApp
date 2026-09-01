pub mod middleware;
mod password;
mod repo;
pub mod routes;
mod service;
mod tokens;

use std::str::FromStr;

use thiserror::Error;

pub use middleware::{AuthenticatedUser, require_auth};
pub use routes::auth_router;
use sea_orm::{DeriveActiveEnum, EnumIter};
use server_types::user::RoleType;

#[derive(Clone, Debug, PartialEq, EnumIter, DeriveActiveEnum)]
#[sea_orm(db_type = "Text")]
#[sea_orm(rs_type = "String")]
pub enum Role {
    #[sea_orm(string_value = "user")]
    User,
    #[sea_orm(string_value = "admin")]
    Admin,
    #[sea_orm(string_value = "superadmin")]
    SuperAdmin,
}

#[derive(Debug, Error)]
#[error("invalid role: {0}")]
pub struct InvalidRoleError(pub String);

impl FromStr for Role {
    type Err = InvalidRoleError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "user" => Ok(Role::User),
            "admin" => Ok(Role::Admin),
            "superadmin" => Ok(Role::SuperAdmin),
            _ => Err(InvalidRoleError(s.to_string())),
        }
    }
}

impl From<RoleType> for Role {
    fn from(role: RoleType) -> Self {
        match role {
            RoleType::User => Role::User,
            RoleType::Admin => Role::Admin,
            RoleType::SuperAdmin => Role::SuperAdmin,
        }
    }
}
