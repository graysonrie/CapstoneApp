use axum::extract::multipart::{Field, MultipartError};

use crate::features::file_storage::file_storage_trait::FileStorageStateType;

pub enum MultipartReaderError {
    Axum(MultipartError),
    IncorrectMultipartFormat,
    Io(std::io::Error),
    Storage(anyhow::Error),
}

#[allow(clippy::from_over_into)]
impl Into<MultipartReaderError> for std::io::Error {
    fn into(self) -> MultipartReaderError {
        MultipartReaderError::Io(self)
    }
}

impl From<anyhow::Error> for MultipartReaderError {
    fn from(value: anyhow::Error) -> Self {
        MultipartReaderError::Storage(value)
    }
}

impl From<MultipartError> for MultipartReaderError {
    fn from(value: MultipartError) -> Self {
        MultipartReaderError::Axum(value)
    }
}

/// Streams a multipart field into storage at `relative_path` (e.g. `"AddinsLibrary/v1/my_addin/data.bin"`).
pub async fn stream_field_to_storage(
    storage: &FileStorageStateType,
    mut field: Field<'_>,
    relative_path: &str,
) -> Result<u64, MultipartReaderError> {
    let mut total_bytes = 0u64;
    let mut is_first_chunk = true;

    while let Some(chunk) = field.chunk().await.map_err(MultipartReaderError::from)? {
        total_bytes += chunk.len() as u64;

        if is_first_chunk {
            storage
                .write_file_bytes(relative_path, &chunk)
                .await
                .map_err(MultipartReaderError::from)?;
            is_first_chunk = false;
        } else {
            storage
                .append_file_bytes(relative_path, &chunk)
                .await
                .map_err(MultipartReaderError::from)?;
        }
    }

    Ok(total_bytes)
}
