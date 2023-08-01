use crate::*;

// Import macros for importing other modules
pub mod Macros;
pub use Macros::*;

// Directories are self contained and linear
pub mod Directories;

BrokenImport!{Logging}
BrokenImport!{BrokenLock}
BrokenImport!{BrokenSync}
BrokenImport!{Constants}
BrokenImport!{Spin}

// ------------------------------------------------------------------------------------------------|
// FIXME: doko to put

pub fn betterGlob(globPattern: PathBuf) -> Vec<PathBuf> {
    glob(globPattern.into_os_string().into_string().unwrap().as_str())
        .expect("Bad glob pattern").flat_map(|e| e).collect()
}

pub fn remove(path: PathBuf) {
    if !path.exists() {
        return;
    } else {
        info!("Removing path [{}]", path.display());
        if path.is_dir() {
            _rmdir(&path)
        } else {
            _rmfile(&path)
        }
    }.expect(format!("Failed to remove path [{}]", path.display()).as_str());
}

pub fn moveFile(from: &PathBuf, to: &PathBuf) {
    std::fs::rename(&from, &to).expect(format!("Failed to move file [{}] to [{}]", from.display(), to.display()).as_str());
}
