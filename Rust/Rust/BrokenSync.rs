use crate::*;

// Mostly for learning, totally superseeded by Freewheel except for single-thread so keeping

/// Frequency-based syncronization primitive for callables
///
/// Be careful, frameSkip=false might lag behind A LOT and deadlock on Somes(())
pub struct BrokenSyncClient {
    pub callable: Box<dyn FnMut() + Send>,
    pub nextCall: Instant,
    pub frameSkip: bool,
    pub hertz: f64,
}

impl BrokenSyncClient {
    pub fn new(callable: impl FnMut() + Send + 'static, hertz: f64, frameSkip: bool) -> BrokenSyncClient {
        BrokenSyncClient {
            callable: Box::new(callable),
            nextCall: Instant::now(),
            hertz: hertz,
            frameSkip: frameSkip,
        }
    }
}

#[derive(SmartDefault)]
pub struct BrokenSyncManager {
    clients: Vec<BrokenSyncClient>,
}

impl BrokenSyncManager {
    pub fn add(&mut self, client: BrokenSyncClient) {
        self.clients.push(client);
    }

    /// 1. For the `BrokenSync` with smallest `nextCall` time if any:
    /// - `block=true` will sleep until the next call and call it
    /// - `block=false` will only call if pending calls are due
    ///
    /// Returns:
    /// - Some(()) if a call was made (useful for `while let Some(_) = manager.next(false) {}`)
    /// - None if no call was made
    pub fn step(&mut self, block: bool) -> Option<()> {
        let client = self.clients.iter_mut().min_by_key(|c| c.nextCall)?;
        let waitFor = client.nextCall - Instant::now();

        if !block && waitFor > Duration::from_secs(0) {
            return None;
        }

        // Wait for sync
        Thread::sleep(waitFor);

        // Sets nextCall based on frameSkip
        let dt = Duration::from_secs_f64(1.0 / client.hertz);
        client.nextCall = if client.frameSkip {Instant::now() + dt} else {client.nextCall + dt};

        // Call and return
        (client.callable)();
        return Some(());
    }

    /// Repeatedly calls `.step()` until no more calls are due
    ///
    /// **Note:** This might deadlock if expensive calls are made and the CPU chokes at the target BrokenSync::hz
    pub fn next(&mut self) {
        while let Some(_) = self.step(false) {}
    }
}
