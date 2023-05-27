use crate::*;

// Basic logging
pub use log::{debug, error, info, trace, warn};

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
                "[{green}{:<4} ms{reset}]─[{level}{:<5}{reset}] ▸ {}",
                start.elapsed().as_millis(),
                record.level(),
                message,
                level = format_args!("\x1B[{}m", logColors.get_color(&record.level()).to_fg_str()),
                green = format_args!("\x1B[{}m", Color::Green.to_fg_str()),
                reset = "\x1B[0m"
            ))
        })
        .chain(std::io::stdout())
        .level(log::LevelFilter::Trace)
        .apply()
        .expect("Failed to set up logging");
}
