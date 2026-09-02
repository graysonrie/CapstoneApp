use axum::extract::multipart::{Field, MultipartError};

use crate::features::file_storage::file_storage_trait::FileStorageStateType;
use crate::features::file_storage::FileStorageError;
use crate::prelude::*;

#[derive(Debug, Error)]
pub enum MultipartReaderError {
    #[error(transparent)]
    Axum(#[from] MultipartError),

    #[error("incorrect multipart format")]
    IncorrectMultipartFormat,

    #[error(transparent)]
    Io(#[from] std::io::Error),

    #[error(transparent)]
    Storage(#[from] FileStorageError),
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
