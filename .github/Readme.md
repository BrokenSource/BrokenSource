👆【☰】Table of Contents

<div align="center">
  <img src="https://github.com/BrokenSource/Assets/raw/Master/Logos/Protostar.png" onerror="this.src='../Assets/Logos/Protostar.svg'"/>
  <i>Readme available in:</i>

  <!-- Preferably order in number of speakers: EN, CN, IN, ES, FR, RU, PT, JP, DE -->
  <!-- You must add "Translations are community Driven, BrokenSource official language is English and Portuguese, we don't take responsibility for innacuracies" -->

  <a href="Readme.md">   <img src="https://hatscripts.github.io/circle-flags/flags/us.svg" style="vertical-align: middle;" width="50"></a>
  <a href="Readme-cn.md"><img src="https://hatscripts.github.io/circle-flags/flags/cn.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme-in.md"><img src="https://hatscripts.github.io/circle-flags/flags/in.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme-es.md"><img src="https://hatscripts.github.io/circle-flags/flags/es.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme-fr.md"><img src="https://hatscripts.github.io/circle-flags/flags/fr.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme-ru.md"><img src="https://hatscripts.github.io/circle-flags/flags/ru.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme-pt.md"><img src="https://hatscripts.github.io/circle-flags/flags/br.svg" style="vertical-align: middle;" width="50"></a>
  <a href="Readme-jp.md"><img src="https://hatscripts.github.io/circle-flags/flags/jp.svg" style="vertical-align: middle;" width="30"></a>
  <a href="Readme-de.md"><img src="https://hatscripts.github.io/circle-flags/flags/de.svg" style="vertical-align: middle;" width="30"></a>
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
  curl -sSL https://github.com/BrokenSource/Protostar/raw/Master/nebula | python
  ```
</div>
<sub><i><b>Continue</b> reading...</i></sub>



<div align="center">
  <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle;" width="82">

  Windows 10+
</div>
<p>

- Shift+ Right Click a target directory on Windows Explorer, "Open PowerShell here", run:

<div align="center">

  ```ps
  winget install -e --id Python.Python.3.11
  ```
  ```ps
  (Invoke-WebRequest -Uri https://github.com/BrokenSource/Protostar/raw/Master/nebula -UseBasicParsing).Content | python -
  ```
</div>

- **NOTE:** You'll probably need to configure yourself some C/C++/FORTRAN libraries like OpenBLAS, LAPACK and installing MinGW 64 bits compiler for projects that depends on `ndarray-linalg`.

- **NOTE:** Broken Source projects are released with an without [UPX](https://upx.github.io/) (a safe executable file compressor), Windows Defender and/or antivirus most likely will trigger on those, if that is the case use the "fat" non-UPX executable.

<sub><i><b>Continue</b> reading...</i></sub>



<br>

## ▸ Compiling, Executing Projects
Simply run `./nebula` and see all available commands!



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



<br>

# ● License
- **Code:**  All projects have their own license. Check `License.md` on respective repository.

- **Assets:** See [Assets](https://github.com/BrokenSource/Assets) repository.
