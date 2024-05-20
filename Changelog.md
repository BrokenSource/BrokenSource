
<!------------------------------------------------------------------------------------------------>

# • [0.2.2] - (Staging)

> Implemented stuff awaiting a release

**General**:
    - The new minimum Python version is 3.9

**ShaderFlow**:

- **Bugfixes**:
    - Reset time when pressing "o" for resetting the Scene
    - Set `repeat=False` on shader texture, as it was wrapping pixels on `ssaa<1`
    - Progress bar no longer interfered with window visibility `log.info` (changed to `log.debug`)

- **Additions**:
    - Initial logic for batch exporting:
        - Add `hyphen_range` parser to the shared library for that
        - New `--batch/-b` command on ShaderScene's main
    - The `scale` is now an attribute, rather than carrying pre-multiplication on width and height

**Pianola**:
- Improved visuals, note border and beat markers

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
