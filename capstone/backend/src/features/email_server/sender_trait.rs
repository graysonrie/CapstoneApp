use std::sync::Arc;

use anyhow::Ok;
use sea_orm::entity::prelude::async_trait::async_trait;

pub type EmailSenderStateType = Arc<dyn EmailSender + Send + Sync>;

#[async_trait]
pub trait EmailSender {
    async fn send_verification_code(&self, to: &str, code: &str) -> anyhow::Result<()>;
}

pub struct MockEmailSender;

#[async_trait]
impl EmailSender for MockEmailSender {
    async fn send_verification_code(&self, to: &str, code: &str) -> anyhow::Result<()> {
        tracing::warn!("sent code {code} to {to} (not really)");

        Ok(())
    }
}
