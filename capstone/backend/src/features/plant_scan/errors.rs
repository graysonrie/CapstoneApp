use crate::prelude::*;

#[derive(Debug, Error)]
pub enum PlantScanError {
    #[error("openai api key is not configured")]
    MissingApiKey,
    #[error("image is required")]
    MissingImage,
    #[error("image is too large")]
    ImageTooLarge,
    #[error("the image does not contain a recognizable plant")]
    NotAPlant,
    #[error("openai request failed: {0}")]
    OpenAi(String),
    #[error("failed to parse plant identification")]
    InvalidModelResponse,
    #[error(transparent)]
    Database(#[from] DbErr),
    #[error(transparent)]
    Storage(#[from] crate::features::file_storage::FileStorageError),
    #[error(transparent)]
    Io(#[from] std::io::Error),
}

pub struct PlantScanHttpError(pub (StatusCode, String));

impl From<PlantScanError> for PlantScanHttpError {
    fn from(err: PlantScanError) -> Self {
        let (status, msg) = match &err {
            PlantScanError::MissingApiKey => (
                StatusCode::SERVICE_UNAVAILABLE,
                "plant scanning is not configured".to_string(),
            ),
            PlantScanError::MissingImage => (StatusCode::BAD_REQUEST, "image is required".into()),
            PlantScanError::ImageTooLarge => (StatusCode::BAD_REQUEST, "image is too large".into()),
            PlantScanError::NotAPlant => (
                StatusCode::UNPROCESSABLE_ENTITY,
                "could not identify a plant in that photo".into(),
            ),
            PlantScanError::InvalidModelResponse | PlantScanError::OpenAi(_) => {
                tracing::error!("plant scan error: {err:?}");
                (
                    StatusCode::BAD_GATEWAY,
                    "failed to analyze the plant".into(),
                )
            }
            PlantScanError::Database(_) | PlantScanError::Storage(_) | PlantScanError::Io(_) => {
                tracing::error!("plant scan error: {err:?}");
                (StatusCode::INTERNAL_SERVER_ERROR, "internal server error".into())
            }
        };
        Self((status, msg))
    }
}

impl IntoResponse for PlantScanHttpError {
    fn into_response(self) -> Response {
        let (status, body) = self.0;
        (status, body).into_response()
    }
}
