#![allow(non_snake_case)]
#![allow(non_upper_case_globals)]

// Mostly std
pub use std::collections::HashMap;
pub use std::collections::HashSet;
pub use std::collections::BTreeMap;
pub use std::fs::File;
pub use std::io::BufReader;
pub use std::io::BufRead;
pub use std::io::BufWriter;
pub use std::io::Write;
pub use std::io::Read;
pub use std::net::TcpListener;
pub use std::net::TcpStream;
pub use std::path::PathBuf;
pub use std::path::Path;
pub use std::process::exit;
pub use std::process::Command as Subprocess;
pub use std::process::Stdio;
pub use std::sync::Arc;
pub use std::sync::RwLock;
pub use std::time::Duration;
pub use std::time::Instant;

// Path
pub use std::fs::remove_dir_all as _rmdir;
pub use std::fs::remove_file as _rmfile;
pub use regex::Regex;

// Math
pub use libm::*;
pub use unordered_pair::UnorderedPair;
pub use itertools::Itertools;
pub use num::complex::Complex64;
pub use rand;

// Cache
pub use lru_cache::LruCache;
pub use glob::glob;

// Serde and CLI
pub use clap::Parser;
pub use serde_derive::Deserialize;
pub use serde_derive::Serialize;
pub use serde_with::serde_as;
pub use strum::Display;
pub use toml::Value;

// Nice Set derive
pub use derive_setters::Setters;
pub use smart_default::SmartDefault;
pub use derive_new::new;
pub use str_macro::str;

#[cfg(feature="skia")]
pub use skia_safe as skia;

#[cfg(feature="ndarray")]
pub use {
    ndarray::Array,
    ndarray::Dim,
    ndarray_linalg::Inverse,
    ndarray_linalg::Solve,
};


// ------------------------------------------------------------------------------------------------|

#[macro_export]
macro_rules! BrokenStruct {
    ($i:item) => {
        #[serde_as]
        #[derive(SmartDefault, Serialize, Deserialize, Clone, Debug, Setters)]
        #[serde(default)]
        $i
   }
}

#[macro_export]
macro_rules! BrokenEnum {
    ($i:item) => {
        #[serde_as]
        #[derive(SmartDefault, Serialize, Deserialize, Clone, Debug, Display)]
        $i
   }
}

/// Import a module and export all its contents, useful for mod.rs folders
#[macro_export]
macro_rules! import {
    ($module:ident) => {
        pub mod $module;
        pub use $module::*;
    }
}

// ------------------------------------------------------------------------------------------------|

// Basic logging
pub use log::{debug, error, info, trace, warn};

// fstrings
pub use fstrings::println_f as printf;
pub use fstrings::format_args_f;
pub use fstrings::format_args_f as f;

// fstrings logging
#[macro_export]
macro_rules! debugf {($i:expr) => {debug!("{}", format_args_f!($i))}}
#[macro_export]
macro_rules! errorf {($i:expr) => {error!("{}", format_args_f!($i))}}
#[macro_export]
macro_rules! infof  {($i:expr) => { info!("{}", format_args_f!($i))}}
#[macro_export]
macro_rules! tracef {($i:expr) => {trace!("{}", format_args_f!($i))}}
#[macro_export]
macro_rules! warnf  {($i:expr) => { warn!("{}", format_args_f!($i))}}

// Sets up Broken logging, this shouldn't really crash..
pub fn setupLog() {
    use fern::colors::{Color, ColoredLevelConfig};

    // Time the program started
    let start = Instant::now();

    // Logging colors
    let logColors = ColoredLevelConfig::new()
        .error(Color::Red)
        .warn(Color::BrightYellow)
        .info(Color::White)
        .debug(Color::Blue)
        .trace(Color::BrightBlue);

    // Create fern log template
    fern::Dispatch::new()
        .format(move |out, message, record| {
            out.finish(format_args!(
                "[{green}{:<6} µs{reset}]─[{level}{:<5}{reset}] ▸ {}",
                // start.elapsed().as_millis(),
                start.elapsed().as_micros(),
                record.level(),
                message,
                level = format_args!("\x1B[{}m", logColors.get_color(&record.level()).to_fg_str()),
                green = format_args!("\x1B[{}m", Color::Green.to_fg_str()),
                reset = "\x1B[0m"
            ))
        })
        .chain(std::io::stdout())
        // .level(log::LevelFilter::Info)
        .level(log::LevelFilter::Trace)
        // .chain(fern::log_file("output.log").expect("Failed to set logging file"))
        .apply()
        .expect("Failed to set up logging");
}

// ------------------------------------------------------------------------------------------------|
// Directories

pub use once_cell::sync::OnceCell;

/// Access stuff with either
/// | let dirs = setupProjectDirectories("Project Name");
/// | dirs.cache_dir();
/// Or with
/// | Broken::Directories::Project.get().unwrap().cache_dir();
/// Or since we do use Broken::*; you can just do
/// | Directories::Project.get().unwrap().cache_dir();
/// | Directories::User.home_dir()
pub mod Directories {
    use crate::*;

    lazy_static::lazy_static! {
        // User and Base directories, if needed (ever)
        pub static ref User: directories::UserDirs = directories::UserDirs::new().unwrap();
        pub static ref Base: directories::BaseDirs = directories::BaseDirs::new().unwrap();

        // Per-project directories, call setupProjectDirectories("Project Name") once for initialization
        pub static ref Project: OnceCell<directories::ProjectDirs> = OnceCell::new();

        // Broken directories, for example, a single cache for FFmpeg downloads across projects
        pub static ref Broken: directories::ProjectDirs = directories::ProjectDirs::from("com", "BrokenSource", "BrokenSource").unwrap();
    }
}

// Sets up project directories based on given project name for Directories::Project
pub fn setupProjectDirectories(projectName: &str) -> &'static directories::ProjectDirs {
    Directories::Project.get_or_init(|| directories::ProjectDirs::from("com", "BrokenSource", projectName).unwrap())
}

// ------------------------------------------------------------------------------------------------|
// Broken exports

pub mod Constants {
    pub const AUTHOR: &str = "Tremeschin";
    pub mod About {
        pub const Ardmin:      &str = "Ardmin, an Ardour Session Minimizer.\n(c) 2023 Tremeschin, AGPLv3-only License.";
        pub const Harper:      &str = "Harper, a Terraria Symphony Tool.\n(c) 2023 Tremeschin, MIT License.";
        pub const HypeWord:    &str = "HypeWord, a Fun Livestream Chat Tool.\n(c) 2022-2023 Tremeschin, AGPLv3-only License.";
        pub const PocketSolar: &str = "PocketSolar, a Solar Panel IV Curve Tracker\n(c) Tremeschin, MIT License.";
        pub const PhasorFlow:  &str = "PhasorFlow, a Power Flow Tool.\n(c) Tremeschin, Proprietary License.";
        pub const ShaderFlow:  &str = "ShaderFlow, The Interactive Shader Renderer Platform.\n(c) 2023 Tremeschin, AGPLv3-only License.";
    }
}

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
