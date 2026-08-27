use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct PendingEmailVerificationResponse {
    pub plaintext_code: String,
}
