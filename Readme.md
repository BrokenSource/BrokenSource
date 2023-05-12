👆【☰】Table of Contents

<div align="center">
  <img src="https://avatars.githubusercontent.com/u/110147748" style="vertical-align: middle; border-radius: 10%" width="140">

    :: Broken Source Software ::
</div>

<sub><i><b>Note:</b> This is a "Developer Mode" repository, not all projects are Open Source yet, and this will not be the best Rust code you ever read, I'm still learning</i></sub>


<br>

# ● Running From the Source Code

Please read all instructions before executing them for tips and notes

<br>

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle;" width="82">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle;" width="82">

  **Linux**, **MacOS**
</div>

<sub><i><b>Note:</b> For MacOS, use [Homebrew](https://brew.sh/) package manager if needed</i></sub>

- Install the latest `python` and `git` for your platform<sup>(it's probably already installed)</sub>

- Open a Terminal on some directory you want to clone the repository and run:

<div align="center">

  ```ps
  # Installs "brakeit", our convenience script
  python3 -m pip install git+https://github.com/brokensource/brakeit
  ```
  ```ps
  # Clones the monorepo and public submodules
  python3 -m brakeit
  ```
</div>

Now run `broken` and see all available commands!

<sub><b>Note:</b> On subsequent runs, open the terminal inside `BrokenSource` folder and run `poetry shell` then you'll have `broken` available</sub>




<br>

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;" width="82">

  **Windows 10+**
</div>

Easiest way is using [MSYS2](https://www.msys2.org/) which provides an Unix-like environment for Windows, please install it

Compiling "natively" requires installing manually Python, Git, CMake, MinGW GCC and GFortran, Visual Studio C++ Build Tools, not really easy

- Open a MSYS2 terminal
- Install dependencies: `pacman -S git python python-pip python-wheel mingw-w64-x86_64-gcc-fortran`
- Run the Linux and MacOS command above

**Note**: Stuff will be downloaded to `C:\msys64\home\USERNAME\BrokenSource` on default configs

**Tip:** You can press `Shift+Insert` to paste stuff on `Ctrl+C` to MSYS2 terminal


Now run `broken` and see all available commands!

<sub><i>Linux and terminal commands aren't that hard!.. see? 😉</i></sub>


<br>

# ● License
- All projects have their own license, unless otherwise specified in the file or `Readme.md`, all files are subject to the `License.md` on their respective repository
