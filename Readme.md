<div align="right">
【☰】Table of Contents 👆
</div>

<div align="justify">

<div align="center">
  <img src="./Broken/Resources/Broken.png" width="200">

  <h2>Broken Source Software</h2>

  <img src="https://img.shields.io/github/stars/BrokenSource/BrokenSource" alt="Stars Badge"/>
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2FBrokenSource%2FBrokenSource.json%3Fshow%3Dunique&label=Visitors&color=blue" alt="Visitors Badge"/>
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2FBrokenSource%2FBrokenSource.json&label=Page%20Views&color=blue" alt="Page Views Badge"/>
  <img src="https://img.shields.io/github/license/BrokenSource/BrokenSource?color=blue" alt="License Badge"/>
  <a href="https://t.me/brokensource">
    <img src="https://img.shields.io/badge/Telegram-Channel-blue?logo=telegram" alt="Telegram Channel Badge"/>
  </a>
  <a href="https://discord.gg/KjqvcYwRHm">
    <img src="https://img.shields.io/discord/1184696441298485370?label=Discord&color=blue" alt="Discord Badge"/>
  </a>

  <sub> 👆 Out of the many **Explorers**, you can be among the **Shining** stars who support us! ⭐️ </sub>

  <!-- <a href="Readme pt-BR.md"><img src="https://hatscripts.github.io/circle-flags/flags/br.svg" style="vertical-align: middle;" width="50"></a> -->
  <!-- <a href="Readme.md">      <img src="https://hatscripts.github.io/circle-flags/flags/us.svg" style="vertical-align: middle;" width="50"></a> -->
</div>

<br>

This _mono_-repository hosts the **📚 Shared Library** called **❤️‍🩹 Broken**, a **🎩 Manager Tool** of the same name, and **📦 Submodules** of all our **💎 Projects**. User first, trust and quality are our core values.

- **Framework**: A solution for project unification and consistency 🌟

- **Automation**: Easy deploy, spend more time **using** the Projects 🚀


<br>
<br>
<br>

# 🔥 Running From the Source Code

> **Please read all instructions** before executing them for tips, notes and troubleshooting

<br>

## ✅ Linux and MacOS

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle;" width="82">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle;" width="82">

  **Linux** 💎 **MacOS**
</div>

<sub><i><b>Note:</b> For MacOS, use [Homebrew](https://brew.sh/) package manager if needed 🍺</i></sub>

- **Install** [**Git**](https://git-scm.com/downloads) and [**Python**](https://www.python.org/downloads) for your platform

- Open a **Terminal** on some directory and run:

  ```bash
  git clone https://github.com/BrokenSource/BrokenSource
  ```
  ```bash
  python ./BrokenSource/brakeit
  ```

**And done**, you can now run `broken` and see all available commands 🚀

- Head back to the *Project* you want to run for further instructions 🍷

<sub><b>Note:</b> On subsequent runs, open a terminal inside `BrokenSource` folder and execute `python ./brakeit` script again</sub>


<br>

## ✅ Windows

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;" width="82">

  **Windows 10+**
</div>

**Open** some folder you want to download the code to on **Windows Explorer**

- Press `Ctrl+L` to focus the address bar and type `cmd` to open a terminal

- **Install** [**Git for Windows**](https://git-scm.com/downloads) with the command:
  ```ps
  winget install -e --id Git.Git --source winget
  ```

- **Install** [**Python**](https://www.python.org/downloads) with the command:
  ```ps
  winget install -e --id Python.Python.3.11
  ```

**Now**, run the same **Linux** and **MacOS** commands above

<br>

<sub><b>Note:</b> You might need to replace `/` with `\` on the second command and `python` to `python3` or add `.exe` to it</sub>

<sub><b>Note:</b> You don't need to use Winget (it's more practical), you can manual install Python and Git following the links above</sub>


<br>

## ⚠️ **Common** Troubleshooting

**Generic**:

<details>
  <summary>
    No such command <code>(project)</code> when running <code>broken (project)</code>
  </summary>
  <br>

  - Run `broken submodules` to clone all the public projects
  <br>
</details>

<br>

**Windows**:

<details>
  <summary>
    Shell Error: <i>execution of scripts is disabled on this system</i>
  </summary>
  <br>

  Following <a href="https://stackoverflow.com/a/4038991"><b>This Answer</b></a>, Open a PowerShell terminal as Administrator and run:

  ```powershell
  Set-ExecutionPolicy RemoteSigned
  ```
  <br>
</details>

<details>
  <summary>
    <a href="https://github.com/microsoft/winget-cli"><b>Winget</b></a> is not installed or available on your System
  </summary>
  <br>

  As [**Microsoft**](https://learn.microsoft.com/en-us/windows/package-manager/winget/#install-winget) says in their documentation, you have options:

  - Install it from the [**Microsoft Store**](https://apps.microsoft.com/detail/9NBLGGH4NNS1)

  - Open a PowerShell terminal and run:

  ```powershell
  Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe
  ```
  <br>
</details>



<br>
<br>
<br>

# 📦 Pre-compiled binaries

Head over to each project's **Releases** page and download the latest version for your platform if any available

Otherwise, you'll have to run from the source code

- **Help needed**: Package managers for Linux and MacOS are welcome, you'll be credited ❤️

Our **release binaries** follow the **naming convention** below:

- `$project_name-$operating_system-$cpu_architecture-$version.$extension`

where

<div align="center">

| **Variable**         | **Possible Values**         | **Notes**     |
|:--------------------:|:---------------------------:|:-------------:|
| `$project_name`      | Many                        | -             |
| `$operating_system`  | `linux`, `macos`, `windows` | _*1_          |
| `$cpu_architecture`  | `amd64`, `arm`              | _*1_          |
| `$version`           | `YYYY.MM.DD`                | _*2_          |
| `$extension`         | `.bin`, `.exe`              | Depends on OS |

</div>

We also provide a `.sha256` file for checksum for each binary for integrity verification

<sub><i>*1: We don't have the hardware to test on ARM or MacOS, so we can't provide binaries for those platforms. You likely can run from the source code</i></sub>

<sub><i>*2: Our versioning is based on a date format since most code is rolling release; we don't plan to have that many releases; they encode the rough timespan where the project was at and gets neatly sorted by name on file explorers</i></sub>

<sub><i><b>Warning for Windows:</b> Our binaries are 100% safe - you can read the source code - but are likely to be flagged dangerous by Windows Smart Screen, mistaken as a malware by your antivirus or blocked by Windows Defender, given enough people downloading and executing them. Code signing is expensive and we 1. Don't have a budget for it; 2. Are completely Open Source, no shady between the lines stuff</i></sub>


<br>
<br>
<br>

# 🚧 Hardware Requirements

<sup><b>Note</b>: This section is under construction</sup>

The faster the hardware (CPU, GPU, RAM), the faster the code will run.

Apart from memory restrictions your hardware should support some minimum technologies:

## Projects with PyTorch

## Projects with FFmpeg




<br>
<br>
<br>

# ❤️‍🩹 Contributing
Thanks for taking your time to contribute to Broken Source Software projects!!

- Apart from the usual "be nice", "be respectful", we have some guidelines to help you get started

## • Help Needed
- Designer needed for the logos and consistent art
- Packaging binaries on Linux and MacOS - package managers

## • Reporting Issues
- **We do not** test enough or at all the code on Windows or MacOS
- Always give **minimal steps** to reproduce the error (instructions or code)
- Most projects deal with Audio or Video, issues may be file-specific
- **We only support the latest versions of any given project**, we are rolling-release
  - <sub>We'll still help troubleshooting older code or releases, just don't except back-porting</sub>

## • Suggesting Enhancements
- Rejection of ideas on Free and Open Source Software is a common and intimidating problem to newcomers, so we want to reduce the fear and cooperate with you
- Not all suggestions matches the project original idea
- No commentaries are criticizing your person, rather your *work*
- **Stuff needs time and effort to be implemented**
- Feel absolutely free to debate on choices and ideas for the projects
- Do not be afraid to ask for help or guidance


<br>
<br>
<br>

# 💎 Acknowledgements

All the infrastructure in **Broken Source Software's Framework** and **Projects** wouldn't be possible without many programming language packages, software we use and exponentially more **Open Source Contributors** that made it possible. **To all of you**, an **uncountable list of direct and indirect contributors**, we thank you for your time and effort to make the world a better place ❤️‍🩹

Below a list, **not ordered by importance or relevance**, of the most notable software and people.

### General
- [**FFmpeg**](https://ffmpeg.org): _"A complete, cross-platform solution to record, convert and stream audio and video."_ - and they are not lying!!
- [**Linux**](https://www.linux.org): Father of Open Source and all the things
- [**Visual Studio Code**](https://code.visualstudio.com): _"Code editing. Redefined."_
- [**Stability AI**](https://stability.ai): AI by the people for the people. Many products
- [**Huggingface 🤗**](https://huggingface.co): Central repository for AI models made easy with Diffusers, Gradio, Transformers
- [**Khronos Group**](https://www.khronos.org): For OpenGL, GLSL, Vulkan
- [**NVIDIA**](https://www.nvidia.com): Bittersweet one, but CUDA and the GPU's technology are undeniably amazing
- [**GitHub Copilot**](https://copilot.github.com): Spend more time thinking architecture than implementation


### Python
- [**Python**](https://www.python.org): The programming language
- [**Poetry**](https://python-poetry.org): Package manager and virtual environments
- [**PyInstaller**](https://www.pyinstaller.org): A complete Python bundler for end user binaries
- [**Nuitka**](https://nuitka.net): A Python compiler to a redistributable portable binary
- [**ModernGL**](https://github.com/moderngl/moderngl): OpenGL made-easy wrapper
- [**GLFW**](https://www.glfw.org): Easy OpenGL window and input manager
- [**NumPy**](https://numpy.org): Numerical Python, the math behind the scenes
- [**Quaternion**](https://github.com/moble/quaternion): Built-in NumPy support for [Quaternions](https://www.youtube.com/watch?v=d4EgbgTm0Bg)<sup>Ew <a href="https://github.com/moble/quaternion/wiki/Euler-angles-are-horrible">Euler Angles</a></sup>
- [**DotMap**](https://github.com/drgrib/dotmap): Great and simple dot notation for dynamic dictionaries
- [**tqdm**](https://github.com/tqdm/tqdm): Progress bar for the terminal
- [**Rich**](https://github.com/Textualize/rich): Beautiful formatting in Python
- [**Loguru**](https://github.com/Delgan/loguru): Python logging made stupidly simple
- [**Forbiddenfruit**](https://github.com/clarete/forbiddenfruit): Monkey patching for builtins in Python
- [**Typer**](https://github.com/tiangolo/typer): Great Command Line Interfaces made easy
- [**Halo**](https://github.com/manrajgrover/halo): Beautiful spinners on the terminal
- [**Appdirs**](https://github.com/ActiveState/appdirs): Platform specific user directories
- [**Pillow**](https://github.com/python-pillow/Pillow): Complete Imaging Library for Python
- [**Aenum**](https://github.com/ethanfurman/aenum): Advanced enums in python
- [**TOML**](https://github.com/uiri/toml): Python [TOML](https://toml.io/en/) file support
- [**Schedule**](https://github.com/dbader/schedule): Python job scheduling for humans
- [**attrs**](https://github.com/python-attrs/attrs): Python classes without boilerplate
- [**intervaltree**](https://github.com/chaimleib/intervaltree): Timeline-like intervals made easy
- [**PyTorch**](https://pytorch.org): General AI and Machine Learning
- [**isort**](https://github.com/PyCQA/isort): _isort_ your imports, so you don't have to
- [**imgui**](https://github.com/ocornut/imgui): Bloat-free hacky-vibes user interface
- [**DearPyGui**](https://github.com/hoffstadt/DearPyGui): Awesome User Interfaces for Python
- [**SoundCard**](https://github.com/bastibe/SoundCard): A Pure-Python Real-Time Audio Library
- [**Imageio-FFmpeg**](https://github.com/imageio/imageio-ffmpeg): Bundling FFmpeg binaries so I don't have to
- [**mido**](https://pypi.org/project/mido): MIDI Files manipulation in Python

### Rust
- [**Rust**](https://www.rust-lang.org): The programming language
- _Incomplete list_

### Package Maintainers
Package managers for Linux and MacOS are welcome, you'll be credited ❤️

<br>
<sub><i><b>Note:</b> It is very likely that I've missed someone, contact me if you feel something should be here!</i></sub>

<br>
<br>
<br>

# ⚖️ License and Fair Use

> **We are not** _"Source Available"_ or _"Open Core"_ software. **We are** _**Free and Open Source Software**_.

- By contributing to the Projects, you inherently agree to the **License** and **Terms** below.

- We deeply trust the user and community, but there is no free lunch. Please read carefully.

<br>

**The terms below** are **simple** yet detailed - **be fair** and **responsible**, **credit** us and **retribute** the favor if you can, only sell stuff you own, independent SAAS derivative work is not allowed for now.

<br>

## 🎓 Basic Terms
- 📝 **All Projects have their own License**; unless specified in the Code or `Readme.md` on the Project's Root or Subdirectories, all Files are subject to the `License.md` and `Readme.md` on the respective Repository and current terms. **Additional terms below apply** for the **Usage** of all the Projects.

- 📈 We hope that using more _"restrictive"_ licenses will keep the projects free from abuse. A feedback loop of **sharing** and **improving**.

- 🍻 You may contribute or use any project as long as you adhere to the **License** and **Terms**.

- There is **_no warranty_** of the Software. However, **it improves over time** and we are open to **fixing** it.

<br>

## 👤 User Generated Content
- 🖋 You are responsible for the **User Generated Content** you create, any copyright or law infringements are your own responsibility. You must own the assets you use.

- 🧨 We take **no responsibility** for any **damage** caused by the use of our projects on you or others, directly or indirectly. May it be a _broken_ system, hardware damage, social damage, etc.

- ⚠️ By default, all **User Generated Content** follows under the [**CC-BY 4.0 License**](https://creativecommons.org/licenses/by/4.0/).

<sub><b>Note:</b> While we won't enforce punishments for failed attributions, we would appreciate if you could credit us.</sub>

<br>

## 🤝 Fair Use
- 💝 Projects takes many human-hours to be created, consider retributing the favor by **donating** if you can or made money with them, do **share** the projects with others.

- 💰 We are **not** against **Commercial** use, but we are against **abuse** of the projects and their code. Be fair, get in touch with us, we'll be happy to help both sides grow.

- 🚫 We **do not allow selling** assets you **do not own**, you must distribute them freely for demonstration, research and/or educational purposes. External copyright laws apply.

<br>

## 🎩 Commercial Usage
Want to **use** our **Projects** for **Your Company** or **YouTube Channel**?

- Let's do something great together, contact us at [**Broken Source Software**](https://github.com/BrokenSource)

<br>

## 📚 Software as a Service
- 📡 We are **actively looking** for ways to transform our **Projects** into a **Software as a Service** (SAAS) model for the user's convenience. **Contact us** if you are interested in **collaborating**.

- ✅ No, we are not closing the Source Sode, nor the service shall receive any special(er) treatment.

- ✅ The service won't be greedy, but also can't be entirely free (due computational costs).

- 🔏 We reserve the right to have a closed-source version of the _service_ that uses, externally, the code-bases of any Project. Something similar to what [**Stability AI**](https://stability.ai) does with [**Clipdrop**](https://clipdrop.co)

<sub><b>Note:</b> Until later notice, you must contact us and work together on any SAAS derivative work ❤️‍🩹</sub>

<br>
<br>
<br>

# 👁 Privacy Policy
- ✅ Broken Source Software, via locally executed software, **does not collect any data** from the user for Analytics, **period**<sup><i>*1</i></sup>.

- 🌐 Our software **may download third-party assets** from the internet, such as **FFmpeg** binaries, **PyTorch** models, **Fonts**, **Images**. You inherently agree with the Terms of the third-parties download Servers and Software, as they are required for the Projects to work.

<sub><i>*1:</i> As a consequence, we don't have any analytics or metrics to improve the software (prioritize features, fix bugs, etc), so we rely on user feedback and bug reports</sub>

</div>
