use std::sync::atomic::{AtomicI64, Ordering};

use chrono::{DateTime, Duration, Utc};
use sea_orm::entity::prelude::DateTimeWithTimeZone;

const MAX_OFFSET_SECONDS: i64 = 100 * 365 * 24 * 60 * 60;

pub trait Clock: Send + Sync {
    fn now_utc(&self) -> DateTime<Utc>;

    fn now_db(&self) -> DateTimeWithTimeZone {
        self.now_utc().fixed_offset()
    }
}

#[derive(Debug, Default)]
pub struct AppClock {
    offset_seconds: AtomicI64,
}

#[derive(Debug)]
pub enum ClockError {
    OffsetOutOfRange,
}

impl AppClock {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn offset_seconds(&self) -> i64 {
        self.offset_seconds.load(Ordering::SeqCst)
    }

    pub fn advance_seconds(&self, seconds: i64) -> Result<i64, ClockError> {
        self.offset_seconds
            .fetch_update(Ordering::SeqCst, Ordering::SeqCst, |current| {
                let next = current.checked_add(seconds)?;
                if next.abs() > MAX_OFFSET_SECONDS {
                    return None;
                }
                Some(next)
            })
            .map(|previous| previous + seconds)
            .map_err(|_| ClockError::OffsetOutOfRange)
    }

    pub fn reset(&self) {
        self.offset_seconds.store(0, Ordering::SeqCst);
    }
}

impl Clock for AppClock {
    fn now_utc(&self) -> DateTime<Utc> {
        Utc::now() + Duration::seconds(self.offset_seconds())
    }
}
