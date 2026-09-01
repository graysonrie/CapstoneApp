use std::sync::Arc;

use sea_orm::entity::prelude::async_trait::async_trait;
use thiserror::Error;

pub type EmailSenderStateType = Arc<dyn EmailSender + Send + Sync>;

pub type EmailSenderResult<T> = Result<T, EmailSenderError>;

#[derive(Debug, Error)]
pub enum EmailSenderError {
    #[error("failed to send verification email")]
    SendFailed,
}

#[async_trait]
pub trait EmailSender {
    async fn send_verification_code(&self, to: &str, code: &str) -> EmailSenderResult<()>;
}

pub struct MockEmailSender;

#[async_trait]
impl EmailSender for MockEmailSender {
    async fn send_verification_code(&self, to: &str, code: &str) -> EmailSenderResult<()> {
        tracing::warn!("sent code {code} to {to} (not really)");

        Ok(())
    }
}
