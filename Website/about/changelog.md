<div style="text-align: justify;" markdown>

⭐️ Here you can find all the most significant changes made or ongoing to the software!

- Keep in mind this list isn't exhaustive, for the full thing, see commit history itself
- Unlisted projects might have received indirect changes from others or the main lib

<hr>

<!------------------------------------------------------------------------------------------------->

### 🔘 0.9.0 <small>Ongoing</small> {#0.9.0}

:material-arrow-right: You can run this version right now [from source](site:/get/source)!

**General**:

- Added support for Intel Macs and Linux Arm builds to the releases
- Actually fix FFmpeg automatic downloads on macOS (missing chmod)
- Many improvements on the Docker images, and publish them on GHCR
    - Vulkan now works inside docker for upscayl and ncnn upscalers
    - Publish images of tags `project-(latest,cpu,cu121)`
- Moderate code simplifications and refactoring throughout the codebase

**DepthFlow**:

- Add [Upscayl](https://github.com/upscayl/upscayl) as an upscaler option
- Fixed drag and drop of files due new lazy loading logic
- Improve dolly preset phase start to be more accurate
- Add stretch detection math on the shader for potential fill-in with gen ai
    - Command is `inpaint`, options `--black`, `--limit`
- Create a robust and fast `DepthServer` with FastAPI interface
- DepthMaps are now cached using diskcache for safer and safer cross-process access
- Rewrite the animation system to be more flexible and reliable
- Add colors filters (sepia, grayscale, saturation, contrast, brightness)
- Add transverse lens distortion filter (intensity, decay options)
- Base scene duration is now 5 seconds
- Internally interpolate isometric factor from 0.5 to 1 for better edges
- Overhaul animation system to be more flexible and reliable:
    - Completely serializable, changing any state parameter
- Reorganize website examples section into their own pages
- Cached depthmaps are now handled by `diskcache` for safer cross-process access
- Implement an API with FastAPI, Uvicorn accessible via `depthflow server`:
    - Fully serializable, simple json requests and responses
    - Videos are cached, same-hash requests are served from it
    - Configurable maximum simultaneous renders at any time


**ShaderFlow**:

- Enforce `#!py weakref.proxy()` on every module's `.scene` to allow for explicit `gc.collect()` to find circular references and clean up resources properly
- Assign all module scenes with a `weakref.proxy` for better gc collection
- Add an heuristic to use the headless context when exporting videos (TODO)
- Fix progress bar creation before ffmpeg command log causing a bad line
- Fix frametimer first frame being `dt=0`
- Rename `ShaderObject` to `ShaderProgram`
- Initial ground work on better metaprogramming and include system
- Partial overhaul and heavily simplify `ShaderTexture` class:
    - The `track` parameter is now a float ratio of the scene's resolution
- `ShaderTexture.track` is now a float ratio of the scene's resolution
- Drastically improve import times and consequently CLI startup times
- Speed improvements moving to float64 on dynamic number + partial rewrite:
    - Integral and derivatices are optional now, huge speedup as well
- Fix many _(dumb)_ memory leaks:
    - Do not recreate imgui context on every scene init
    - Release proxy render buffers that are piped to ffmpeg when done
    - Release texture objects when ShaderTexture is garbage collected
    - Enforce a `gc.collect()` on scene deletion for cyclic references
- Base duration of the scenes are now configurable (10 seconds default)
- Throw an exception when FFmpeg process stops unexpectedly
- Fix sharing a global watchdog causing errors on many initializations

<!------------------------------------------------------------------------------------------------->

### 🔘 0.8.0 <small>October 27, 2024</small> {#0.8.0}

**General**:

- Move away from [Rye](https://rye.astral.sh/) to [uv](https://astral.sh/) tooling
- ⚠️ **New** minimum version of Python: 3.10
- Bump managed Releases and From Source Python version to 3.12
- Releases download links now points to a version than `-latest.*`
- Move a lot of `Broken.*` global constants to a `Broken.Runtime` class
- **Unix** releases are now a `.tar.gz` file to preserve executable attribute
- Many improvements to `BrokenTyper` on REPL or non-REPL, direct or releases
- Restyle the website to a more modern look; lots of improvements and additions:
    - New Cloud Providers section on installation methods
    - Add this monolithic changelog than using blog posts
- Lots of releases management improvements. When running binaries **without args**:
    - A `version.tracker` text file is initialized or updated on all **PyApp** installed versions's root, which contains the last time the binary was run. If this is older than a week by default, a prompt will appear to delete the old installed version to save disk space.
    - Similarly, a `version.check` SQLite from `requests-cache` is created, which verifies the latest version of the software using PyPI endpoints each hour. A warning will be shown if a newer version is available; and a error will be shown if the current version is newer than the latest, which can indicate a yanked release or a time-traveller.
- Potential fix on macOS automatic downloads of a FFmpeg binary

**DepthFlow**:

- Implement batch export logic within the main command line
- PyTorch is now managed within a top-most CLI entry point
- Many improvements to the website documentation: Quickstart, examples, and more
- Added Apple's [DepthPro](https://github.com/apple/ml-depth-pro) as an Depth Estimator option
- The exported video now properly follows the input image's resolution
- Loading inputs is now _lazy_, and only happens at module setup before rendering
- Improved the Readme with community work, quick links, showcase

**ShaderFlow**:

- [**(#6)**](https://github.com/BrokenSource/ShaderFlow/issues/6) Move away from [pyimgui](https://pypi.org/project/imgui/) to [imgui-bundle](https://pypi.org/project/imgui-bundle/)
- Fix `Scene.tau` overlooked calculation, it was _half right!_
- Add optional frameskipping disabling on `Scene.main`
- Add optional progress callback on `Scene.main`
- The `Camera.zoom` is now how much is visible vertically from the center
- Add `Camera.fov` bound to `Camera.zoom`
- Use `numpy.dtype` instead of spaghetti methods on `Texture`
- Add many `Scene.log_*` methods for DRY 'who module's logging
- Performance improvements on not fitting rendering resolutions
- Add a `Uniform` class for convenience than the whole `Variable`
- Fix bug ensure the parent directory exists when exporting
- Revert `vflip`'s duty to FFmpeg than on the final sampling shader
- Renamed `Scene.main(benchmark=)` to `freewheel` (exporting mode)
- Internal code simplification and bug fixes

<!------------------------------------------------------------------------------------------------->

<hr>

### 🔘 0.7.1 <small>October 5, 2024</small> {id="0.7.1"}

- Fixed readme links to the website
- Fixed black video exports on Linux llvmpipe
- Fixed black video exports on macOS

<!------------------------------------------------------------------------------------------------->

</div>
