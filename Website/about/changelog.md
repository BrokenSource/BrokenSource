<style>
    ul {margin-top:    2px !important;}
    li {margin-bottom: 2px !important;}
    p  {margin-bottom: 2px !important;}
</style>


⭐️ All significant or ongoing changes to the projects are documented here!

- Unlisted ones may have been indirectly improved by shared code
- This list isn't exhaustive, see the commit history for full details

<hr>

### ✏️ v0.9.0 <small>Unreleased</small> {#0.9.0}

:material-arrow-right: You can run this version right now [from source](site:/get/source)!

!!! example ""
    === "General"
        - Bump managed and pyapp binaries Python to 3.13
        - Added support for Intel Macs and Linux Arm builds to the releases
        - Fix FFmpeg automatic downloads on macOS (missing chmod)
        - Many improvements on the Docker images, and publish them on GHCR
            - Vulkan now works inside docker for upscayl and ncnn upscalers
            - Publish images of tags `project-{latest,0.9.0}-{cpu,cu121}`
        - Support for running all projects standalone mode without the monorepo
        - Add a hatchling build hook to set versions dynamically and pin for PyApp
        - PyApp fork now installs files on `$user_local_data/BrokenSource/Versions`
        - Heavy code simplifications and refactoring throughout the codebase
        - Improved import times across the board
    === "DepthFlow"
        - Overhauled the Readme and the WebUI layout and content
        - Improvements to perceptual quality of the animation presets
        - Add a command line interface for all upscalers and depth estimators
        - Add [Upscayl](https://github.com/upscayl/upscayl) as an upscaler option
        - Fixed drag and drop of files due new lazy loading logic
        - Add stretch detection math on the shader for potential fill-in with gen ai
            - Command is `inpaint`, options `--black`, `--limit`
        - Add colors filters (sepia, grayscale, saturation, contrast, brightness)
        - Add transverse lens distortion filter (intensity, decay options)
        - Fix base scene duration is now 5 seconds
        - Overhaul animation system to be more flexible and reliable
        - Reorganize website examples section into their own pages
        - Cached depthmaps are now handled by `diskcache` for safer cross-process access
        - Refactor the shader for future include system external usage
        - Simplify  how the ray intersections are computed with ray marching
        - Fix how projection rays are calculated, as `steady`, `focus` were slightly wrong
    === "ShaderFlow"
        - Add an heuristic to use the headless context when exporting videos
        - Fix progress bar creation before ffmpeg command log causing a bad line
        - Fix frametimer first frame being `dt=0` instead of `1/fps`
        - Rename `ShaderObject` to `ShaderProgram`
        - Initial ground work on better metaprogramming and include system
        - Partial overhaul and simplify the `ShaderTexture` class
        - `ShaderTexture.track` is now a float ratio of the scene's resolution
        - Drastically improve import times and consequently CLI startup times
        - Speed improvements with float64 on dynamic number and optional aux vars
        - [**(#61)**](https://github.com/BrokenSource/DepthFlow/issues/61)  Fix many _(skill issue)_ memory leaks:
            - Use `#!py weakref.proxy()` on every module's `.scene` to allow for deeper `gc.collect()` to find circular references and clean up resources properly
            - Release proxy render buffers that are piped to ffmpeg when done
            - Release texture objects when ShaderTexture is garbage collected
            - Do not recreate imgui context on every scene init
        - Base duration of the scenes are now configurable (10 seconds default)
        - Throw an exception when FFmpeg process stops unexpectedly
        - Fix sharing a global watchdog causing errors on many initializations
        - Cleanup scheduler before module setup, fixes scene reutilization bug
        - Add a new 'subsample' parameter for better downsampling of SSAA>2
        - Use macros for initializing structs with fixed specification from uniforms
        - Bundle the `Examples` directory into `Resources` for wheel releases
        - Support for rendering videos "in-memory" without a named file on disk

<!------------------------------------------------------------------------------------------------->

### 📦 v0.8.0 <small>October 27, 2024</small> {#0.8.0}

!!! success ""
    === "General"
        - Move from [Rye](https://rye.astral.sh/) to [uv](https://astral.sh/) for tooling
        - New minimum Python version 3.10, bump managed to 3.12
        - Releases download links now points to a version than `-latest.*`
        - Linux/macOS releases are now a `.tar.gz` file to preserve executable attribute
        - Many improvements to `BrokenTyper` on REPL or non-REPL, direct or releases
        - Restyle the website to a modern look, content improvements, monolithic changelog
        - Lots of releases management improvements. When running binaries **without args**:
            - A `version.tracker` text file is initialized or updated on all **PyApp** installed versions's root, which contains the last time the binary was run. If this is older than a week by default, a prompt will appear to delete the old installed version to save disk space.
            - Similarly, a `version.check` SQLite from `requests-cache` is created, which verifies the latest version of the software using PyPI endpoints each hour. A warning will be shown if a newer version is available; and a error will be shown if the current version is newer than the latest, which can indicate a yanked release or a time-traveller.
        - Potential fix on macOS automatic downloads of a FFmpeg binary

    === "DepthFlow"
        - Implement batch export logic within the main command line
        - PyTorch is now managed in a top-level CLI entry point
        - Many improvements to the website documentation: Quickstart, examples, and more
        - Added Apple's [DepthPro](https://github.com/apple/ml-depth-pro) as an Depth Estimator option
        - The exported video now properly follows the input image's resolution
        - Loading inputs is now _lazy_, and only happens at module setup before rendering
        - Improved the Readme with community work, quick links, showcase

    === "ShaderFlow"
        - [**(#6)**](https://github.com/BrokenSource/ShaderFlow/issues/6) Move away from [pyimgui](https://pypi.org/project/imgui/) to [imgui-bundle](https://pypi.org/project/imgui-bundle/)
        - Fix `Scene.tau` overlooked calculation, it was _half right!_
        - Add optional frameskipping disabling on `Scene.main`
        - Add optional progress callback on `Scene.main`
        - The `Camera.zoom` is now the distance from the center to the top
        - Add `Camera.fov` bound to `Camera.zoom`, a simple tan atan relation
        - Use `numpy.dtype` instead of spaghetti methods on `Texture`
        - Add many `Scene.log_*` methods for DRY 'who module's logging
        - Do not fit rendering resolutions every frame (slow)
        - Add a `Uniform` class for convenience than the whole `Variable`
        - Fix bug ensure the parent directory exists when exporting
        - Revert `vflip`'s duty to FFmpeg than on the final sampling shader
        - Renamed `Scene.main(benchmark=)` to `freewheel` (exporting mode)
        - Internal code simplification and bug fixes

<!------------------------------------------------------------------------------------------------->

</div>
