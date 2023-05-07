
#[macro_export]
macro_rules! BrokenStruct {
    ($i:item) => {
        #[serde_as]
        #[derive(SmartDefault, Serialize, Deserialize, Derivative, Setters)]
        #[derivative(Debug)]
        #[serde(default)]
        $i
   }
}

#[macro_export]
macro_rules! BrokenEnum {
    ($i:item) => {
        #[serde_as]
        #[derive(SmartDefault, Serialize, Deserialize, Derivative, Display)]
        #[derivative(Debug)]
        $i
   }
}

/// Imports File.rs and use contents
#[macro_export]
macro_rules! BrokenImport {
    ($module:ident) => {
        pub mod $module;
        pub use $module::*;
    }
}
