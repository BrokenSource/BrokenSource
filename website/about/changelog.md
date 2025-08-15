---
icon: material/file-document-edit
---

<style>
    li {margin-bottom: 2px !important;}
    p  {margin-bottom: 2px !important;}
</style>

### ✏️ v0.9.2 <small>August ??, 2025</small> {#0.9.2}

!!! example ""
    - Recalled all executable releases, enough users didn't see warnings
    - Fixed FFmpeg command line interface options missing
    - Ensure PowerShell is installed on `get.ps1`
    - Fix `NoUpscaler` shouldn't.. upscale
    - Stop providing lockfiles, as they can't split private projects well

### 📦 v0.9.0 <small>June 2, 2025</small> {#0.9.0}

!!! success ""
    - Fix FFmpeg automatic downloads on macOS (missing chmod)
    - Many improvements on the Docker images, and publish them on GHCR
        - Vulkan now works inside docker for upscayl and ncnn upscalers
        - Publish images of tags `project-{latest,0.9.0}-{cpu,cu121}`
    - Support for running all projects standalone mode without the monorepo
    - Add a hatchling build hook to set versions dynamically and pin for Pyaket
    - Heavy code simplifications and refactoring throughout the codebase
    - Improved import times across the board

### 📦 v0.8.0 <small>October 27, 2024</small> {#0.8.0}

!!! success ""
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
