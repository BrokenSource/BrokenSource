use crate::*;

BrokenEnum! {
    #[derive(Clone)]
    pub enum SpinMode {
        /// Calls `.main()` as fast as possible
        #[default]
        Freewheel,
        /// Calls `.main()` at a target frequency ("vsync"), guaranteed if enough CPU resources
        Frequency(f64),
        /// Calls `.main()` when internal value is Some
        Ondemand(Option<()>),
    }
}

/// Syncronization primitive for callables with a few different modes
/// Optimized for structs that has RwLock<F> fields with
pub trait SpinWise: Sized + Sync + Send + 'static {

    /// Default implementation on how to spin, override for custom behavior
    fn spin_mode(&self) -> SpinMode {
        SpinMode::Freewheel
    }

    /// None means to stop the spin
    fn main(self: &Arc<Self>) -> Option<()>;

    /// Creates a thread that calls FreewheelWise::main() on self
    /// according to `Spin::Spinmode`
    fn spin(self) -> Arc<Self> {
        // Create an Arc reference from self that will
        // be returned and one that will be moved to the thread
        let owned_self = Arc::new(self);
        let thread_self = owned_self.clone();

        Thread::spawn(move || {
            let mut next_call = Instant::now();

            loop {
                match thread_self.spin_mode() {
                    SpinMode::Freewheel => {},

                    SpinMode::Frequency(f) => {
                        Thread::sleep(next_call - Instant::now());
                        next_call += Duration::from_secs_f64(1.0 / f);
                    },

                    SpinMode::Ondemand(mut _value) => {
                        while let None = _value {
                            Thread::sleep(Duration::from_millis(1))
                        }
                        _value = Some(());
                    },
                };

                // Call main, exit when told so
                if SpinWise::main(&thread_self).is_none() {break}
            }
        });

        return owned_self;
    }
}


// FIXME: For compatibility on PocketSolar, remove later? Useful anywhere locking the whole struct?

/// Freewheel a struct globally with RwLock<T> instead of the fields having their own RwLock<F>
pub trait SpinWhole: Sized + Sync + Send + 'static {
    fn main(this: Arc<RwLock<Self>>);

    /// Creates a thread that calls FreewheelWhole::main() on self
    fn spin(initialized: Self) -> Arc<RwLock<Self>> {
        let object = Arc::new(RwLock::new(initialized));
        let threadObject = object.clone();
        Thread::spawn(|| SpinWhole::main(threadObject));
        return object;
    }

    /// Spawns a FreewheelWhole::spin with a default initialized Self
    fn spin_default() -> Arc<RwLock<Self>> where Self: Default {
        return SpinWhole::spin(Self::default());
    }
}