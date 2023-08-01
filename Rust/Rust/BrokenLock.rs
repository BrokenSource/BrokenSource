use crate::*;

// At Broken Source Software we need no safety!
//
// Defines .get() and .set() methods on RwLock that implicitly calls .unwrap() on .read() and .write()
// Don't waste 5 minutes on what you can do in 5 seconds!
// (ps. all this for not wanting to type .unwrap() since BrokenSource code will obviously never panic)

pub trait BrokenRwLock<T> {
    fn get(&self) -> T;
    fn mutable(&self) -> std::sync::RwLockWriteGuard<T>;
    fn set(&self, value: T);
}

impl<T: Clone> BrokenRwLock<T> for RwLock<T> {

    /// Get T value _unsafely_
    fn get(&self) -> T {
        (*self.read().unwrap()).clone()
    }

    /// Get a .write() _unsafely_)
    fn mutable(&self) -> std::sync::RwLockWriteGuard<T> {
        self.write().unwrap()
    }

    /// Directly sets T value _unsafely_
    fn set(&self, value: T) {
        *self.mutable() = value.into();
    }
}
