use std::fs::File;

use migration::{Migrator, MigratorTrait};
use sea_orm::Schema;

use crate::prelude::*;
pub mod models;

async fn ensure_user_table(db: &sea_orm::DatabaseConnection) -> Result<(), sea_orm::DbErr> {
    ensure_table(db, models::user::Entity).await
}

async fn ensure_email_verification_table(
    db: &sea_orm::DatabaseConnection,
) -> Result<(), sea_orm::DbErr> {
    ensure_table(db, models::email_verification::Entity).await
}

/// Creates the table from the given entity if the table does not exist
async fn ensure_table(
    db: &sea_orm::DatabaseConnection,
    entity: impl EntityTrait,
) -> Result<(), sea_orm::DbErr> {
    let backend = db.get_database_backend();
    let schema = Schema::new(backend);
    let mut stmt = schema.create_table_from_entity(entity);
    stmt.if_not_exists();
    db.execute(&stmt).await?;
    Ok(())
}

/// Creates the tables for all models specified in `super::models` if they do not already exist
async fn ensure_tables(db: &sea_orm::DatabaseConnection) -> Result<(), sea_orm::DbErr> {
    ensure_user_table(db).await?;
    ensure_email_verification_table(db).await?;
    Ok(())
}

async fn get_local_sqlite_database_connection(
    db_file_path: impl AsRef<Path>,
) -> Result<sea_orm::DatabaseConnection, sea_orm::DbErr> {
    let db_file_path = db_file_path.as_ref();

    let db_file_name = db_file_path
        .file_name()
        .expect("no file name")
        .to_string_lossy();

    if !db_file_path.exists() {
        File::create(db_file_path).unwrap();
    }
    let database_url = format!("sqlite://{}?mode=rwc", db_file_name);

    let db = sea_orm::Database::connect(&database_url)
        .await
        .expect("connect database");

    Migrator::up(&db, None).await?;
    ensure_tables(&db).await?;
    Ok(db)
}

/// TODO: allow for other database types than sqlite
pub async fn get_database_connection(
    config: &AppConfig,
) -> Result<sea_orm::DatabaseConnection, sea_orm::DbErr> {
    get_local_sqlite_database_connection(config.db.local_sqlite.as_ref().unwrap().db_path.clone())
        .await
}

/// Deletes everything from all tables
pub async fn erase_and_recreate_all_tables(db: &DatabaseConnection) -> Result<(), DbErr> {
    if !environment::is_dev() {
        return Err(DbErr::Custom("Can't do that".to_string()));
    }

    let _ = crate::features::db::models::user::Entity::delete_many()
        .exec(db)
        .await?;

    let _ = crate::features::db::models::email_verification::Entity::delete_many()
        .exec(db)
        .await?;

    tracing::warn!("Database has been erased from erase_and_recreate_all_tables");

    Ok(())
}
