use keyring::Entry;
use log::warn;

const SERVICE_NAME: &str = "plant-app";
const REFRESH_TOKEN_ACCOUNT: &str = "refresh_token";

fn refresh_entry() -> Result<Entry, keyring::Error> {
    Entry::new(SERVICE_NAME, REFRESH_TOKEN_ACCOUNT)
}

pub fn save_refresh_token(token: &str) {
    match refresh_entry() {
        Ok(entry) => {
            if let Err(err) = entry.set_password(token) {
                warn!("Failed to save refresh token to keyring: {err}");
            }
        }
        Err(err) => warn!("Failed to open keyring entry: {err}"),
    }
}

pub fn load_refresh_token() -> Option<String> {
    match refresh_entry() {
        Ok(entry) => match entry.get_password() {
            Ok(token) if !token.is_empty() => Some(token),
            Ok(_) => None,
            Err(keyring::Error::NoEntry) => None,
            Err(err) => {
                warn!("Failed to load refresh token from keyring: {err}");
                None
            }
        },
        Err(err) => {
            warn!("Failed to open keyring entry: {err}");
            None
        }
    }
}

pub fn clear_refresh_token() {
    match refresh_entry() {
        Ok(entry) => {
            if let Err(err) = entry.delete_credential() {
                match err {
                    keyring::Error::NoEntry => {}
                    other => warn!("Failed to clear refresh token from keyring: {other}"),
                }
            }
        }
        Err(err) => warn!("Failed to open keyring entry: {err}"),
    }
}
