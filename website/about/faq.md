
## General

### **Q:** Can you make X thing run faster? {#make-it-faster}

Most likely not, but maybe- I'm **very** sensitive to speeds and latencies by myself, and have already done lots of optimizations and micro-benchmarks to squeeze the most out of the hardware and language I use. Sure, there are always things that can be improved, but anything past doing stuff in parallel (rendering), and _specially_ if the CPU/GPU are already nearing 100% usage on your system, it's simply a matter of the hardware's capabilities.

<hr>

## DepthFlow / ShaderFlow

### **Q:** The program closes right before rendering (segfaults) {#exporting-segfault}

Your hardware _probably_ doesn't support rendering while there are mapped buffers in OpenGL, which happens when [TurboPipe](https://github.com/BrokenSource/TurboPipe) is enabled (default). This is likely to take place on older systems (GTX <= 800) or integrated GPUs from Intel or AMD and/or hybrid systems.

:material-arrow-right: Fix: disable it on the `main` **command** as in `depthflow main (...) --no-turbo`

> **Sidenote**: There's no easy way to detect support for it. [Most users](https://store.steampowered.com/hwsurvey/) have a decently modern GPU and the speed gains are too good to pass on, so it's enabled by default

<hr>

### **Q:** Rendered videos are black {#black-videos}

This seems to be a problem in hybrid systems, that is, a system that has both an integrated and dedicated GPU. While rendering in live mode in either GPU should work, OpenGL or Windows seems to have issues reading the rendered frames data from a GPU that is not the primary one.

See the next question [#wrong-gpu](#wrong-gpu) for a fix.

### **Q:** Wrong GPU being used for rendering {#wrong-gpu}

ShaderFlow says which GPU is being used for rendering:

```log
│DepthFlow├┤...│ Initializing scene 'DepthScene' with backend WindowBackend.GLFW
│DepthFlow├┤...│ OpenGL Renderer: NVIDIA GeForce RTX 3060/PCIe/SSE2
```

However, Hybrid Systems (Multiple GPUs) may be using the "wrong" one. This can cause issues such as black videos, low performance, artifacts, corrupted frames, etc:

```log
│DepthFlow├┤...│ Initializing scene 'DepthScene' with backend WindowBackend.GLFW
│DepthFlow├┤...│ OpenGL Renderer: Intel(R) RaptorLake-S Mobile Graphics Controller
```

:material-arrow-right: Fixing this highly depends on your platform:

<br>

:material-microsoft: **Windows** with NVIDIA <small>• thanks to [@stephanedebove](https://github.com/BrokenSource/DepthFlow/issues/83#issuecomment-2832210216)</small>

- Open the NVIDIA Control Panel, go to <kbd>Manage 3D Settings</kbd> → <kbd>Global Settings</kbd>
- Under <kbd>Preferred Graphics Processor</kbd> select <kbd>High-performance NVIDIA processor</kbd>
- Apply the changes, run depthflow/shaderflow again

<br>

:octicons-question-16: **Others** (any)

<sup><b>Help needed:</b> What are the instructions here?</sup>
