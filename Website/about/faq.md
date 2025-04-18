
## General

### **Q:** Can you make X thing run faster? {#make-it-faster}

Most likely not, but maybe- I'm **very** sensitive to speeds and latencies by myself, and have already done lots of optimizations and micro-benchmarks to squeeze the most out of the hardware and language I use. Sure, there are always things that can be improved, but anything past doing stuff in parallel (rendering), and _specially_ if the CPU/GPU are already nearing 100% usage on your system, it's simply a matter of the hardware's capabilities.

<hr>

## DepthFlow / ShaderFlow

### **Q:** The program closes right before rendering (segfaults) {#exporting-segfault}

Your hardware _probably_ doesn't support rendering while there are mapped buffers in OpenGL, which happens when [TurboPipe](https://github.com/BrokenSource/TurboPipe) is enabled (default). This is likely to take place on older systems (GTX <= 800) or integrated GPUs from Intel or AMD and/or hybrid systems.

:material-arrow-right: Fix: disable it on the `main` **command** as in `depthflow main (...) --no-turbo`

> **Sidenote**: There's no easy way to detect support for it. [Most users](https://store.steampowered.com/hwsurvey/){:target="_blank"} have a decently modern GPU and the speed gains are too good to pass on, so it's enabled by default

<hr>

### **Q:** Rendered videos are black {#black-videos}

This seems to be a problem in hybrid Windows systems, that is, a system that has both an integrated and dedicated GPU. While rendering in live mode in either GPU should work, OpenGL or Windows seems to have issues reading the rendered frames data from a GPU that is not the primary one. To fix this, you can try the following:

- **NVIDIA**: Go to the NVIDIA Control Panel, _"Manage 3D settings"_, find either the System's Python if running from PyPI, or a `pyaket` if running From Releases, and select the dedicated GPU as the preferred one.

<sup><b>Note:</b> I don't have an hybrid system, so this setting doesn't show in the screenshot below.</sup>

<img src="https://github.com/user-attachments/assets/2b0bb178-6248-4109-aff6-975427e5d8bf"></img>

### **Q:** Wrong GPU being used for rendering {#wrong-gpu}

See this [related question](#black-videos) for changing the preferred GPU in NVIDIA systems.

<sup><b>Help:</b> What are the instructions for AMD and Intel GPUs?</sup>
