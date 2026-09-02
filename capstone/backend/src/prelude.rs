//! Common imports used throughout the server.
//!
//! Most modules can `use crate::prelude::*;` and only add extra imports for
//! things specific to that file.

#![allow(unused_imports)]

pub use std::{
    path::{Path, PathBuf},
    sync::Arc,
};

pub use axum::{
    Json, Router,
    extract::{Request, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::{get, post},
};
pub use chrono::{DateTime, Utc};
pub use sea_orm::ActiveValue::NotSet;
pub use sea_orm::{
    ActiveModelTrait, ActiveValue, ColumnTrait, ConnectionTrait, DatabaseConnection, DbErr,
    DeleteResult, EntityTrait, QueryFilter, Set, UpdateResult,
    entity::prelude::{DateTimeWithTimeZone, async_trait::async_trait},
};
pub use serde::{Deserialize, Serialize};
pub use server_types::prelude::*;
pub use server_types::user::RoleType;
pub use thiserror::Error;

pub use crate::app_config::AppConfig;
pub use crate::clock::{AppClock, Clock};
pub use crate::environment::{self, is_dev, is_prod};
pub use crate::features::auth::Role;
pub use crate::features::db::models::user::UserIdType;
pub use crate::state::AppState;
