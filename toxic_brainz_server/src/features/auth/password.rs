use rand::RngExt;
use rand::rand_core::UnwrapErr;
use rand::rngs::SysRng;

pub fn generate_salt() -> String {
    let mut rng = UnwrapErr(SysRng);
    (0..32)
        .map(|_| format!("{:02x}", rng.random::<u8>()))
        .collect()
}

fn peppered_password(password: &str, salt: &str) -> String {
    if salt.is_empty() {
        password.to_string()
    } else {
        format!("{password}{salt}")
    }
}

pub fn hash_password(password: &str, salt: &str) -> Result<String, bcrypt::BcryptError> {
    bcrypt::hash(peppered_password(password, salt), bcrypt::DEFAULT_COST)
}

pub fn verify_password(
    password: &str,
    salt: &str,
    password_hash: &str,
) -> Result<bool, bcrypt::BcryptError> {
    bcrypt::verify(peppered_password(password, salt), password_hash)
}
