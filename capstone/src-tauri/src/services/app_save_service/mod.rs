use crate::prelude::*;
use dirs::data_dir;
pub mod tauri_exports;

pub struct AppSaveService {
    pub save_dir: PathBuf,
}

impl AppSaveService {
    pub fn new(app_handle: AppHandle) -> Self {
        let save_path = AppSaveService::get_save_path_internal(&app_handle);
        if !save_path.exists() {
            fs::create_dir_all(save_path.clone()).expect("could not create App directory");
        }
        Self {
            save_dir: save_path,
        }
    }

    /// Example: `projects\project1`
    pub fn ensure_folder_created(&self, relative_path: impl AsRef<Path>) {
        let initial_path = self.save_dir.clone();
        let full_path = initial_path.join(relative_path);
        if let Err(err) = fs::create_dir_all(full_path) {
            println!("Warning when trying to create dir: {err}")
        }
    }

    /// Returns the full paths of all the items in the folder
    pub fn get_items_in_folder(
        &self,
        relative_path: impl AsRef<Path>,
    ) -> anyhow::Result<Vec<PathBuf>> {
        let mut items = Vec::new();
        let full_path = self.save_dir.join(relative_path);
        let read_dir = fs::read_dir(full_path)?;
        for item in read_dir.into_iter().flatten() {
            items.push(item.path())
        }
        Ok(items)
    }

    /// Returns the file names of all the items in the folder (with their extension)
    pub fn get_items_in_folder_names(
        &self,
        relative_path: impl AsRef<Path>,
    ) -> anyhow::Result<Vec<String>> {
        let mut items = Vec::new();
        let full_path = self.save_dir.join(relative_path);
        let read_dir = fs::read_dir(full_path)?;
        for item in read_dir.into_iter().flatten() {
            if let Some(fname) = item.path().file_name() {
                items.push(fname.to_string_lossy().to_string());
            }
        }
        Ok(items)
    }

    /// Checks to see if the file or directory exists
    pub fn exists(&self, relative_path: impl AsRef<Path>) -> bool {
        let full = self.get_full_path(relative_path);

        full.exists()
    }

    /// Returns the full path for a relative path
    pub fn get_full_path(&self, relative_path: impl AsRef<Path>) -> PathBuf {
        let relative_path = relative_path.as_ref();
        self.save_dir.join(Path::new(relative_path))
    }

    /// Example: `projects\project1\thing.json`
    pub fn save_json<T: Serialize>(
        &self,
        relative_path: impl AsRef<Path>,
        json: &T,
    ) -> anyhow::Result<()> {
        let initial_path = self.save_dir.clone();
        let full_path = initial_path.join(relative_path);
        let file = fs::File::create(full_path)?;
        let writer = BufWriter::new(file);

        serde_json::to_writer_pretty(writer, json).map_err(|e| anyhow::anyhow!(e))
    }

    pub fn read_file_string(&self, relative_path: impl AsRef<Path>) -> anyhow::Result<String> {
        let initial_path = self.save_dir.clone();
        let full_path = initial_path.join(relative_path);
        let content = fs::read_to_string(full_path)?;
        Ok(content)
    }

    pub fn read_json<T: for<'de> Deserialize<'de>>(
        &self,
        relative_path: impl AsRef<Path>,
    ) -> anyhow::Result<T> {
        let content = self.read_file_string(relative_path)?;
        serde_json::from_str(&content).map_err(|e| anyhow::anyhow!(e))
    }

    /// Copies a file from the source path to the destination path
    /// Example: `projects\project1\thing.json`
    pub fn copy_file(
        &self,
        source_path: impl AsRef<Path>,
        relative_dest_path: impl AsRef<Path>,
    ) -> anyhow::Result<()> {
        let initial_path = self.save_dir.clone();
        let full_path = initial_path.join(relative_dest_path);
        fs::copy(source_path, full_path)?;
        Ok(())
    }

    /// Deletes a file at the relative path
    /// Example: `projects\project1\images\photo.jpg`
    pub fn delete_file(&self, relative_path: impl AsRef<Path>) -> anyhow::Result<()> {
        let relative_path = relative_path.as_ref();
        let full_path = self.save_dir.join(Path::new(relative_path));
        fs::remove_file(full_path).map_err(|e| anyhow::anyhow!(e))
    }

    /// Deletes a folder and all its contents at the relative path
    /// Example: `projects\project1`
    pub fn delete_folder(&self, relative_path: impl AsRef<Path>) -> anyhow::Result<()> {
        let full_path = self.save_dir.join(relative_path);
        fs::remove_dir_all(full_path).map_err(|e| anyhow::anyhow!(e))
    }

    /// Moves/renames a folder from one relative path to another
    /// Example: from `projects\project1` to `archived\project1`
    pub fn rename_folder(
        &self,
        from: impl AsRef<Path>,
        to: impl AsRef<Path>,
    ) -> anyhow::Result<()> {
        let from_path = self.save_dir.join(from);
        let to_path = self.save_dir.join(to);
        fs::rename(from_path, to_path).map_err(|e| anyhow::anyhow!(e))
    }

    /// Get the save path for the app from the AppData directory
    fn get_save_path_internal(app: &AppHandle) -> PathBuf {
        let save_path = data_dir().expect("Could not find AppData directory");
        save_path.join(app.package_info().name.clone())
    }
}
