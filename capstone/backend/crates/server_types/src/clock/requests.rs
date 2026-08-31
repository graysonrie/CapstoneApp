use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct AdvanceClockRequest {
    pub seconds: i64,
}
