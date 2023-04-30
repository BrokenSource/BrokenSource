👆【☰】Table of Contents

<div align="center">
  <!-- <img src="https://github.com/BrokenSource/Assets/raw/Master/Logos/Protostar.png" onerror="this.src='../Assets/Logos/Protostar.svg'"/> -->
</div>

🔨 There is Some™ ongoing maintenance and renamings... 👨‍🔧 expect inconsistencies or.. _broken_ stuff 😅

<sub><i><b>Note:</b> This is a "Developer Mode" repository, not all projects are Open Source yet, and this will not be the best Rust code you ever read, I'm still learning</i></sub>


<br>

# ● Running From the Source Code

The `brakeit` script will automatically install dependencies and enter the developer environment, you can do that manually in the future with:
- `python -m poetry install`
- `python -m poetry shell`

<br>

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle;" width="82">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle;" width="82">

  **Linux**, **MacOS**
</div>

- Install `python` 3.10 and `git` for your platform (probably already installed)

<sub><i><b>Note:</b> For MacOS, use [Homebrew](https://brew.sh/).</i></sub>

- Open a Terminal on some directory you want to clone the repository and run:

<div align="center">

  ```ps
  python3 -m pip install git+https://github.com/brokensource/brakeit
  ```
  ```ps
  python3 -m brakeit
  ```
</div>

Now run `broken` and see all available commands!



<br>

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;" width="82">

  **Windows 10+**
</div>

Easiest way is using [MSYS2](https://www.msys2.org/) which provides an Unix-like environment for Windows

Compiling "natively" requires installing cmake, mingw gcc, mingw gfortran, visual studio c++ build tools, not really friendly

<sub><b>Tip:</b> you can press `Shift+Insert` to paste stuff on `Ctrl+C` to MSYS2 terminal</sub>

- Open a MSYS2 terminal
- Install dependencies: `pacman -S git python python-pip python-wheel mingw-w64-x86_64-gcc-fortran`
- Run the Linux and MacOS command above

**Note**: Stuff will be downloaded to `C:\msys64\home\USERNAME\BrokenSource` on default configs

Now run `broken` and see all available commands!

<sub><i>Linux and terminal commands aren't that hard!.. see? 😉</i></sub>


<br>

# ● License
- All projects have their own license, unless otherwise specified in the file or `Readme.md`, all files are subject to the `License.md` on their respective repository
