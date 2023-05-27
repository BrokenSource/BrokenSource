use crate::*;

lazy_static::lazy_static! {
    // User and Base directories, if needed (ever)
    pub static ref User: directories::UserDirs = directories::UserDirs::new().unwrap();
    pub static ref Base: directories::BaseDirs = directories::BaseDirs::new().unwrap();

    // Per-project directories, call setupProjectDirectories("Project Name") once for initialization
    pub static ref Project: OnceCell<directories::ProjectDirs> = OnceCell::new();

    // Broken directories, for example, a single cache for FFmpeg downloads across projects
    pub static ref Common: directories::ProjectDirs = directories::ProjectDirs::from("com", "BrokenSource", "BrokenSource").unwrap();
}

// mkdir(exist_ok=True, parents=True)
pub fn makeCommonDirectories() -> Result<(), Box<dyn Error>> {
    info!("[Common Cache]      {:?}", Common.cache_dir());
    info!("[Common Config]     {:?}", Common.config_dir());
    info!("[Common Data]       {:?}", Common.data_dir());
    std::fs::create_dir_all(Common.cache_dir())?;
    std::fs::create_dir_all(Common.config_dir())?;
    std::fs::create_dir_all(Common.data_dir())?;
    return Ok(());
}

/// Sets up project directories based on given project name for Directories::Project
///
/// Access stuff with either
/// | let dirs = setupProjectDirectories("Project Name");
/// | dirs.cache_dir();
/// Or with
/// | Broken::Directories::Project.get().unwrap().cache_dir();
/// Or since we do use Broken::*; you can just do
/// | Directories::Project.get().unwrap().cache_dir();
/// | Directories::User.home_dir()
pub fn setupProjectDirectories(projectName: &str) -> &'static directories::ProjectDirs {
    let directories = Directories::Project.get_or_init(|| directories::ProjectDirs::from("com", "BrokenSource", projectName).unwrap());
    info!("[Cache]      {:?}", directories.cache_dir());
    info!("[Config]     {:?}", directories.config_dir());
    info!("[Data]       {:?}", directories.data_dir());
    return directories;
}
