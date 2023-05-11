use crate::*;

BrokenEnum! {
    #[derive(Clone)]
    pub enum SpinMode {
        #[default]
        /// Calls `.main()` as fast as possible (spins)
        Freewheel,
        /// Spins at a target frequency ("vsync")
        Frequency(f64),
        /// Calls `.main()` when Some(())
        Ondemand(Option<()>),
    }
}

/// Syncronization primitive for callables with a few modes
/// Optimized for structs that has RwLock<F> fields with
pub trait SpinWise: Sized + Sync + Send + 'static {

    /// Default implementation on how to spin, override for custom behavior
    fn spinMode(&self) -> SpinMode {
        SpinMode::Freewheel
    }

    /// None means to stop the spin
    fn main(self: &Arc<Self>) -> Option<()>;

    /// Creates a thread that calls FreewheelWise::main() on self
    /// according to `Spin::Spinmode`
    fn spin(self: Self) -> Arc<Self> {
        let ownerSelf = Arc::new(self);
        let threadSelf = ownerSelf.clone();

        Thread::spawn(move || {
            let main = || SpinWise::main(&threadSelf);
            let mut nextCall = Instant::now();

            loop {
                match threadSelf.spinMode() {
                    SpinMode::Freewheel => {},

                    SpinMode::Frequency(f) => {
                        Thread::sleep(nextCall - Instant::now());
                        nextCall += Duration::from_secs_f64(1.0 / f);
                    },

                    SpinMode::Ondemand(mut _value) => {
                        while let None = _value {
                            Thread::sleep(Duration::from_millis(1))
                        }
                        _value = Some(());
                    },
                };

                // Call main, exit when told so
                if main().is_none() {break}
            }
        });

        return ownerSelf;
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