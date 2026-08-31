use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct ClockStatusResponse {
    pub now_utc: String,
    pub offset_seconds: i64,
}
