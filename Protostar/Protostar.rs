// | (c) Tremeschin, AGPLv3-only License | Protostar Project | //
#![allow(non_snake_case)]

/*
 *   Protostar is the shared code between all Rust projects.
 * We export a lot of common imports to be readily available
 * and define quality of life functions, classes that hopefully
 * are useful to one or more projects.
 */

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
pub use std::time::Duration;
pub use std::time::Instant;

// Path
pub use std::fs::remove_dir_all as _rmdir;
pub use std::fs::remove_file as _rmfile;
pub use fs_extra::dir::get_size as dirSize;
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

#[cfg(feature = "skia")]
pub use skia_safe as skia;

// ------------------------------------------------------------------------------------------------|

#[macro_export]
macro_rules! Protostruct {
    ($i:item) => {
        #[serde_as]
        #[derive(SmartDefault, Serialize, Deserialize, Clone, Debug, Setters)]
        #[serde(default)]
        $i
   }
}

#[macro_export]
macro_rules! Protoenum {
    ($i:item) => {
        #[serde_as]
        #[derive(SmartDefault, Serialize, Deserialize, Clone, Debug, Display)]
        $i
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

// Sets up Protostar logging, this shouldn't really crash..
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
// Protostar exports

pub mod Constants;

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
