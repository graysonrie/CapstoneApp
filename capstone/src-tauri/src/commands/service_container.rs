use crate::prelude::*;
use crate::services::AppSaveService;
use crate::services::TestService;

pub fn register_services(handle: &AppHandle) {
    let handle = handle.clone();

    let app_save_service = Arc::new(AppSaveService::new(handle.clone()));
    handle.manage(app_save_service.clone());

    let test_service = Arc::new(TestService::default());
    handle.manage(test_service);
}
