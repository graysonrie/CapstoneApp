mod service_container;
mod tauri_registry;


pub use service_container::register_services;
pub use tauri_registry::invoke_handler;