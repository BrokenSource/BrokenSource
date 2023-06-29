👆【☰】Table of Contents

<div align="center">
  <img src="https://avatars.githubusercontent.com/u/110147748" style="vertical-align: middle; border-radius: 10%" width="140">

    :: Broken Source Software ::
</div>

This _mono_-repository hosts the **shared library** called **Broken** (Rust and Python), a convenience script of the same name - `broken` - and **submodules** of **all our projects**

- **Broken** is intended to be a _Framework_ for all other projects, a solution to manage them all in a single place

**Rust** projects might take longer to be developed and shall be the focus on the medium future, while **Python** projects are prototypes, mockups, proof-of-concepts or smaller projects and are the current focus



<br>
<br>

# ● Running From the Source Code

Please read all instructions before executing them for tips and notes

**Common stuff** for all platforms:

- The pre-requirements are having [Git](https://git-scm.com/downloads) and [Python](https://www.python.org/downloads) installed

- Commands don't include the `$` character, it indicates the start of it

<br>

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle;" width="82">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle;" width="82">

  **Linux**, **MacOS**
</div>

<sub><i><b>Note:</b> For MacOS, use [Homebrew](https://brew.sh/) package manager if needed</i></sub>

- Open a Terminal on some directory and run:

```ps
# Clone and enter the repository directory
$ git clone https://github.com/BrokenSource/BrokenSource

# "Open" the repository folder
$ cd BrokenSource

# Install dependencies, activates virtual environment
$ python3 ./brokenshell

# Clone submodules
$ broken clone
```

And done, you can now run `broken` and see all available commands: compile, release and run projects with ease!

<sub><b>Note:</b> On subsequent runs, open a terminal inside `BrokenSource` folder and execute `brokenshell` script again</sub>


<br>

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;" width="82">

  **Windows 10+**
</div>

- Running the Python projects is **easy**, while Rust requires **extra steps**

- **Rust** is split in its own instructions to reduce micro-management and complexity

Depending on the **project language** you want to run, follow the **instructions below**:

<details>
  <summary>
    Python Projects
  </summary>
  <br>

  Have [Git](https://git-scm.com/downloads) and [Python](https://www.python.org/downloads) installed

  <sub><b>Note:</b> Be sure to mark the option to add Python to PATH</sub>

  - **Windows 10**: `Shift+Right Click` some empty space in Windows Explorer, select `Open PowerShell window here`:

  - **Windows 11**: `Right Click` some empty space in Windows Explorer, select `Open in Terminal`:

  Now run the same **Linux** and **MacOS** commands above
</details>

<details>
  <summary>
    Rust Projects
  </summary>
  <br>

  **Rust** requires quite some **dependencies** to be **installed** for a Windows release

  Compiling "natively" requires installing manually Python, Git, CMake, MinGW GCC and GFortran, Visual Studio C++ Build Tools, not really easy but **doable if you want to try**

  Easiest way is using [MSYS2](https://www.msys2.org/) which provides an **Unix-like** environment for Windows, please install it

  - Open a MSYS2 terminal and install dependencies:

  ```ps
  $ pacman -S git python python-pip python-wheel mingw-w64-x86_64-toolchain libffi-devel zlib-devel
  ```

  - Now follow the same **Linux** and **MacOS** instructions above

  **Note**: Stuff will be downloaded to `C:\msys64\home\USERNAME\BrokenSource` on default configs

  **Tip:** You can press `Shift+Insert` to paste stuff on the clipboard to MSYS2 terminal

  <sub><i>Linux and terminal commands aren't that hard!.. see? 😉</i></sub>
</details>



<br>
<br>

# ● Contributing
Thanks for taking your time to contribute to Broken Source Software projects!!

- Apart from the usual "be nice", "be respectful" and "don't be a jerk", we have some guidelines to help you get started

## ▸ Help Needed
- Designer needed for the logos and consistent art
- Packaging binaries on Linux and MacOS package managers

## ▸ Reporting Issues
- **We do not** test enough or at all the code on Windows or MacOS
- Always give **minimal steps** to reproduce the error (instructions or code)
- Most projects deal with Audio or Video, issues may be file-specific
- **We only support the latest versions of any given project**, we are rolling-release
  - <sub>We'll still help troubleshooting older code or releases, just don't except back-porting</sub>

## ▸ Suggesting Enhancements
- Rejection of ideas on Free and Open Source Software is a common and intimidating problem to newcomers, so we want to reduce the fear and cooperate with you
- Not all suggestions matches the project original idea
- No commentaries are criticizing your person, rather your *work*
- **Stuff needs time and effort to be implemented**
- Feel absolutely free to debate on choices and ideas for the projects



<br>
<br>

# ● License and Fair Use
- All projects have their own license; unless specified in the code, asset file or `Readme.md`, all files are subject to the `License.md` on their respective repository

- We embrace the **Open Source** philosophy; The **Free** part we hope that using more _"restrictive"_ licenses will help to keep the projects free from abuse

- We are **not** against **Commercial** use, but we are against **abuse** of the projects and their code. Be fair, get in touch with us and we'll be happy to help both sides grow

<sub>These are not legal advice, just our thoughts and intentions</sub>
