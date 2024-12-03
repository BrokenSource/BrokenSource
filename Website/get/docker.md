---
title: Get/Cloud & Docker
---

## ☁️ Cloud

<b><span class="the">C</span>loud providers</b> are a great way to run the projects without the need of a powerful machine, to have a dedicated server for it, or scale up the usage. Naturally, there are a lot of providers to rent hardware from, with quirks and differences between them.

Getting OpenGL GPU acceleration to work is the trickiest part; if it's not listed here, you could try following the [**Docker**](#docker) section's of what needs to happen. _Consider improving this!_

- **Note**: When the GPU is not used in OpenGL, `llvmpipe` (CPU) device will be used. Rendering speeds will be abysmal, in the order of seconds per frame, {==**avoid at all costs**==}.

- **Note**: The examples below are only for properly setting up the environment for the projects to run. Continue after with any project's installation or usage for more.

- No conclusions, grading and guides are final, and can fail or be improved at any time.

{% include-markdown "include/love-short.md" %}


### 🔘 Amazon EC2

!!! example ""
    > <div><b>✅ &nbsp; #notsponsored • 🌐 <a href="https://aws.amazon.com/ec2/" target="_blank">Website</a><span style="float: right;">⭐️⭐️⭐️⭐️⭐️ (5.0/5.0)</span> • Works out of the box™</b></div>

    - Simply chose [`AWS Deep Learning AMI GPU PyTorch 2.4 (Ubuntu 22.04)`](https://aws.amazon.com/releasenotes/aws-deep-learning-ami-gpu-pytorch-2-4-ubuntu-22-04/) or similar!
    - No extra configuration needed, install the projects and continue


### 🔘 Runpod

#### Pods

!!! example ""
    > <div><b>✅ &nbsp; #notsponsored • 🌐 <a href="https://runpod.io/" target="_blank">Website</a><span style="float: right;">⭐️⭐️⭐️⭐️⭐️ (4.8/5.0)</span> • Minor fixes within user's reach</b></div>

    - Rent any pod with Nvidia GPUs (L4/T4 or cheapest should be enough)
    - Template: `runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04`

    After having access to a terminal, run the following:

    ```bash title=""
    # Installs required packages, adds the NVIDIA as a EGL vendor device
    apt update && apt install -y libegl1-mesa libglvnd-dev libglvnd0
    mkdir -p /usr/share/glvnd/egl_vendor.d
    echo '{"file_format_version":"1.0.0","ICD":{"library_path":"/usr/lib/x86_64-linux-gnu/libEGL_nvidia.so.0"}}' > /usr/share/glvnd/egl_vendor.d/10_nvidia.json
    export __EGL_VENDOR_LIBRARY_FILENAMES=/usr/share/glvnd/egl_vendor.d/10_nvidia.json
    ```

    - Install the projects and continue as usual

    For more context, see this [GitHub comment](https://github.com/akatz-ai/ComfyUI-Depthflow-Nodes/issues/8#issuecomment-2409098774){:target="_blank"} of mine.

#### Serverless

!!! example ""
    > <div><b>❓ &nbsp; #notsponsored • 🌐 <a href="https://runpod.io/" target="_blank">Website</a><span style="float: right;">(?/5.0)</span> • Unknown</b></div>

    Unknown.


### 🔘 Google Cloud

!!! example ""
    > <div><b>✅ &nbsp; #notsponsored • 🌐 <a href="https://cloud.google.com/" target="_blank">Website</a><span style="float: right;">⭐️⭐️⭐️⭐️<span style="font-size: 15px;">☆</span> (4.5/5.0)</span> • Minor changes needed</b></div>

    Goes mostly smooth by following the base dockerfiles, reportedly works with GPU Acceleration.


### 🔘 Modal

!!! example ""
    > <div><b>✅ &nbsp; #notsponsored • 🌐 <a href="https://modal.com/" target="_blank">Website</a><span style="float: right;">⭐️⭐️⭐️<span style="font-size: 15px;">☆☆</span> (3.0/5.0)</span> • Major changes needed + support ticket</b></div>

    - **You must** ask their support team to move your workspace to an older runner of theirs, as the newer ones don't expose `graphics` capabilities to Docker containers, failing to use the GPU.

    - **NVENC** is not available due _"security reasons"_; they can enable it if you're trustworthy, again, ask them.

    See [this script file](https://github.com/BrokenSource/BrokenSource/blob/main/Docker/Cloud/Modal.py) for running the projects on Modal!


### 🔘 Google Colab

!!! example ""
    > <div><b>❌ &nbsp; #notsponsored • 🌐 <a href="https://colab.research.google.com/" target="_blank">Website</a><span style="float: right;">⭐️<span style="font-size: 15px;">☆☆☆☆</span> (1.0/5.0)</span> • No GPU acceleration</b></div>

    - **⚠️ Important**: Colab [**disallows**](https://research.google.com/colaboratory/intl/en-GB/faq.html#disallowed-activities) WebUI usage in their free plan.

    - Doesn't seem to provide GPU acceleration for OpenGL.

    Here's my [**effort**](https://colab.research.google.com/drive/1C1mmq4GUrhBUeVoX04jAenE3Ex_IDqDB) on trying to get it working.


### 🔘 Replicate

!!! example ""
    > <div><b>❌ &nbsp; #notsponsored • 🌐 <a href="https://beam.cloud/" target="_blank">Website</a><span style="float: right;"><span style="font-size: 15px;">☆☆☆☆☆</span> (0.0/5.0)</span> • No OpenGL and Pydantic version conflict</b></div>

    - I am using [Pydantic](https://docs.pydantic.dev/latest/) version 2 for at least a couple of months, but they're stuck on v1.0 in `cog` and injecting on the environment for a good while, making it a dependency conflict hard to solve at runtime.

    - Not only that, when I tried plain `moderngl` for OpenGL, I couldn't get GPU acceleration to work.

    It's been a while since I tried it, it's probably possible to get it to work with some effort.


### 🔘 Inferless

!!! example ""
    > <div><b>❓ &nbsp; #notsponsored • 🌐 <a href="https://inferless.com/" target="_blank">Website</a><span style="float: right;">?/5.0</span> • No OpenGL acceleration?</b></div>

    A community member reportedly ran it basing off my main [dockerfile](https://github.com/BrokenSource/BrokenSource/blob/main/Docker/base.dockerfile), and OpenGL acceleration didn't work.

    - I don't have any more information or if this is true.


### 🔘 Beam Cloud

!!! example ""
    > <div><b>❓ &nbsp; #notsponsored • 🌐 <a href="https://beam.cloud/" target="_blank">Website</a><span style="float: right;">?/5.0</span></b></div>

    It's been a while since I tried it, but don't remember getting it to work.


<br>

## 🐳 Docker

<a href="https://www.docker.com" target="_blank"><b><span class="the">D</span>ocker</b></a> is a platform for containerization of software, easy deployment and scalability. Basic usage is relatively simple, and most Linux knowledge can be applied to it. The main problem for running the projects on Docker is getting OpenGL acceleration to work, as the focus of it are compute workloads (CUDA, ML) or services (Jellyfin, NextCloud, APIs, etc).

There are *quite a lot* of combinations in hardware[^1], platform and intention to use it, and guides like this can only go so far, and focuses on getting OpenGL working.

[^1]: Untested on AMD Radeon, Intel iGPU, Intel ARC. Your mileage may vary, here be dragons !

??? warning "**Docker can't open native GUIs** on the Host OS • The intended usage are:"
    - Implementing a backend _e.g._ with [**FastAPI**](https://fastapi.tiangolo.com){:target="_blank"}
    - Serving and acessing a [**Gradio**](https://www.gradio.app){:target="_blank"} web page
    - Isolation, security or **Headless** usage

### ⚡️ Installing

- (Windows) Install [**WSL2**](https://learn.microsoft.com/en-us/windows/wsl/install){:target="_blank"}, default Ubuntu 22.04 distro is fine
    ```powershell title="PowerShell"
    wsl --install
    ```
    - Preferably add an user with `sudo adduser <username>` (inside `wsl`)
    - And make it default `ubuntu config --default-user <username>`

<hr>

- Install [**Docker Desktop**](chttps://www.docker.com/products/docker-desktop/){:target="_blank"} for your platform or Package Manager
    - **Linux users** might only want [**Docker Engine**](https://wiki.archlinux.org/title/Docker){:target="_blank"}, per bloat and licensing model
    - **Windows**: Enable `Settings > Resources > WSL Integration > Default distro`

<hr>

- (Linux) You might need to install [**Docker Compose**](https://docs.docker.com/compose/){:target="_blank"} if you distro splits it

<hr>

- (NVIDIA) Install the [**NVIDIA Container Toolkit**](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-with-apt){:target="_blank"} for your Distro
    - I don't have to say _"Have NVIDIA Drivers installed"_, on the **host system**, do I?
    - **Windows**: Follow the `apt` instructions on the link above, inside WSL

!!! warning "**DO NOT INSTALL NVIDIA OR DISPLAY DRIVERS (MESA) ON THE WSL DISTRO [**PER NVIDIA DOCS**](https://docs.nvidia.com/cuda/wsl-user-guide/index.html#step-1-install-nvidia-driver-for-gpu-support){:target="_blank"}**"

<hr>

**Restart** the Docker Engine:

- (Linux) Run `sudo systemctl restart docker` on the Terminal
- (Others) Close and open Docker Desktop on the System Tray

!!! note "(Windows) It may be a good idea to reboot the whole system"

<hr>

- Clone the Monorepo following the [**🔥 From Source/Manual**](site:/get/source/#installing-manual){:target="_blank"} page, until `uv sync`

### 🚀 Context

Per Monorepo structure, I've configured a [**`.docker-compose.yml`**](https://github.com/BrokenSource/BrokenSource/blob/main/docker-compose.yml){:target="_blank"} file that builds a [**`base.dockerfile`**](https://github.com/BrokenSource/BrokenSource/blob/main/Docker/base.dockerfile){:target="_blank"} with common dependencies, and {>>hopefully<<} **OpenGL Acceleration**. The other dockerfiles starts of at the end of this base image for the specific project

??? tip "Have enough RAM and don't want to hurt your SSD's TBW?"
    Edit or create the file `sudo nano /etc/docker/daemon.json` and add:
    ```json
    {
        "data-root": "/tmp/docker",
        // ...
    }
    ```

Most Projects uses [**ModernGL**](https://github.com/moderngl/moderngl){:target="_blank"} for interfacing with OpenGL, that renders the Shaders. The Context creation is handled by [**glcontext**](https://github.com/moderngl/glcontext){:target="_blank"}, which selects the proper platform's API to use

<h3>What to avoid</h3>

**Long story short**, we want to avoid _at maximum_ using [**x11**](https://en.wikipedia.org/wiki/X.Org_Server) inside Docker {>>and even on native Linux !<<}. The code is feature-frozen but with many technical debts, requires a real _"Display"_ for Graphics APIs (OpenGL, Vulkan) to even work, and there is no headless mode

- One might think that prepending the commands with [**xvfb-run**](https://en.wikipedia.org/wiki/Xvfb){:target="_blank"} could work, but this will always use [**Software Rendering**](https://en.wikipedia.org/wiki/Software_rendering){:target="_blank"}, {>>which happens entirely on the CPU - a fraction of the speed of a GPU<<}. So, we {==want to avoid *xvfb* at all costs==}

This isn't an issue _per se_ when running natively, as OpenGL Contexts created on a live Desktop Environment _WILL_ have GPU Acceleration via [**GLX**](https://en.wikipedia.org/wiki/GLX){:target="_blank"}, provided by the current driver. Or EGL itself, if we're running [**Wayland**](https://wayland.freedesktop.org/){:target="_blank"}

<hr>

<h3>Why we want EGL</h3>

Luckily, **Khronos Group** developed [**EGL**](https://en.wikipedia.org/wiki/EGL_(API)), and **NVIDIA** the [**libglvnd**](https://github.com/NVIDIA/libglvnd){:target="_blank"} libraries. Together, EGL provides context creation directly on OpenGL without relying on WGL/CGL/GLX, so we can have **true GPU accelerated headless contexts**, and libglvnd a vender-neutral dispatch for so

**Well, not so fast.** That is, if the available devices are GPUs themselves. It is well known that NVIDIA provides their own Proprietary Drivers and firmware for their GPUs, with shared libraries {>>(`.so` files on Linux, `.dll` on Windows)<<} pointing to their driver's libraries; while AMD and Intel GPUs on Linux runs the Godly [**Mesa Project**](https://www.mesa3d.org/){:target="_blank"}. {==Mesa always at least provides `llvmpipe` device, which is a Software Rendering fallback device==}

<hr>

<h3>Native Linux vs WSL</h3>

Now, here's where it gets tricky. Docker is running a virtualized Linux machine always, but inside a _pseudo-native Linux_ in WSL (three layers lol). The previously installed [**NVIDIA Container Toolkit**](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installing-with-apt){:target="_blank"} deals with both cases slightly differently:

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

!!! success "For reference, here's the final [**Base Dockerfile**](https://github.com/BrokenSource/BrokenSource/blob/main/Docker/base.dockerfile){:target="_blank"} and [**docker-compose.yml**](https://github.com/BrokenSource/BrokenSource/blob/main/docker-compose.yml){:target="_blank"} files"

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
