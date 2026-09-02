use std::path::Component;

use tokio::{fs, io::AsyncWriteExt};

use crate::features::file_storage::{FileStorageError, FileStorageResult};
use crate::prelude::*;

pub type FileStorageStateType = Arc<dyn FileStorage + Send + Sync>;

#[async_trait]
pub trait FileStorage {
    async fn create_dir_all(&self, relative_path: &str) -> FileStorageResult<()>;
    async fn directory_exists(&self, relative_path: &str) -> FileStorageResult<bool>;
    async fn file_exists(&self, relative_path: &str) -> FileStorageResult<bool>;
    /// If you want to get the directories too, use `get_files_and_directories_in_dir` instead
    async fn get_files_in_dir(&self, relative_path: &str) -> FileStorageResult<Vec<String>>;
    async fn get_files_and_directories_in_dir(
        &self,
        relative_path: &str,
    ) -> FileStorageResult<Vec<String>>;
    async fn delete_dir(&self, relative_path: &str) -> FileStorageResult<()>;
    async fn write_file_bytes(
        &self,
        relative_path: &str,
        bytes: &[u8],
    ) -> FileStorageResult<()>;
    /// Appends bytes to a file, creating the file and parent directories if needed.
    async fn append_file_bytes(
        &self,
        relative_path: &str,
        bytes: &[u8],
    ) -> FileStorageResult<()>;
    async fn delete_file(&self, relative_path: &str) -> FileStorageResult<()>;
    async fn read_file_bytes(&self, relative_path: &str) -> FileStorageResult<Vec<u8>>;
}

#[derive(Debug, Clone)]
pub struct LocalFileStorage {
    root: PathBuf,
}

impl LocalFileStorage {
    pub fn new(root: impl Into<PathBuf>) -> Self {
        Self { root: root.into() }
    }

    pub fn new_from_config(config: &AppConfig) -> Self {
        let root = config
            .file_storage
            .local_file_storage_directory_path
            .as_ref()
            .expect("To use local file storage, you must specify a directory");
        Self::new(root)
    }

    pub fn root(&self) -> &Path {
        &self.root
    }

    fn resolve_path(&self, relative_path: &str) -> FileStorageResult<PathBuf> {
        let relative = Path::new(relative_path);
        if relative.as_os_str().is_empty() {
            return Err(FileStorageError::EmptyPath);
        }
        if relative.is_absolute() {
            return Err(FileStorageError::AbsolutePathNotAllowed);
        }
        for component in relative.components() {
            if matches!(
                component,
                Component::ParentDir | Component::RootDir | Component::Prefix(_)
            ) {
                return Err(FileStorageError::InvalidPathComponent {
                    path: relative_path.to_string(),
                });
            }
        }
        Ok(self.root.join(relative))
    }
}

#[async_trait]
impl FileStorage for LocalFileStorage {
    async fn create_dir_all(&self, relative_path: &str) -> FileStorageResult<()> {
        let path = self.resolve_path(relative_path)?;
        fs::create_dir_all(path).await?;
        Ok(())
    }

    async fn directory_exists(&self, relative_path: &str) -> FileStorageResult<bool> {
        let path = self.resolve_path(relative_path)?;
        match fs::metadata(path).await {
            Ok(metadata) => Ok(metadata.is_dir()),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(false),
            Err(error) => Err(error.into()),
        }
    }

    async fn file_exists(&self, relative_path: &str) -> FileStorageResult<bool> {
        let path = self.resolve_path(relative_path)?;
        match fs::metadata(path).await {
            Ok(metadata) => Ok(metadata.is_file()),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(false),
            Err(error) => Err(error.into()),
        }
    }

    async fn get_files_and_directories_in_dir(
        &self,
        relative_path: &str,
    ) -> FileStorageResult<Vec<String>> {
        let path = self.resolve_path(relative_path)?;
        let mut entries = fs::read_dir(path).await?;
        let mut files = Vec::new();

        while let Some(entry) = entries.next_entry().await? {
            if let Some(name) = entry.file_name().to_str() {
                files.push(name.to_owned());
            }
        }

        files.sort();
        Ok(files)
    }

    async fn get_files_in_dir(&self, relative_path: &str) -> FileStorageResult<Vec<String>> {
        let path = self.resolve_path(relative_path)?;
        let mut entries = fs::read_dir(path).await?;
        let mut files = Vec::new();

        while let Some(entry) = entries.next_entry().await? {
            if entry.file_type().await?.is_file()
                && let Some(name) = entry.file_name().to_str()
            {
                files.push(name.to_owned());
            }
        }

        files.sort();
        Ok(files)
    }

    async fn delete_dir(&self, relative_path: &str) -> FileStorageResult<()> {
        let path = self.resolve_path(relative_path)?;
        match fs::remove_dir_all(path).await {
            Ok(()) => Ok(()),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
            Err(error) => Err(error.into()),
        }
    }

    async fn write_file_bytes(
        &self,
        relative_path: &str,
        bytes: &[u8],
    ) -> FileStorageResult<()> {
        let path = self.resolve_path(relative_path)?;
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent).await?;
        }
        fs::write(path, bytes).await?;
        Ok(())
    }

    async fn append_file_bytes(
        &self,
        relative_path: &str,
        bytes: &[u8],
    ) -> FileStorageResult<()> {
        let path = self.resolve_path(relative_path)?;
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent).await?;
        }
        let mut file = fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)
            .await?;
        file.write_all(bytes).await?;
        Ok(())
    }

    async fn delete_file(&self, relative_path: &str) -> FileStorageResult<()> {
        let path = self.resolve_path(relative_path)?;
        match fs::remove_file(path).await {
            Ok(()) => Ok(()),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(()),
            Err(error) => Err(error.into()),
        }
    }

    async fn read_file_bytes(&self, relative_path: &str) -> FileStorageResult<Vec<u8>> {
        let path = self.resolve_path(relative_path)?;
        Ok(fs::read(path).await?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::{SystemTime, UNIX_EPOCH};

    fn unique_test_root() -> PathBuf {
        let nanos = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system time before unix epoch")
            .as_nanos();
        std::env::temp_dir().join(format!("local_file_storage_test_{nanos}"))
    }

    async fn cleanup(root: &Path) {
        let _ = fs::remove_dir_all(root).await;
    }

    async fn storage_with_root() -> (LocalFileStorage, PathBuf) {
        let root = unique_test_root();
        fs::create_dir_all(&root)
            .await
            .expect("create test root directory");
        (LocalFileStorage::new(&root), root)
    }

    #[tokio::test]
    async fn create_dir_and_check_exists() {
        let (storage, root) = storage_with_root().await;

        storage.create_dir_all("nested/dir").await.unwrap();
        assert!(storage.directory_exists("nested/dir").await.unwrap());
        assert!(!storage.directory_exists("nested/missing").await.unwrap());

        cleanup(&root).await;
    }

    #[tokio::test]
    async fn write_read_and_delete_file() {
        let (storage, root) = storage_with_root().await;
        let contents = b"hello from local storage";

        storage
            .write_file_bytes("docs/hello.txt", contents)
            .await
            .unwrap();
        assert!(storage.file_exists("docs/hello.txt").await.unwrap());
        assert!(!storage.file_exists("docs/missing.txt").await.unwrap());

        let read_back = storage.read_file_bytes("docs/hello.txt").await.unwrap();
        assert_eq!(read_back, contents);

        storage.delete_file("docs/hello.txt").await.unwrap();
        assert!(!storage.file_exists("docs/hello.txt").await.unwrap());

        cleanup(&root).await;
    }

    #[tokio::test]
    async fn list_files_in_directory() {
        let (storage, root) = storage_with_root().await;

        storage
            .write_file_bytes("uploads/a.txt", b"a")
            .await
            .unwrap();
        storage
            .write_file_bytes("uploads/b.txt", b"b")
            .await
            .unwrap();
        storage
            .write_file_bytes("uploads/.keep", b"")
            .await
            .unwrap();

        let files = storage.get_files_in_dir("uploads").await.unwrap();
        assert_eq!(files, vec![".keep", "a.txt", "b.txt"]);

        cleanup(&root).await;
    }

    #[tokio::test]
    async fn delete_directory_removes_nested_content() {
        let (storage, root) = storage_with_root().await;

        storage
            .write_file_bytes("bundle/nested/file.bin", b"123")
            .await
            .unwrap();
        assert!(storage.directory_exists("bundle").await.unwrap());

        storage.delete_dir("bundle").await.unwrap();
        assert!(!storage.directory_exists("bundle").await.unwrap());
        assert!(!storage.file_exists("bundle/nested/file.bin").await.unwrap());

        cleanup(&root).await;
    }

    #[tokio::test]
    async fn rejects_path_traversal() {
        let (storage, root) = storage_with_root().await;

        let result = storage.write_file_bytes("../escape.txt", b"nope").await;
        assert!(result.is_err());

        cleanup(&root).await;
    }

    #[tokio::test]
    async fn files_are_confined_to_root_directory() {
        let (storage, root) = storage_with_root().await;

        storage
            .write_file_bytes("inside/root.txt", b"safe")
            .await
            .unwrap();

        let full_path = root.join("inside/root.txt");
        assert!(full_path.is_file());

        let outside_path = root.parent().unwrap().join("outside.txt");
        assert!(!outside_path.exists());

        cleanup(&root).await;
    }
}
