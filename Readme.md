👆【☰】Table of Contents

<div align="center">
  <img src="https://avatars.githubusercontent.com/u/110147748" style="vertical-align: middle; border-radius: 10%" width="140">

    :: Broken Source Software ::
</div>

This _mono_-repository hosts the **shared library** called **Broken** (Rust and Python), a convenience script of the same name,`broken`, and **submodules** of **all projects**.

- **Broken** is intended to be a _Framework_ for all other projects, a solution to manage them all in a single place.

**Rust** projects might take longer to be developed and shall be the focus on the medium future, while **Python** projects are prototypes, mockups, proof-of-concepts or smaller projects and are the current focus.



<br>
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


```ps
# Clone the bare monorepository
$ git clone https://github.com/BrokenSource/BrokenSource
```
```ps
# Enter the repository folder
$ cd BrokenSource
```
```ps
# Download poetry, setup virtualenv and enter poetry shell
# > "bash" is only required for the first run
$ bash ./brokenshell
```
```ps
# Clone public submodules of projects
$ broken clone
```

And done, you can now run `broken` and see all available commands: compile, release and run projects with ease!

<sub><b>Note:</b> On subsequent runs, open a terminal inside `BrokenSource` folder and run `./brokenshell` then you'll have `broken` available again</sub>

For projects that requires external packages to be installed, you _can_ run the following command:

```ps
# Attempts to install all needed dependencies for your platform
$ broken requirements
```

I can't exaustively test all platforms, feel free to pull request any missing package, dependency and fixes.

As a bonus, you can _"install"_ `broken` with:

```ps
# Symlinks Broken to /Broken and adds it to PATH
$ broken install
```

- After restarting the shell you can just type `brokenshell` anywhere to get access to `broken`

- External Python projects that depends on `broken` will be able to import it from anywhere, point the dependency to `/Broken`




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
<br>

# ● Contributing
Thanks for taking your time to contribute to Broken Source Software projects!!

- Apart from the usual "be nice", "be respectful" and "don't be a jerk", we have some guidelines to help you get started.

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
- All projects have their own license; unless specified in the code, asset file or `Readme.md`, all files are subject to the `License.md` on their respective repository.

- We embrace the **Open Source** philosophy; The **Free** part we hope that using more _"restrictive"_ licenses will help to keep the projects free from abuse.

- We are **not** against **Commercial** use, but we are against **abuse** of the projects and their code. Be fair, get in touch with us and we'll be happy to help both sides grow.

<sub>These are not legal advice, just our thoughts and intentions.</sub>
