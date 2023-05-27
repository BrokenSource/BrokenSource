#![allow(non_snake_case)]
use Broken::*;

// Spin constants
const SPIN_FREQUENCY: f64 = 10.0;
const DELTA_T: f64 = 1.0 / SPIN_FREQUENCY;

BrokenStruct! {
    struct Scene {
        time: RwLock<f64>,
    }
}

// Mut borrow test for Scene values
fn increasesTime(value: &mut f64) {
    *value += DELTA_T;
}

impl SpinWise for Scene {
    fn main(self: &Arc<Self>) -> Option<()> {

        // Proof of concept: Any of these 3 ways should work
        match 3 {
            1 => {
                increasesTime(&mut self.time.mutable());
            },
            2 => {
                *self.time.mutable() += DELTA_T;
            },
            3 => {
                self.time.set(self.time.get() + DELTA_T);
            },
            _ => {panic!("Bad")}
        }

        // Stop after 5 seconds
        if self.time.get() >= 5.0 {
            return None
        }
        Some(())
    }

    fn spin_mode(&self) -> SpinMode {
        let mut input = String::with_capacity(100);

        // Proof of concept: (1: "vsynced") (2: press enter to run) (3: free)
        match 1 {
            1 => SpinMode::Frequency(5.0),
            2 => {
                std::io::stdin().read_line(&mut input).unwrap();
                SpinMode::Ondemand(Some(()))
            },
            _ => {SpinMode::Freewheel}
        }
    }
}


fn main() {
    Broken::setupLog();
    let scene = Scene::default().spin();

    loop {
        Thread::sleep(Duration::from_millis(100));
        info!("(Main Thread) time: {:.3}", scene.time.get());
    }
}
