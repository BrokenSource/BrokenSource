#![allow(non_snake_case)]
#![allow(non_upper_case_globals)]

// Mostly std
pub use std::collections::BTreeMap;
pub use hashbrown::HashMap;
pub use hashbrown::HashSet;
pub use std::collections::VecDeque;
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
pub use std::error::Error;

// Sync, mutex, thread
pub use std::thread as Thread;
pub use std::cell::Cell;
pub use std::cell::RefCell;
pub use once_cell::sync::OnceCell;
pub use std::sync::Arc;
pub use std::sync::Mutex;
pub use std::sync::RwLock;
pub use std::rc::Rc;
pub use std::pin::Pin;

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
pub use uuid::Uuid as UUID;

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
pub use derivative::Derivative;
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

// Broken Rust Modules
pub mod Rust;
pub use Rust::*;
