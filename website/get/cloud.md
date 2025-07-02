---
icon: material/cloud
---

<b><span class="the">C</span>loud providers</b> are a great way to run the projects without the need of a powerful machine, to have a dedicated server for it, or scale up the usage. Naturally, there are a lot of providers to rent hardware from, with quirks and differences between them.

Getting OpenGL GPU acceleration to work is the trickiest part; if it's not listed here, you could try following the [**Docker**](site:get/docker) page of what needs to happen. _Consider improving this!_

- **Note**: When the GPU is not used in OpenGL, `llvmpipe` (CPU) device will be used. Rendering speeds will be abysmal, in the order of seconds per frame, {==**avoid at all costs**==}.

- **Note**: The examples below are only for properly setting up the environment for the projects to run. Continue after with any project's installation or usage for more.

- No conclusions, grading and guides are final, and can fail or be improved at any time.

--8<-- "include/love-short.md"


## Works


### Modal

!!! example ""
    > <div><b>✅ &nbsp; #notsponsored • 🌐 <a href="https://modal.com/">Website</a><span style="float: right;">⭐️⭐️⭐️⭐️⭐️<span style="font-size: 15px;"></span> (5.0/5.0)</span> • Works out of the box</b></div>

    - Must use NVIDIA T4 GPU as it's the only one exposing OpenGL through EGL.
    - Nicely integrates with Python scripts, plenty free credits, good docs.

    :material-arrow-right: [Example Script](https://github.com/BrokenSource/BrokenSource/blob/main/docker/cloud/modal_com.py)


### Runpod

#### Pods

!!! example ""
    > <div><b>✅ &nbsp; #notsponsored • 🌐 <a href="https://runpod.io/">Website</a><span style="float: right;">⭐️⭐️⭐️ (4.5/5.0)</span> • Minor fixes within user's reach</b></div>

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

    For more context, see this [GitHub comment](https://github.com/akatz-ai/ComfyUI-Depthflow-Nodes/issues/8#issuecomment-2409098774) of mine.

#### Serverless

!!! example ""
    > <div><b>✅ &nbsp; #notsponsored • 🌐 <a href="https://runpod.io/">Website</a><span style="float: right;">⭐️⭐️⭐️ (3.5/5.0)</span> • Minor fixes within user's reach</b></div>

    - Same as above, very annoying to push new docker images every time, weird api, but works.


### Google Colab

!!! example ""
    > <div><b>✅ &nbsp; #notsponsored • 🌐 <a href="https://colab.research.google.com/">Website</a><span style="float: right;">⭐️⭐️⭐️⭐️<span style="font-size: 15px;">☆</span> (4.0/5.0)</span> • Minor changes needed</b></div>

    - **⚠️ Important**: Colab [disallows](https://research.google.com/colaboratory/intl/en-GB/faq.html#disallowed-activities) WebUI usage in their free plan.
    - Some recent update added EGL support, didn't work previously.

    :material-arrow-right: [Example Notebook](https://colab.research.google.com/drive/1Wh8JwXNIws989yIsdIn2ESweip_62ivn)


## Unknown

### Replicate

!!! example ""
    > <div><b>❓ &nbsp; #notsponsored • 🌐 <a href="https://beam.cloud/">Website</a><span style="float: right;"><span style="font-size: 15px;">☆☆☆☆☆</span> (0.0/5.0)</span> • No OpenGL and Pydantic version conflict</b></div>

    - I am using [Pydantic](https://docs.pydantic.dev/latest/) version 2 for at least a couple of months, but they're stuck on v1.0 in `cog` and injecting on the environment for a good while, making it a dependency conflict hard to solve at runtime.

    - Not only that, when I tried plain `moderngl` for OpenGL, I couldn't get GPU acceleration to work.

    It's been a while since I tried it, it's probably possible to get it to work with some effort.

### Amazon EC2

!!! example ""
    > <div><b>❓ &nbsp; #notsponsored • 🌐 <a href="https://aws.amazon.com/ec2/">Website</a><span style="float: right;"><span style="font-size: 15px;">☆☆☆☆☆</span> (0.0/5.0)</span> • Reportedly works out of the box</b></div>

    Based on a single user report without proof:

    - Chose [`AWS Deep Learning AMI GPU PyTorch 2.4 (Ubuntu 22.04)`](https://aws.amazon.com/releasenotes/aws-deep-learning-ami-gpu-pytorch-2-4-ubuntu-22-04/) or similar!
    - No extra configuration needed, install the projects and continue

### Google Cloud

!!! example ""
    > <div><b>❓ &nbsp; #notsponsored • 🌐 <a href="https://cloud.google.com/">Website</a><span style="float: right;"><span style="font-size: 15px;">☆☆☆☆☆</span> (0.0/5.0)</span> • Minor changes needed</b></div>

    Based on a single user report without proof:

    - Goes mostly smooth by following the base dockerfiles, reportedly works with GPU Acceleration.

### Inferless

!!! example ""
    > <div><b>❓ &nbsp; #notsponsored • 🌐 <a href="https://inferless.com/">Website</a><span style="float: right;"><span style="font-size: 15px;">☆☆☆☆☆</span> 0.0/5.0</span> • No OpenGL acceleration?</b></div>

    A community member reportedly ran it basing off my main [dockerfile](https://github.com/BrokenSource/BrokenSource/blob/main/docker/base.dockerfile), and OpenGL acceleration didn't work.

    - I don't have any more information or if this is true.


### Beam Cloud

!!! example ""
    > <div><b>❓ &nbsp; #notsponsored • 🌐 <a href="https://beam.cloud/">Website</a><span style="float: right;"><span style="font-size: 15px;">☆☆☆☆☆</span> 0.0/5.0</span></b></div>

    It's been a while since I tried it, but don't remember getting it to work.
