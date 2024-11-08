## DepthFlow / ShaderFlow

### **Q:** The program closes right before rendering (segfaults)

Your hardware _probably_ doesn't support rendering while there are mapped buffers in OpenGL, which happens when [TurboPipe](https://github.com/BrokenSource/TurboPipe) is enabled (default). This is likely to take place on older systems (GTX <= 800) or integrated GPUs from Intel or AMD and/or hybrid systems.

:material-arrow-right: To fix this, you can go to the (DepthFlow) **WebUI's Advanced** tab and disable TurboPipe, or pass the `--no-turbo` flag to the `main` **command** as in `depthflow main (...) --no-turbo`

> **Sidenote**: There's no easy way to detect support for it. [Most users](https://store.steampowered.com/hwsurvey/){:target="_blank"} have a decently modern GPU and the speed gains are too good to pass on, so it's enabled by default.


### **Q:** Rendered videos are black

This seems to be a problem in hybrid Windows systems, that is, a system that has both an integrated and dedicated GPU. While rendering in live mode in either GPU should work, OpenGL or Windows seems to have issues reading the rendered frames data from a GPU that is not the primary one. To fix this, you can try the following:

- **NVIDIA**: Go to the NVIDIA Control Panel, _"Manage 3D settings"_, find either the System's Python if running from PyPI, or a `pyapp` if running From Releases, and select the dedicated GPU as the preferred one.

<sup><b>Note:</b> I don't have an hybrid system, so this setting doesn't show in the screenshot below.</sup>

<img src="https://github.com/user-attachments/assets/2b0bb178-6248-4109-aff6-975427e5d8bf"></img>
