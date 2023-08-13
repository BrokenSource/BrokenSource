from . import *


@attrs.define
class BrokenAudio:

    # Data buffer and its type
    data: numpy.ndarray = None
    dtype = numpy.float32

    # File mode
    file: Path = None

    # Recorder mode
    recorder: Any = None
    device:   Any = None

    # Internal
    end: int = -1

    # FIXME: Maybe implement own audioread for better control

    def __init__(self, *args, **kwargs):
        self.__attrs_init__(*args, **kwargs)
        BrokenUtils.need_import("soundcard", "audioread")

    # # Properties utils

    @property
    def sample_rate(self) -> Option[int, None]:
        """Get the current audio sample rate"""
        if self.device:
            # FIXME: Recorder doesn't have a sample rate?
            return 44100
        elif self.file:
            return self.file.samplerate
        return self.__no_input_error()

    @property
    def channels(self) -> Option[int, None]:
        """Get the current number of audio channels"""
        if self.device:
            return self.device.channels
        elif self.file:
            return self.file.channels
        return self.__no_input_error()

    @property
    def duration(self) -> Option[float, None]:
        """Get the current audio duration in seconds, infinite for Recorder"""
        if self.device:
            return math.inf
        elif self.file:
            return self.file.duration
        return self.__no_input_error()

    @property
    def data_length(self) -> Option[int, None]:
        """Returns the current audio data length in samples"""
        if self.data is None:
            return None
        return self.data.shape[1]

    @property
    def type(self):
        return "file" if self.file else "recorder" if self.device else None

    # # Open device or file functions

    def open_file(self, file: Path) -> numpy.ndarray:
        """Opens an audio file and reads its contents into memory self.data"""
        log.info(f"Reading audio file [{file}] contents, might take some seconds on bigger files")

        if file is None:
            log.warning("No file provided on BrokenAudio")
            return

        # Open the audio file
        self.file = audioread.audio_open(file)

        # Read data from all buffers from bytes, "self.file.read_data()" is a generator of bytes
        self.data = numpy.frombuffer(
            # Join all byte chunks
            b"".join(self.file.read_data()),

            # 16-bit little-endian signed integer PCM data
            dtype=numpy.dtype(numpy.int16)
        ).reshape((-1, self.channels)).T

        # Convert and normalize to self.dtype
        self.data = self.data.astype(self.dtype) / 2**15

        # About 700 MB for 1 hour of 48 kHz stereo audio, do we need to make it better?
        log.fixme(f"Loaded full audio file [{file}] into memory [Size: {self.data.nbytes/1024/1024:.2f} MB], maybe implement progressive mode")

        return self.data

    @property
    def devices(self) -> list[str]:
        """Lists of all available audio devices"""
        return [device for device in soundcard.all_microphones(include_loopback=True)]

    @property
    def devices_names(self) -> list[str]:
        """List of all available audio devices's names"""
        return [device.name for device in self.devices]

    def log_available_devices(self):
        log.info(f"Available Audio Capture devices:")
        for device in self.devices:
            log.info(f" • {device.name}")

    def open_device(self, name: str=None, buffer_seconds: float=60) -> None:
        """
        - name: Opens the fuzzy-searched device name, or the default recorder device
        - buffer_seconds: How many seconds of audio to keep in memory
        """
        if name is None:
            for device in self.devices:
                if not device.isloopback:
                    continue
                log.success(f"Found loopback device [{device.name}]")
                self.device = device
                break
            else:
                log.warning("Couldn't find any loopback device, using default Microphone device")
                self.device = soundcard.default_microphone()

        # Fuzzy find device name string
        else:
            log.info(f"Fuzzy string searching for audio capture device with name [{name}]")
            fuzzy_name, confidence = BrokenUtils.fuzzy_string_search(name, self.devices_names)

            if fuzzy_name is None:
                log.error(f"Couldn't find any device with name [{name}] out of devices:")
                self.log_available_devices()
                return None

            # Find the device
            self.device = next((device for device in self.devices if device.name == fuzzy_name), None)

        # Open the recorder
        log.info(f"Opening recorder with device [{self.device}]")
        self.recorder = self.device.recorder(
            samplerate=self.sample_rate,
            channels=self.channels,
            blocksize=128
        ).__enter__()

        # Create the recorder data buffer
        self.create_data_buffer(buffer_seconds)

    def create_data_buffer(self, seconds=60):
        """Creates self.data buffer with the specified seconds. Useful on Recorder mode"""
        self.data = numpy.zeros((self.channels, seconds*self.sample_rate), dtype=self.dtype)

    # # Capture audio functions

    def add_data(self, data: numpy.ndarray, normalize: bool=True) -> Option[numpy.ndarray, None]:
        """Add data to the end of data buffer keeping the size, must be same channel dimensions"""

        # Check if data has same number of channels
        if data.shape[0] != self.channels:
            log.error(f"Data shape [{data.shape}] doesn't match data buffer shape [{self.data.shape}]")
            return None

        # Now we have to roll the data buffer and add the new data to the end
        self.data = numpy.roll(self.data, -data.shape[1], axis=1)
        self.data[:, -data.shape[1]:] = data

        return self.data

    def record(self, numframes: int=None) -> Option[numpy.ndarray, None]:
        """Capture all buffered audio from the recorder"""

        # Recorder is easy, just ask numframes
        if not self.device:
            log.error("No audio input device found")
            return None

        # Capture pending data, add to self.data return it
        return self.add_data(self.recorder.record(numframes=None).T.astype(self.dtype))

    def catch_up_recorder(self) -> numpy.ndarray:
        """Record everything that is pending on the recorder"""
        return self.record(numframes=None)

    def start_capture_thread(self) -> None:
        """Keep recording audio on a separate thread"""
        BrokenUtils.better_thread(self.catch_up_recorder, daemon=True, loop=True)

    # # Get data functions

    def get_data_between_samples(self, start: int, end: int) -> Option[numpy.ndarray, None]:
        """Get the audio data between two samples intervals, returns [channels][start:end], size (end - start) samples"""
        if self.data_length < end:
            log.warning(f"Audio buffer doesn't have enough data to get [{end}] samples, only has [{self.data_length}]")
            return None
        return self.data[:, int(start):int(end)]

    def get_data_between_seconds(self, start: float, end: float) -> Option[numpy.ndarray, None]:
        """Get the audio data between seconds intervals, returns [channels][start:end] size int(sample_rate*(end - start)) samples"""
        return self.get_data_between_samples(*self.sample_rate*numpy.array((start, end), dtype=int))

    def get_last_n_samples(self, n: int) -> Option[numpy.ndarray, None]:
        """Get the last n samples from the audio buffer relative to self.end, returns [channels][-n:]"""
        # TODO: Return zeros on the start if not enough data
        if (self.end >= 0) and (self.end < n):
            return self.get_data_between_samples(0, n)
        return self.get_data_between_samples(self.end-n, self.end)

    # # Internal functions

    def __no_input_error(self):
        log.error("No audio input device found")
        return None

    def info(self):
        log.info(f"Type:        [{self.type}]")
        log.info(f"Sample Rate: [{self.sample_rate}]")
        log.info(f"Channels:    [{self.channels}]")

# -------------------------------------------------------------------------------------------------|

class BrokenAudioFourierMagnitude:
    """"Given an raw FFT, interpret the complex number as some size"""
    amplitude = eval("lambda x: numpy.abs(x)")
    power     = eval("lambda x: x*x.conjugate()")

class BrokenAudioSpectrogramInterpolation:
    """Interpolate the FFT values, discrete to continuous"""
    euler = eval("lambda x: numpy.exp(-(x*1.3)**2)")
    sinc  = eval("lambda x: numpy.sinc(x)")

class BrokenAudioVolume:
    """Convert the FFT into the final spectrogram's magnitude bin (kinda volume)"""
    dBFsTremx = eval("lambda x: 10*(numpy.log10(x+0.1) + 1)/1.0414")
    dBFs      = eval("lambda x: 10*numpy.log10(x)")
    sqrt2     = eval("lambda x: x**0.5")
    linear    = eval("lambda x: x")

class BrokenAudioSpectrogramScale:
    """Functions that defines the y scale of the spectrogram. Tuples of f(x) and f^-1(x)"""

    # Octave, the most mathy one that will match the piano keys
    octave = (
        eval("lambda x: 12 * numpy.log10(x/440) / numpy.log10(2)"),
        eval("lambda x: 440 * 2**(x/12)")
    )

    # Personally not a big fan
    mel = (
        eval("lambda x: 2595 * numpy.log10(1 + x/700)"),
        eval("lambda x: 700 * (10**(x/2595) - 1)"),
    )

class BrokenAudioSpectrogramWindow:
    @functools.lru_cache
    def hann_poisson_window(N, alpha=2):
        """
        Generate a Hann-Poisson window.

        Parameters:
            N (int): The number of window samples.
            alpha (float): The parameter that controls the slope of the exponential.

        Returns:
            np.array: The window samples.
        """
        n = numpy.arange(N)
        hann_part = 0.5 * (1 - numpy.cos(2 * numpy.pi * n / N))
        poisson_part = numpy.exp(-alpha * numpy.abs(N - 2*n) / N)

        return hann_part * poisson_part

    @functools.lru_cache
    def hanning(size: int) -> numpy.ndarray:
        """Returns a hanning window of the given size"""
        return numpy.hanning(size)

@attrs.define
class BrokenAudioSpectrogram:
    audio: BrokenAudio

    # # FFT Options
    # 2^n FFT size, higher values, higher frequency resolution, less responsiveness
    fft_n: int = 12
    magnitude_function: callable = BrokenAudioFourierMagnitude.amplitude
    window_function:    callable = BrokenAudioSpectrogramWindow.hanning

    # Transformation Matrix functions
    scale:  Tuple[callable] = BrokenAudioSpectrogramScale.octave
    interpolation: callable = BrokenAudioSpectrogramInterpolation.euler

    # Spectrogram properties
    spectrogram_volume: callable = BrokenAudioVolume.linear
    spectrogram_frequencies: numpy.ndarray = None
    spectrogram_matrix:      numpy.ndarray = None

    @property
    def fft_size(self) -> int:
        """Returns the size of the FFT batch, in samples to be computed"""
        return int(2**self.fft_n)

    @property
    def fft_bins(self) -> int:
        """Returns the number of bins of the FFT"""
        return int(self.fft_size/2+1)

    @property
    def fft_frequencies(self) -> numpy.ndarray:
        """Returns the frequencies of each bin of the FFT, in Hz"""
        return numpy.fft.rfftfreq(self.fft_size, 1/self.audio.sample_rate)

    def fft(self, end: int=-1) -> numpy.ndarray:
        """Calculates the FFT of the last batch of samples"""
        data = self.window_function(self.fft_size) * self.audio.get_last_n_samples(self.fft_size)
        return self.magnitude_function(numpy.fft.rfft(data)).astype(self.audio.dtype)

    def spectrogram(self) -> numpy.ndarray:
        """Apply the transformation matrix to the FFT on each channel of self.fft"""
        return self.spectrogram_volume(numpy.array(
            [self.spectrogram_matrix @ channel for channel in self.fft()],
            dtype=self.audio.dtype)
        )

    @property
    def spectrogram_bins(self) -> int:
        return self.spectrogram_matrix.shape[0]

    def make_spectrogram_matrix(self,
        minimum_frequency: float=20,
        maximum_frequency: float=20000,
        bins: int=1000,
    ) -> tuple[numpy.ndarray, numpy.ndarray]:
        """
        Gets a transformation matrix that multiplied with self.fft yields "spectrogram bins" in custom scale

        The idea to get the center frequencies on the custom scale is to compute the following:
        $$ center_frequencies = T^-1(linspace(T(min), T(max), n)) $$

        Where T(f) transforms a frequency to some scale (for example octave or melodic)

        And then create many band-pass filters, each one centered on the center frequencies using
        Whittaker-Shannon's interpolation formula per row of the matrix, considering the FFT bins as
        a one-hertz-frequency function to interpolate, we find "the around frequencies" !

        # Returns (Frequencies, Transformation matrix)
        """
        log.info(f"Making Spectrogram Matrix ({minimum_frequency:.2f}Hz - {maximum_frequency:.2f}Hz) with {bins} bins)")

        # Get the linear space on the custom scale -> "frequencies to scale"
        transform_linspace = numpy.linspace(
            self.scale[0](minimum_frequency),
            self.scale[0](maximum_frequency),
            bins,
        )

        # Number of FFT bins
        fft_bins = self.fft_frequencies.shape[0]

        # Get the center frequencies on the octave scale -> "scale to frequencies", revert the transform
        self.spectrogram_frequencies = self.scale[1](transform_linspace)

        # Apply Whittaker-Shannon interpolation formula per row of the matrix
        # - https://en.wikipedia.org/wiki/Whittaker%E2%80%93Shannon_interpolation_formula
        self.spectrogram_matrix = numpy.array([
            self.interpolation(theoretical_index - numpy.arange(fft_bins))
            for theoretical_index in (self.spectrogram_frequencies/self.fft_frequencies[1])
        ], dtype=self.audio.dtype)

        return (self.spectrogram_frequencies, self.spectrogram_matrix)

    def make_spectrogram_matrix_piano(self,
        start: BrokenNote,
        end:   BrokenNote,
        extra: int=0,
    ):
        """
        Get the FFT to spectrogram matrix with the bins matched to piano keys
        - start: The first note of the piano
        - end:   The last note of the piano
        - extra: Add `extra` bins between each note
        """
        log.info(f"Making Spectrogram Piano Matrix from notes ({start.name} - {end.name})")
        return self.make_spectrogram_matrix(
            minimum_frequency=start.frequency,
            maximum_frequency=end.frequency,
            bins=((end.note - start.note) + 1) * (extra + 1),
        )
