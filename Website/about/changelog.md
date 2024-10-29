<div style="text-align: justify;" markdown>

⭐️ Here you can find all the most significant changes made or ongoing to the software!

- Keep in mind this list isn't exhaustive, for the full thing, see commit history itself
- Unlisted projects might have received indirect changes from others or the main lib

<hr>

<!------------------------------------------------------------------------------------------------->

### 🔘 0.8.0 <small>Ongoing</small> {#0.8.1}

##### General {#0.8.1-general}

##### DepthFlow {#0.8.1-depthflow}
- Add [Upscayl](https://github.com/upscayl/upscayl) as an upscaler option
- Fixed drag and drop of files due new lazy loading logic

##### ShaderFlow {#0.8.1-shaderflow}
- Enforce `#!py weakref.proxy()` on every module's `.scene` to allow for explicit `gc.collect()` to find circular references and clean up resources properly

<!------------------------------------------------------------------------------------------------->

### 🔘 0.8.0 <small>October 27, 2024</small> {#0.8.0}

##### General {#0.8.0-general}

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

##### DepthFlow {#0.8.0-depthflow}

- Implement batch export logic within the main command line
- PyTorch is now managed within a top-most CLI entry point
- Many improvements to the website documentation: Quickstart, examples, and more
- Added Apple's [DepthPro](https://github.com/apple/ml-depth-pro) as an Depth Estimator option
- The exported video now properly follows the input image's resolution
- Loading inputs is now _lazy_, and only happens at module setup before rendering
- Improved the Readme with community work, quick links, showcase

##### ShaderFlow {#0.8.0-shaderflow}

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

<h5>ShaderFlow</h5>

- Fixed black video exports on Linux llvmpipe
- Fixed black video exports on macOS

<!------------------------------------------------------------------------------------------------->

</div>
