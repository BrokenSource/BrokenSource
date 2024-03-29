【☰】Table of Contents 👆

<div align="justify">

<div align="center">
  <img src="./Broken/Resources/Images/Broken.png" width="200">

  <h2>Broken Source Software</h2>

  <img src="https://img.shields.io/github/stars/BrokenSource/BrokenSource?style=flat" alt="Stars Badge"/>
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2FBrokenSource%2FBrokenSource.json%3Fshow%3Dunique&label=Visitors&color=blue" alt="Visitors Badge"/>
  <img src="https://img.shields.io/github/license/BrokenSource/BrokenSource?color=blue" alt="License Badge"/>
  <img src="https://img.shields.io/pypi/v/broken-source"/>
  <a href="https://t.me/brokensource">
    <img src="https://img.shields.io/badge/Telegram-Channel-blue?logo=telegram" alt="Telegram Channel Badge"/>
  </a>
  <a href="https://discord.gg/KjqvcYwRHm">
    <img src="https://img.shields.io/discord/1184696441298485370?label=Discord&color=blue" alt="Discord Badge"/>
  </a>

  <sub> 👆 Out of the many **Explorers**, you can be among the **Shining** stars who support us! ⭐️ </sub>

  <!-- <a href="Readme pt-BR.md"><img src="https://hatscripts.github.io/circle-flags/flags/br.svg" style="vertical-align: middle;" width="50"></a> -->
  <!-- <a href="Readme.md">      <img src="https://hatscripts.github.io/circle-flags/flags/us.svg" style="vertical-align: middle;" width="50"></a> -->

  <br>

  Here lies **❤️‍🩹 Broken** (The **📚 Shared Library** and **🎩 Manager**) + **📦 Submodules** of all our **💎 Projects**
</div>

- **🌟 Framework**: A solution for Unification and Consistency

- **🚀 Automation**: Spend more time **using** the Projects


<br>
<br>
<br>

# 🔥 Running From the Source Code

> **Please read all instructions** before executing them for tips, notes and troubleshooting

- **Note**: The Tooling recently changed to [**Rye**](https://rye-up.com). Expect some rough edges

<details>
  <summary>
    Don't want to use <code>get.{sh,ps1}</code>?
  </summary>
  <br>

  - **Install** [**Git**](https://git-scm.com/downloads) and [**Rye**](https://rye-up.com) for your platform

  - **Windows**: Prefer using a PowerShell than the Command Prompt (CMD)

  <br>

  ```bash
  # Clone the Monorepo and all Submodules
  git clone https://github.com/BrokenSource/BrokenSource --recurse-submodules --jobs 4
  ```
  ```bash
  # Enter the Monorepo directory
  cd BrokenSource
  ```
  ```bash
  # Checkout all Submodules to the Master branch
  git submodule foreach --recursive 'git checkout Master || true'
  ```
  ```bash
  # Install Rye, Windows: https://rye-up.com
  curl -sSf https://rye-up.com/get | bash
  ```
  ```bash
  # Create the main Virtual Environment and install the dependencies
  rye sync
  ```
  ```bash
  # Activate the main Virtual Environment

  # Windows:
  .venv\Scripts\Activate.ps1

  # Linux and MacOS:
  source .venv/bin/activate # Bash
  soruce .venv/bin/activate.fish # Fish
  ```
</details>

<br>

## ✅ Windows

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;" width="82">

  **Windows 10+**
</div>

**Open** some folder you want to download the code to on **Windows Explorer**

- Press `Ctrl+L` and enter `powershell` to open a Terminal

  ```bash
  irm https://brakeit.github.io/get.ps1 | iex
  ```

**And done**, now run `broken` for a Command List 🚀

<br>

⚠️ **Enable** [**Developer Mode**](https://rye-up.com/guide/faq/#windows-developer-mode) for [Symlinks](https://en.wikipedia.org/wiki/Symbolic_link) to each Project's Workspace on its Folder

<br>

## ✅ Linux and MacOS

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle;" width="82">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle;" width="82">

  **Linux** 💎 **MacOS**
</div>

Open a **Terminal** on some directory and run
  ```bash
  /bin/bash -c "$(curl -sS https://brakeit.github.io/get.sh)"
  ```

**And done**, now run `broken` for a Command List 🚀

<br>
<br>
<br>

# 📦 Pre-compiled binaries

Head over to each project's **Releases** page and download the latest version for your platform, if available. Otherwise, you'll have to run directly from the Source Code

Our **release binaries** follow the **naming convention** below:

- `$project_name-$flavor-$operating_system-$cpu_architecture-$version.$extension`

where

<div align="center">

| **Variable**         | **Possible Values**         | **Notes**     |
|:--------------------:|:---------------------------:|:-------------:|
| `$project_name`      | Many                        | -             |
| `$flavor`            | Often empty                 | _*1_          |
| `$operating_system`  | `linux`, `macos`, `windows` | _*2_          |
| `$cpu_architecture`  | `amd64`, `arm`              | _*2_          |
| `$version`           | `YYYY.MM.DD`                | _*3_          |
| `$extension`         | `.bin`, `.exe`              | Depends on OS |

</div>

We also provide a `.sha256` file for checksum for each binary for integrity verification

- **Help needed**: Package managers for Linux and MacOS are welcome, you'll be credited ❤️

<br>

<sub><i>*1: Some projects might use PyTorch and include `cpu`, `cuda` or `rocm` flavors</i></sub>

<sub><i>*2: We don't have the hardware to test on ARM or MacOS, so we can't provide binaries for those platforms. You likely can run from the source code</i></sub>

<sub><i>*3: We use date versioning as we are rolling release and is neatly sorted by name on file explorers</i></sub>

<sub><i><b>⚠️ Warning for Windows:</b> Our binaries are 100% safe - you can read the source code - but are likely to be flagged dangerous by Windows Smart Screen, mistaken as a malware by your antivirus or blocked by Windows Defender, given enough people downloading and executing them. Code signing is expensive and we 1. Don't have a budget for it; 2. Are completely Open Source, no shady between the lines stuff</i></sub>

<br>
<br>
<br>

# 🗑️ Uninstalling

We have a partially implemented command for uninstalling, but it doesn't exist for release versions yet:
- `broken uninstall`

For now, you can just delete the directories we use below:

<br>

### Workspaces
The main Library uses [**AppDirs**](https://pypi.org/project/appdirs) to decide per-platform directories

For unification, all project's Workspaces are located at the User Data directory, followed by a AppAuthor and AppName subdirectories which will be `BrokenSource` and `ProjectName` in most cases
- **Linux**: `~/.local/share/AppAuthor/AppName/*`
- **Windows**: `%applocaldata%\AppAuthor\AppName\*`
- **MacOS**: `~/Library/Application Support/AppAuthor/AppName/*`

<br>

### Python Virtual Environment
Rye creates Virtual Environments on the `.venv` directory on the Monorepo root

The download cache if you chose `uv` instead of `pip-tools` is located at:
- **Linux**: `~/.cache/uv/*`
- **Windows**: `%localappdata%\uv\*`
- **MacOS**: `~/Library/Caches/uv/*`

<br>

### Releases Virtual Environment
We use [**PyApp**](https://github.com/ofek/pyapp) to make the releases. It unpacks itself on:
- **Linux**: `~/.local/share/pyapp`
- **Windows**: `%applocaldata%\pyapp`
- **MacOS**: `~/Library/Application Support/pyapp`

<br>
<br>
<br>

# ❤️‍🩹 Contributing
Thanks for taking your time for contributing to Broken Source Software Projects!!

**Main ways to contribute**:
- _Reporting issues_: See the Issue Template when creating a new Issue
- _Suggesting Features_: See the Feature Template when creating a new Issue
- _Pull Requests_: Code itself is the best way to contribute to the projects
- _Design and Art_: We need logos, icons, and consistent art for the projects
- _Package Maintainers_: Help us packaging the binaries for any platform
- **Get in Touch**: Contact us on [Discord](https://discord.com/invite/KjqvcYwRHm) or [Telegram](https://t.me/brokensource) to see how you can help!



<br>
<br>
<br>

# 🚧 Hardware Requirements

<sup><b>Note</b>: This section is under construction</sup>

**Golden Rule:** The faster the hardware (CPU, GPU, RAM), the faster the code will run.

Apart from memory restrictions your hardware should support some minimum technologies:

## Projects with PyTorch

## Projects with FFmpeg



<br>
<br>
<br>

# 💎 Acknowledgements

All the infrastructure in **Broken Source Software's Framework** and **Projects** wouldn't be possible without many Programming Language Packages, Software we use and exponentially more **Open Source Contributors** that made it possible. **To all of you**, an **uncountable list of direct and indirect contributors**, we thank you for your time and effort to make the world a better place ❤️‍🩹

Below a list, **not ordered by importance or relevance**, of the most notable software and people.

Some of them were once used, or learned from, yet are a token of gratitude and recommendation!

<br>

### Sponsorships
Be part of the **Explorers** and **Shining Stars** by sponsoring us! 🌟

<br>

### Package Maintainers
Package managers for Linux and MacOS are welcome, you'll be credited ❤️

<br>

### General
- [**FFmpeg**](https://ffmpeg.org): _"A complete, cross-platform solution to record, convert and stream audio and video."_
- [**Linux**](https://www.linux.org): Father of Open Source and all the things
- [**Visual Studio Code**](https://code.visualstudio.com): _"Code editing. Redefined."_
- [**Stability AI**](https://stability.ai): AI by the people for the people<sup>(Citation needed?)</sup>. Many products
- [**Huggingface 🤗**](https://huggingface.co): Central repository for AI models made easy with Diffusers, Gradio, Transformers
- [**Khronos Group**](https://www.khronos.org): For OpenGL, GLSL, Vulkan
- [**NVIDIA**](https://www.nvidia.com): Bittersweet one, but CUDA and the GPU's technology are undeniably amazing
- [**GitHub Copilot**](https://copilot.github.com): Spend more time thinking architecture than implementation

<br>

### Python
- [**Python**](https://www.python.org): The programming language
- [**Poetry**](https://python-poetry.org): Package manager and virtual environments
- [**Rye**](https://rye-up.com/): _"A Hassle-Free Python Experience"_
- [**Ruff**](https://github.com/astral-sh/ruff): _"An extremely fast Python linter and code formatter"_
- [**uv**](https://github.com/astral-sh/uv): _"An extremely fast Python package installer and resolver"_
- [**PyInstaller**](https://www.pyinstaller.org): A complete Python bundler for end user binaries
- [**Nuitka**](https://nuitka.net): A Python compiler to a redistributable portable binary
- [**ModernGL**](https://github.com/moderngl/moderngl): OpenGL made-easy wrapper
- [**GLFW**](https://www.glfw.org): Easy OpenGL window and input manager
- [**NumPy**](https://numpy.org): Numerical Python, the math behind the scenes
- [**NumPy Quaternion**](https://github.com/moble/quaternion): Built-in NumPy support for [Quaternions](https://www.youtube.com/watch?v=d4EgbgTm0Bg)<sup>Ew <a href="https://github.com/moble/quaternion/wiki/Euler-angles-are-horrible">Euler Angles</a></sup>
- [**DotMap**](https://github.com/drgrib/dotmap): Great and simple dot notation for dynamic dictionaries
- [**tqdm**](https://github.com/tqdm/tqdm): Progress bar for the terminal
- [**Rich**](https://github.com/Textualize/rich): Beautiful formatting in Python
- [**Loguru**](https://github.com/Delgan/loguru): Python logging made stupidly simple
- [**Forbiddenfruit**](https://github.com/clarete/forbiddenfruit): Monkey patching for built-ins in Python
- [**Typer**](https://github.com/tiangolo/typer): Great Command Line Interfaces made easy
- [**Halo**](https://github.com/manrajgrover/halo): Beautiful spinners on the terminal
- [**AppDirs**](https://github.com/ActiveState/appdirs): Platform specific user directories
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
- [**pyfiglet**](https://github.com/pwaller/pyfiglet): Pure Python easy Text ASCII art !
- [**opensimplex**](https://github.com/lmas/opensimplex): Simplex Noise in Python, fast
- [**pyapp**](https://github.com/ofek/pyapp): Bundling Python packages to installers
- [**ZeroMQ**](https://zeromq.org) and [**PyZMQ**](https://github.com/zeromq/pyzmq): Fastest pipes in the west

<br>

### Rust
- [**Rust**](https://www.rust-lang.org): The programming language
- _Incomplete list_

<br>
<sub><i><b>Note:</b> It is very likely that I've missed someone, contact me if you feel something should be here!</i></sub>

<br>
<br>
<br>

# ⚖️ License and Fair Use

> **We are not** _"Source Available"_ or _"Open Core"_ software. **We are** _**Free and Open Source Software**_

- By contributing and using to the Projects, you agree to the **License** and **Terms** below

**The terms** are **simple** yet detailed - **be fair** and **responsible**, **credit** us and consider **donating** !


## 🎓 Basic Terms
- 📝 **All Projects have their own License**, unless specified in the Code or some `Readme.md`

- ☑️ There is **_no warranty_** of the Software. However, **it improves over time** and we are open to **fixing** it


## 👤 User Generated Content
- 🖋 You are responsible for the **Content** you generate, external copyright laws applies

- ⚠️ By default, all **Content** you generate falls under the [**CC-BY 4.0 License**](https://creativecommons.org/licenses/by/4.0/)

<sub><b>Note:</b> While we won't enforce punishments for failed attributions, we would appreciate if you could credit us</sub>

## 🤝 Fair Use
- 💝 Projects takes many hours to be created, consider **donating** and **sharing** the projects with others

- 💰 We are **not** against **Commercial** use, but we are against **abuse** of the projects and their code. Be fair, get in touch with us, we'll be happy to help both sides grow

## 🎩 Commercial Usage
Want to **use** our **Projects** for **Your Company** or **YouTube Channel**?

- Let's do something great together, contact me at [**@Tremeschin**](https://github.com/Tremeschin)

## 👁 Privacy Policy
- ✅ We **do not collect any data** from the user via Locally run Software, **period**<sup>*</sup>

- 🌐 Our software **may download third-party assets** from the internet, such as **FFmpeg** binaries, **PyTorch** models, **Fonts**, **Images**, **SoundFonts**. You agree with the Terms of the third-parties download Servers and Software, as they are required for the Projects to work

<sub><i>*1:</i> As a consequence, we don't have any analytics or metrics to improve the software, so we rely on user feedback and bug reports</sub>

</div>
