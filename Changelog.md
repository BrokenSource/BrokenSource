
<!------------------------------------------------------------------------------------------------>

# • [0.3.3] - (Staging changes awaiting a release)

**Broken**:
- Fix: Always `.upper()` values from `LOGLEVEL`
- Add `valid: bool` on `BrokenPath` initialization istself, as `BrokenPath(None).valid()` is invalid
- Fix: `BrokenTyper` replace '_' with '-' on given command names and `tuple(map(str, args))` them
- Fixed BrokenAudioReader not yielding data if `chunk=0` when entering the context
- Rewrite FFmpeg file, options for easily exporting to H264, HEVC, AV1, VP9, (+NVENC alts)
- Rewrite Upscalers file, much more stable and better code
- Reimplement threaded stdin writing directly on `shell` command

**ShaderFlow**:
- Prompt the user to install audio server packages if `soundcard` import fails
- Always use EGL for creating the OpenGL context, disableable with `WINDOW_EGL=0`
- Safety checks for all modules to be initialized with `Module(self=instance(ShaderScene))`
    - Don't worry, a scene itself defaults `self.scene = self` so it is a scene !
    - This enables type hinting on the Module class, that depends on Scene, which depends on Module
- Always swap buffers even if on headless, NVIDIA driver was softlocking/hanging on benchmark mode
- Added `ShaderScene.cycle` variable. `tau` is normalized time, and `cycle` is norm angle `2pi*tau`
- Renamed `Message` to `ShaderMessage` for consistency (psa. Shader is short for ShaderFlow)
- Rename `ShaderScene.main(end)` to `ShaderScene.main(time)`
- The default quality level is now `50%`, for equal options on increasing or decreasing
- Rewrite Monocular Depth Estimators class, options for DepthAnything(1,2), ZoeDepth, Marigold
- Depth estimators now use and saves uint16 pngs file for better precision on large offsets
- The equirectangular 360° videos projection mode can now be 'zoomed' with regular zoom factor
- Added .on_frame BrokenRelay to ShaderVideo, for user option to process raw video frames
- Improved music visualizer demo scene

**DepthFlow**:
- Huge performance gains on the shader by walking on bigger steps first, then precise backwards
- Big performance gain on not calculating `tan(theta)` on every loop (that was uneventful lol)
- Per uint16 depth maps, removed the option to upscale them, as ncnn doesn't implement it
- Added a `vec2 iDepthCenter` shader variable for true camera offsets
- Renamed `focus->static` and `plane->focus` for better clarity
- Renamed all shader variables prefixes from `iParallax` to `iDepth`

<br>

<!------------------------------------------------------------------------------------------------>

# • [0.3.2] - (2024.05.29)

**General**:
- Iterate over `site.getsitepackages()` for finding PyTorch version instead of `[-1]`

**ShaderFlow**:
- Fix early Shader rendering when they weren't compiled on Windows
    - Caused by the hidden GLFW window signaling a resize when final resolution was set calculated
- Temporary Debug UI modules contents are expanded by default
- Add an opt-out `WINDOW_EGL=1` env var for Linux Headless rendering

**DepthFlow**:
- Add Depth of Field and Vignette post processing effects.
    - Disabled by default until better parameters are found, and maybe a faster blur

<br>

<!------------------------------------------------------------------------------------------------>

# • [0.3.1] - (2024.05.27)

**General**:
- Fixed PyApp releases of the projects in the new single wheel architecture
    - The venv is shared across same-version projects and managed by uv
    - **Fixme hack:** PyTorch flavor is being passed as `PYAPP_SELF_COMMAND` until we can send envs
- Projects requiring PyTorch now have a prompt to install it if not found
- Windows NTFS workaround on deleting the release venv if a reinstall is due
- Use newest version of PyApp, as yanked dependency specification was updated

**DepthFlow**:
- Use `SSAA=1.5` by default, for sharper images than brute forcing `quality` parameter

<br>

<!------------------------------------------------------------------------------------------------>

# • [0.3.0] - (2024.05.25)

> A bag of new featurs that will stabilize in the upcoming patch versions

**General**:
- The new minimum Python version is 3.9
- Added `Broken.temp_env` context, might be useful later
- Added `OnceTracker`, complementing `SameTracker` values
- Fix `StopIteration` on `BrokenPath.*.extract().rglob()` due bad Path with double output stems

**ShaderFlow**:

- **Bugfixes**:
    - Reset time when pressing "o" for resetting the Scene
    - Set `repeat=False` on shader texture, as it was wrapping pixels on `ssaa<1`
    - Progress bar no longer interfered with window visibility `log.info` (changed to `log.debug`)
    - Improve precision of finding a (numerator, denominator) on glfw.set_window_aspect_ratio
    - Integration on values close to target in Dynamics should not be skipped
    - Use multiple threads in PyTorch due NumPy import with `OMP_NUM_THREADS=1`

- **Additions/Changes**:
    - Initial logic for batch exporting:
        - Add `hyphen_range` parser to the shared library for that
        - New `--batch/-b` command on ShaderScene's main
    - The `scale` is now an attribute, rather than carrying pre-multiplication on width and height
    - Performance improvement on not importing full `arrow` on `ShaderScene.main`
    - Renamed `SHADERFLOW_BACKEND` to `WINDOW_BACKEND` env configuration
    - Add `.instant = True` mode on DynamicNumber, should be useful later on
    - Always build scenes when initializing, so it's not explicit or not assumes else;
        - Fixme: When one just wants the CLI, the full window and shader shall be loaded
    - Add `.duration` property to ShaderPiano, rename some attributes
    - Fix and rename the Motion Blur scene. Instead of bindless textures, return `vec4` switch case
    - The camera 2D Projection plane is now generic, slightly more costly but worth it
        - The plane is defined by `camera.plane_point` and `camera.plane_normal` on manual inits

**DepthFlow**:

- **Additions/Changes**:
    - Refactor `parallax_*` attributes to a state dictionary
    - Implement a new static-projections focal depth plane attribute

**Pianola**:
- Improved visuals, note border and beat markers
- Set initial time to minus roll time, so notes don't suddenly appear
- Set the Scene runtime to the Midi's one when loading
- Unify Midi loading on a `.load_midi` function

<br>

<!------------------------------------------------------------------------------------------------>

# • [0.2.1] - (2024.05.16)

**ShaderFlow**:
- Make `samplerate` dependency optional on `ShaderSpectrogram`, when `sample_rateio!=1`, now Linux shouldn't need C++ compilers to be installed on Python 3.10 or 3.11

**SpectroNote**:
- Don't resample audio - generally speaking, no information is gained

**Fixes**:
- Move staging/future dependencies to optional groups
- Fix Python 3.12 AttributeError of BrokenPath

<br>

<!------------------------------------------------------------------------------------------------>

# • [0.2.0] - (2024.05.15)

**ShaderFlow**:

- Fixes for True Headless rendering with `SHADERFLOW_BACKEND=headless` on Linux servers by using [**EGL**](https://en.wikipedia.org/wiki/EGL_(API)) backend on [**glcontext**](https://github.com/moderngl/glcontext) of the ModernGL Window, so `xvfb-run`/X11 is no longer needed, and GPU acceleration should work

- **Mechanism** to **enforce Aspect Ratio** on Scenes:
    - Without AR, keep previous resolution and override `-w` or `-h`
    - With AR, when one component is sent, calculate the other,-
    - If both are sent, calculates height based on width (prioritizes)
    - Option to limit to a maximum resolution (often the Monitor size)
    - Rounds to nearest multiple of two, so FFmpeg is happy

- **Performance improvements**:
    - The final Fractional SSAA Shader doesn't need the full pipeline
    - Pre-allocate a Buffer to copy each rendered frame to when exporting, to avoid the creation of a temporary `bytes` object
    - _Mystery_: Threaded pipes to FFmpeg subprocess on Linux are wayy faster than single threaded, even though they perform a COPY on each new frame and the subprocess stdin is a `BufferedIO`. Windows performance is comparable to Linux with synchronous code, as expected

**DepthFlow**:
- Now applies the new AR enforcing on loaded images resolution
- All of ShaderFlow above applies

**Known Issues**:
- AttributeError on BrokenPath in Python 3.12

**Fixes**:
- Added [**`cmake`**](https://github.com/tuxu/python-samplerate/tree/fix_cmake_dep) to `[build-system.requires]` for `samplerate`

<br>

<!------------------------------------------------------------------------------------------------>
