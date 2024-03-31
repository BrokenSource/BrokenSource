# 🔦 PyTorch

> Some projects have Optional or Total dependency on [PyTorch](https://pytorch.org/)

**Pick** one option below for your **Hardware** and run the **Command**. Have **Drivers installed**

| Type    | **Hardware** | **Command** | **Notes** |
|---------|--------------|-------------|-----------|
| GPU     | [**NVIDIA**](https://www.nvidia.com/download/index.aspx) + [CUDA](https://en.wikipedia.org/wiki/CUDA) | `poe cuda` | -
| GPU     | [**AMD**](https://www.amd.com/en/support) + [ROCm](https://en.wikipedia.org/wiki/ROCm) | `poe rocm` | [Linux only, >= RX 5000](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/reference/system-requirements.html)
| GPU     | Intel ARC    |  -          | -   |
| CPU     | Any          | `poe cpu`   | Slow |
| MacOS   | -            | `poe base`  | -   |

<sub><b>Note:</b> I don't have an AMD GPU or Macbook to test and give full support</sub>
