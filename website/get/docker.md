---
icon: material/docker
---

<!-- Todo: Overhaul section wip -->
<!--
<b><span class="the">D</span>ocker</b> is a platform for containerization of software, easy deployment and scalability. The main problem for running the projects on Docker is getting OpenGL acceleration to work, as the focus of it are compute workloads or services.

There are *quite a lot* of combinations in hardware[^1], platform and intention to use it, and guides like this can only go so far, and focuses on getting OpenGL working.

[^1]: Untested on AMD Radeon, Intel iGPU, Intel ARC. Your mileage may vary, here be dragons !

??? warning "**Docker can't open native GUIs** on the Host OS • The intended usage are:"
    - Implementing a backend _e.g._ with [**FastAPI**](https://fastapi.tiangolo.com)
    - Serving and acessing a [**Gradio**](https://www.gradio.app) web page
    - Isolation, security or **Headless** usage

## Installation

### Docker

!!! bifurcation ""
    === ":material-microsoft: Windows"
        - Install [**Windows Subsystem for Linux 2**](https://learn.microsoft.com/en-us/windows/wsl/install) in a **PowerShell** terminal with:
        ```powershell title=""
        wsl --install
        ```
        - Install [**Docker Desktop**](chttps://www.docker.com/products/docker-desktop/), enable `Settings > Resources > WSL Integration > Distro`
    === ":simple-linux: Linux"
        - Install the [**Docker Engine**](https://wiki.archlinux.org/title/Docker)
        - Install [**Docker Compose**](https://docs.docker.com/compose/)
        - Install the [**NVIDIA Container Toolkit**](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-with-apt) for your Distro
        - Enable docker socket `sudo systemctl enable --now docker.socket`

- Enable docker socket `sudo systemctl enable --now docker.socket`

### Podman

## Running

You can either use prebuilt images or build them from source.

### Prebuilt images

I build and publish images to GitHub Container Registry (GHCR), you can see all of them [here](https://github.com/orgs/BrokenSource/packages). The last name part is the bundled PyTorch version, such as `cpu`, `cu124`. All `cu*` images uses CUDA and are NVIDIA GPU Exclusive.

You can run the following command

```shell title=""
docker run --rm --gpus all ghcr.io/brokensource/glinfo:latest-cpu
```

### Building images

Clone the monorepo [**from source**](site:/get/source), you can then run and build the images with:

```shell title=""
docker compose run --rm shaderflow
```

You can run the following command

https://github.com/orgs/BrokenSource/packages
 -->



<a href="https://www.docker.com"><b><span class="the">D</span>ocker</b></a> is a platform for containerization of software, easy deployment and scalability. Basic usage is relatively simple, and most Linux knowledge can be applied to it. The main problem for running the projects on Docker is getting OpenGL acceleration to work, as the focus of it are compute workloads (CUDA, ML) or services (Jellyfin, NextCloud, APIs, etc).

There are *quite a lot* of combinations in hardware[^1], platform and intention to use it, and guides like this can only go so far, and focuses on getting OpenGL working.

[^1]: Untested on AMD Radeon, Intel iGPU, Intel ARC. Your mileage may vary, here be dragons !

??? warning "**Docker can't open native GUIs** on the Host OS • The intended usage are:"
    - Implementing a backend _e.g._ with [**FastAPI**](https://fastapi.tiangolo.com)
    - Serving and acessing a [**Gradio**](https://www.gradio.app) web page
    - Isolation, security or **Headless** usage

### ⚡️ Installing

- (Windows) Install [**WSL2**](https://learn.microsoft.com/en-us/windows/wsl/install), default Ubuntu 22.04 distro is fine
    ```powershell title="PowerShell"
    wsl --install
    ```
    - Preferably add an user with `sudo adduser <username>` (inside `wsl`)
    - And make it default `ubuntu config --default-user <username>`

<hr>

- Install [**Docker Desktop**](chttps://www.docker.com/products/docker-desktop/) for your platform or Package Manager
    - **Linux users** might only want [**Docker Engine**](https://wiki.archlinux.org/title/Docker), per bloat and licensing model
    - **Windows**: Enable `Settings > Resources > WSL Integration > Default distro`

<hr>

- (Linux) You might need to install [**Docker Compose**](https://docs.docker.com/compose/) if you distro splits it

<hr>

- (NVIDIA) Install the [**NVIDIA Container Toolkit**](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-with-apt) for your Distro
    - I don't have to say _"Have NVIDIA Drivers installed"_, on the **host system**, do I?
    - **Windows**: Follow the `apt` instructions on the link above, inside WSL

!!! warning "**DO NOT INSTALL NVIDIA OR DISPLAY DRIVERS (MESA) ON THE WSL DISTRO [**PER NVIDIA DOCS**](https://docs.nvidia.com/cuda/wsl-user-guide/index.html#step-1-install-nvidia-driver-for-gpu-support)**"

<hr>

**Restart** the Docker Engine:

- (Linux) Run `sudo systemctl restart docker` on the Terminal
- (Others) Close and open Docker Desktop on the System Tray

!!! note "(Windows) It may be a good idea to reboot the whole system"

<hr>

- Clone the Monorepo following the [**🔥 From Source/Manual**](site:/get/source/#installing-manual) page, until `uv sync`

### 🚀 Context

Per Monorepo structure, I've configured a [**`.docker-compose.yml`**](https://github.com/BrokenSource/BrokenSource/blob/main/docker-compose.yml) file that builds a [**`base.dockerfile`**](https://github.com/BrokenSource/BrokenSource/blob/main/docker/base.dockerfile) with common dependencies, and {>>hopefully<<} **OpenGL Acceleration**. The other dockerfiles starts of at the end of this base image for the specific project

??? tip "Have enough RAM and don't want to hurt your SSD's TBW?"
    Edit or create the file `sudo nano /etc/docker/daemon.json` and add:
    ```json
    {
        "data-root": "/tmp/docker",
        // ...
    }
    ```

Most Projects uses [**ModernGL**](https://github.com/moderngl/moderngl) for interfacing with OpenGL, that renders the Shaders. The Context creation is handled by [**glcontext**](https://github.com/moderngl/glcontext), which selects the proper platform's API to use

<h3>What to avoid</h3>

**Long story short**, we want to avoid _at maximum_ using [**x11**](https://en.wikipedia.org/wiki/X.Org_Server) inside Docker {>>and even on native Linux !<<}. The code is feature-frozen but with many technical debts, requires a real _"Display"_ for Graphics APIs (OpenGL, Vulkan) to even work, and there is no headless mode

- One might think that prepending the commands with [**xvfb-run**](https://en.wikipedia.org/wiki/Xvfb) could work, but this will always use [**Software Rendering**](https://en.wikipedia.org/wiki/Software_rendering), {>>which happens entirely on the CPU - a fraction of the speed of a GPU<<}. So, we {==want to avoid *xvfb* at all costs==}

This isn't an issue _per se_ when running natively, as OpenGL Contexts created on a live Desktop Environment _WILL_ have GPU Acceleration via [**GLX**](https://en.wikipedia.org/wiki/GLX), provided by the current driver. Or EGL itself, if we're running [**Wayland**](https://wayland.freedesktop.org/)

<hr>

<h3>Why we want EGL</h3>

Luckily, **Khronos Group** developed [**EGL**](https://en.wikipedia.org/wiki/EGL_(API)), and **NVIDIA** the [**libglvnd**](https://github.com/NVIDIA/libglvnd) libraries. Together, EGL provides context creation directly on OpenGL without relying on WGL/CGL/GLX, so we can have **true GPU accelerated headless contexts**, and libglvnd a vender-neutral dispatch for so

**Well, not so fast.** That is, if the available devices are GPUs themselves. It is well known that NVIDIA provides their own Proprietary Drivers and firmware for their GPUs, with shared libraries {>>(`.so` files on Linux, `.dll` on Windows)<<} pointing to their driver's libraries; while AMD and Intel GPUs on Linux runs the Godly [**Mesa Project**](https://www.mesa3d.org/). {==Mesa always at least provides `llvmpipe` device, which is a Software Rendering fallback device==}

<hr>

<h3>Native Linux vs WSL</h3>

Now, here's where it gets tricky. Docker is running a virtualized Linux machine always, but inside a _pseudo-native Linux_ in WSL (three layers lol). The previously installed [**NVIDIA Container Toolkit**](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-with-apt) deals with both cases slightly differently:

- **On Windows**, the NVIDIA drivers used are from the Host (Windows itself), _"redirected"_ to WSL. The wrapped binaries are found at `/usr/lib/wsl` on the WSL distro, provided by the container toolkit {>>This is why no drivers should be installed on WSL<<}. The `llvmpipe` device _can be_ a pointer to `d3d12.so` file with actual GPU Acceleration

- **On Linux**, the NVIDIA drivers used are from the Host (Linux itself), directly. The files are found on regular `/usr/lib` location, provided by the container toolkit wrapping the host's drivers. No sketchy, `llvmpipe` is always software and a GPU device shows up

<hr>

<h3>But why is this important?</h3>

**If anything goes wrong** in this complicated soup of shared libraries, {==**your rendering speeds won't be 290 fps, but 40, 20, 5 fps at maximum**==}, without utilizing GPU

- The fun thing is that `/usr/lib/wsl` isn't mapped automatically to Docker on WSL 🤡

- Getting EGL to work on Cloud Providers can be tricky 🎈

<hr>

<h3>Talk is cheap, show me the code</h3>

Thankfully, we have `nvidia/opengl:1.2-glvnd-runtime-ubuntu22.04` image to start with

<hr>

We **absolutely need** to set those env vars:

```dockerfile
ENV NVIDIA_VISIBLE_DEVICES="all"
ENV NVIDIA_DRIVER_CAPABILITIES="all"
```

<hr>

**Additionally**, for ShaderFlow to use EGL, and not GLFW, set

```dockerfile
# Can disable with WINDOW_EGL=0 (sends backend=None to Window class)
ENV WINDOW_BACKEND="headless"

# Alternatively, use shaderflow scene class args
scene = ShaderScene(backend="headless")
```

!!! note "For pure ModernGL users:"
    Sending `backend="headless"` is the same as using the `moderngl_window.context.headless.Window` class, alongside sending a `backend="egl"` kwarg to that Window class initialization if `$WINDOW_EGL` is `"1"`

<hr>

**Almost done**, but there's some CLI args to go:

- **On Any platform**, we must add `--gpus all` to the Docker Engine's CLI for finding GPUs {>>If running from the configured `docker-compose.yml`, this is already configured<<}

- **On Windows**, due the `d3d12.so` lib hack, we must add `-v /usr/lib/wsl:/usr/lib/wsl` to the Docker Engine's CLI {>>Already configured on `docker-compose.yml`<<}. _That makes so we map the WSL's libraries of the Host OS's Drivers to Docker virtualized OS_

<hr>

<h3>Checking stuff is working</h3>

I've configured a Dockerfile for you to test your setup. Check its output messages:

```ps title="Terminal"
docker-compose run --build glinfo
```

If everything is nominal until now, you've _probably_ got a healthy setup 🎉

!!! success "For reference, here's the final [**Base Dockerfile**](https://github.com/BrokenSource/BrokenSource/blob/main/docker/base.dockerfile) and [**docker-compose.yml**](https://github.com/BrokenSource/BrokenSource/blob/main/docker-compose.yml) files"

### ⭐️ Usage

!!! heart "**This page helped you?**"
    Consider [**Joining my Sponsors**](site:/about/sponsors) and helping me continue everything !

<h3>All of that..</h3>

..was just for saying I've {>>suffered<<} and automated enough, so you can simply run:

```bash title="Terminal"
# Torch CPU already managed 😉
docker-compose run --build depthflow

# Somehow, faster than native linux?
docker-compose run --build shaderflow
```

!!! note "Funcionality is limited"
    You're expeceted to upload your own `.py` files in a separate Dockerfile (**recommended**), or edit the ones currently at `Docker/Scripts/*.py` for your current intentions (**anti-pattern**)

!!! success "In the future, there will be `$project-gradio` runnable images"

<h3>Your own Dockerfile</h3>

You can also build the `Docker/base.dockerfile` as `-t broken-base` and base off of it in yours dockerfiles with `FROM broken-base:latest` locally

- Not much different from how it works now:

```dockerfile
FROM broken-base:latest
CMD ["python3", "Docker/Scripts/depthflow.py"]
```

This way, no reinstall is required, and you have everything available right away

<br>


