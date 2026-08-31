use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
};
use sea_orm::DbErr;

pub struct UserHttpError(pub (StatusCode, String));

impl From<DbErr> for UserHttpError {
    fn from(err: DbErr) -> Self {
        let (status, msg) = match err {
            DbErr::RecordNotFound(_) => (StatusCode::NOT_FOUND, "user not found"),
            _ => (StatusCode::INTERNAL_SERVER_ERROR, "internal server error"),
        };
        Self((status, msg.into()))
    }
}

impl IntoResponse for UserHttpError {
    fn into_response(self) -> Response {
        let (status, body) = self.0;
        (status, body).into_response()
    }
}
