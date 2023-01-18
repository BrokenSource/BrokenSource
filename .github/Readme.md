👆【☰】Table of Contents

<div align="center">
  <img src="https://github.com/BrokenSource/Assets/raw/Master/Logos/Protostar.png" onerror="this.src='../Assets/Logos/Protostar.svg'"/>
  <i>Readme available in:</i>

  <!-- Preferably order in number of speakers: EN, CN, IN, ES, FR, RU, PT, JP, DE -->

  <a href="Readme.md">   <img src="https://hatscripts.github.io/circle-flags/flags/us.svg" style="vertical-align: middle;" width="50"></a>
  <a href="Readme cn.md"><img src="https://hatscripts.github.io/circle-flags/flags/cn.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme in.md"><img src="https://hatscripts.github.io/circle-flags/flags/in.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme es.md"><img src="https://hatscripts.github.io/circle-flags/flags/es.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme fr.md"><img src="https://hatscripts.github.io/circle-flags/flags/fr.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme ru.md"><img src="https://hatscripts.github.io/circle-flags/flags/ru.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme pt.md"><img src="https://hatscripts.github.io/circle-flags/flags/br.svg" style="vertical-align: middle;" width="50"></a>
  <a href="Readme jp.md"><img src="https://hatscripts.github.io/circle-flags/flags/jp.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme de.md"><img src="https://hatscripts.github.io/circle-flags/flags/de.svg" style="vertical-align: middle;" width="30"></a>
</div>

<sub><i><b>Note:</b> This is a "Developer Mode" repository, if you intend to only run one of my projects go to their respective repository Releases or (hope) get from your package manager.</i></sub>

<sub><i><b>Note:</b> Not all projects are Open Source yet, and this will not be the best Rust code you ever read, I'm learning while coding the new stuff.</i></sub>



<br>

<!-- # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # -->
# ● Running From Source Code

<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle;" width="82">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle;" width="82">

  **Linux**, **MacOS**
</div>

<div align="center">

  ```ps
  curl -sSL https://github.com/BrokenSource/Protostar/raw/Master/Clone.sh | sh
  ```
</div>
<sub><i><b>Continue</b> reading...</i></sub>



<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;" width="82">

  Windows 10+
</div>
<p>

- Install [Git](https://git-scm.com/download/win).
- Right click a folder, open `Git Bash Here`.

<div align="center">

  ```ps
  curl -sSL https://github.com/BrokenSource/Protostar/raw/Master/Clone.sh | sh
  ```
</div>

**NOTE:** You'll probably need to configure yourself some C++ libraries like OpenBLAS, LAPACK and installing MinGW 64 bits.

<sub><i><b>Continue</b> reading...</i></sub>



<br>

## ▸ Compiling, Executing Projects
Run projects with the following command:

<div align="center">

  ```ps
  cargo (project) -- --help
  ```
</div>

*<b>Where</b> (project):*

- `ardmin`: Ardour Session Minimizer, blazing fast small CLI tool to simplify (in size) an Ardour Session Folder by deleting unused sources (WAV, MIDI), old plugin states and _somewhat_ non important files.

- `harper`: Secret

- `hypeword`: Secret

- `phasorflow`: Simplified equations for Newton-Raphson Power Flow and a new State of the Art Backwards Forwards Sweep-Like Asyncronous Sweep Power Flow that works for Meshed Grids implemented in Rust. **(Not OSS yet)**

- `shaderflow`: [Modular Music Visualizer](https://github.com/Tremeschin/ModularMusicVisualizer) rewrite. Early stages.

- `viyline`: Solar panel IV curve tracker, a DIY physical circuit project using PIC16F877A.

*<b>NOTE:</b> Most projects have a built-in CLI with help, but it's always good to check the original repository for specific instructions if any.*



<!-- # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # -->
<br>

# ● Contributing
Thanks for taking your time to contribute to Broken Source Software projects!!


## ▸ Help Needed
- Designer needed for the logos


## ▸ Reporting Issues
- **We do not** test enough or at all the code on Windows or MacOS, you may need to follow instructions on debugging.
- Always give **minimal steps** to reproduce the error (instructions or code).
- Most projects deal with Audio or Video, issues may be file-specific.
- **We only support the latest versions of any given project**, Protostar is rolling-release model.


## ▸ Suggesting Enhancements
- Rejection of ideas in Free and Open Source Software is a common and intimidating problem to newcomers, so we want to reduce the fear and cooperate with you.
- Not all suggestions matches the project original idea.
- No commentaries are criticizing your person, rather your *work*.
- **Stuff needs time and effort to be implemented**, don't expect stuff to be coded immediately.
- Feel absolutely free to debate on choices and ideas for the projects.




<!-- # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # -->
<br>

# ● Licenses / Licensing

## ▸ Code
- **Every project have their own license.** Always check the `Readme.md` and `License.md` on their respective repository.

## ▸ Logos
- All logos under CC BY-SA 4.0. All logos are made using Inkscape (FOSS) and are hosted on the [BrokenSource/Assets](https://github.com/BrokenSource/Assets) repository.
- The Fonts we use are:
  - **Under Open Font License**: "Alegreya Sans", "Dongle".
  - **GNU Unifont Glyphs**: [`GPLv2-or-later`, `SIL Open Font License`](http://unifoundry.com/unifont/index.html)
  - **DejaVu fonts**: See [here](https://dejavu-fonts.github.io/License.html).
