

## DepthFlow / ShaderFlow

### **Q:** Rendered videos are black

This seems to be a problem in hybrid Windows systems, that is, a system that has both an integrated and dedicated GPU. While rendering in live mode in either GPU should work, OpenGL or Windows seems to have issues reading the rendered frames data from a GPU that is not the primary one. To fix this, you can try the following:

- **NVIDIA**: Go to the NVIDIA Control Panel, _"Manage 3D settings"_, find either the System's Python if running from PyPI, or a `pyapp` if running From Releases, and select the dedicated GPU as the preferred one.

<sup><b>Note:</b> I don't have an hybrid system, so this setting doesn't show in the screenshot below.</sup>

<img src="https://github.com/user-attachments/assets/2b0bb178-6248-4109-aff6-975427e5d8bf"></img>
