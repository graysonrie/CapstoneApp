use super::service::UserError;
use crate::prelude::*;

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

impl From<UserError> for UserHttpError {
    fn from(err: UserError) -> Self {
        let (status, msg) = match err {
            UserError::InvalidProfile => (StatusCode::BAD_REQUEST, "invalid profile data"),
            UserError::NotFound => (StatusCode::NOT_FOUND, "user not found"),
            UserError::Database(db_err) => return UserHttpError::from(db_err),
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
