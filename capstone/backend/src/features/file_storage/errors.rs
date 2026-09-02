use crate::prelude::*;

pub type FileStorageResult<T> = Result<T, FileStorageError>;

#[derive(Debug, Error)]
pub enum FileStorageError {
    #[error("relative path must not be empty")]
    EmptyPath,

    #[error("absolute paths are not allowed")]
    AbsolutePathNotAllowed,

    #[error("invalid path component in {path:?}")]
    InvalidPathComponent { path: String },

    #[error(transparent)]
    Io(#[from] std::io::Error),
}
