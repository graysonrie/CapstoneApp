pub enum AppEnvironment {
    Dev,
    Prod,
}

/// Gets the environment. (Dev or prod)
pub fn get_environment() -> AppEnvironment {
    let is_prod = std::env::var("APP_ENV").unwrap_or_default() == "production";
    if is_prod {
        return AppEnvironment::Prod;
    }
    AppEnvironment::Dev
}

pub fn is_dev() -> bool {
    matches!(get_environment(), AppEnvironment::Dev)
}

pub fn is_prod() -> bool {
    matches!(get_environment(), AppEnvironment::Prod)
}
