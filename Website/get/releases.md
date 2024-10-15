---
title: Get/Releases
---

!!! success "{++The most convenient++} way to use the Projects • Double-click and run, everything's managed for you."
    **Recommended for**: Basic users, alpha testers.

## ⚡️ Installing

!!! abstract ""
    === ":material-microsoft: Windows"
        <div align="center">
          <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg" style="vertical-align: middle; border-radius: 20%;" width="80">
          <div>
            <b>Note:</b> Executables are <b><a target="_blank" href="https://github.com/ofek/pyapp">safe</a></b> and <b><a target="_blank" href="https://github.com/BrokenSource/BrokenSource/actions">auditable</a></b>, but might trigger a false antivirus alert
            <code>
              [<a target="_blank" href="https://github.com/astral-sh/rye/issues/468#issuecomment-1956285911">1</a>]
              [<a target="_blank" href="https://github.com/pyinstaller/pyinstaller/issues/6754">2</a>]
            </code>
            <div><sup>I am not destroying my reputation by distributing malware.</sup></div>
          </div>
        </div>
        === ":octicons-cpu-16: x86-64"
            <table id="windows-amd64"><tbody/></table>
    === ":simple-linux: Linux"
        <div align="center">
          <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg" style="vertical-align: middle; border-radius: 20%;" width="80">
          <div><b>Remember</b> to `chmod +x ./project-*.bin` to make it executable!</div>
          <div><sup></sup></div>
        </div>
        === ":octicons-cpu-16: x86-64"
            <table id="linux-amd64"><tbody/></table>
    === ":simple-apple: MacOS"
        <div align="center">
          <img src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg" style="vertical-align: middle; border-radius: 20%;" width="80">
          <div><b>Remember</b> to `chmod +x ./project-*.bin` to make it executable!</div>
          <div><sup></sup></div>
        </div>
        === ":octicons-cpu-16: Apple Silicon"
            <table id="macos-arm64"><tbody/></table>

<script>
  function add_release(emoji, name, platform, architecture, version, enabled) {

    // Create the project name left button
    const project_cell = Object.assign(document.createElement('td'), {style: 'width: 50%'});
    const name_link = Object.assign(document.createElement('a'), {
      className: 'md-button md-button--stretch md-button--thin',
      href: `https://brokensrc.dev/${name.toLowerCase()}`,
      innerHTML: `${emoji} ${name}`,
    });

    // Create the big clickable download button users love
    const download_cell = Object.assign(document.createElement('td'), {style: 'width: 50%'});
    const download_link = Object.assign(document.createElement('a'), {
      className: 'md-button md-button--primary md-button--stretch',
    });

    if (enabled) {
      const icon = `<span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M2.75 14A1.75 1.75 0 0 1 1 12.25v-2.5a.75.75 0 0 1 1.5 0v2.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 1.5 0v2.5A1.75 1.75 0 0 1 13.25 14Z"></path><path d="M7.25 7.689V2a.75.75 0 0 1 1.5 0v5.689l1.97-1.969a.749.749 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 6.78a.749.749 0 1 1 1.06-1.06z"></path></svg></span>`;
      const extension = {windows: 'exe', linux: 'bin', macos: 'bin'}[platform];
      download_link.innerHTML = `${icon} Download`;
      download_link.href = [
        `https://github.com/BrokenSource/${name}/releases/download/${version}/`,
        `${name.toLowerCase()}-${platform}-${architecture}-${version}.${extension}`
      ].join('');
    } else {
      download_link.classList.add('md-button--disabled');
      download_link.innerHTML = 'Eventually';
    }

    // Create the hierarchy of elements of this row
    const row = document.createElement('tr');
    download_cell.appendChild(download_link);
    project_cell.appendChild(name_link);
    row.appendChild(project_cell);
    row.appendChild(download_cell);

    document.querySelector(`#${platform}-${architecture} tbody`).appendChild(row);
  }

  add_release("🌊", "DepthFlow",   "windows", "amd64", "v0.8.0", true)
  add_release("🌊", "DepthFlow",   "linux",   "amd64", "v0.8.0", true)
  add_release("🌊", "DepthFlow",   "macos",   "arm64", "v0.8.0", true)
  add_release("🔥", "ShaderFlow",  "windows", "amd64", "v0.8.0", true)
  add_release("🔥", "ShaderFlow",  "linux",   "amd64", "v0.8.0", true)
  add_release("🔥", "ShaderFlow",  "macos",   "arm64", "v0.8.0", true)
  add_release("🎹", "Pianola",     "windows", "amd64", "v0.8.0", false)
  add_release("🎹", "Pianola",     "linux",   "amd64", "v0.8.0", false)
  add_release("🎹", "Pianola",     "macos",   "arm64", "v0.8.0", false)
  add_release("🎧", "SpectroNote", "windows", "amd64", "v0.8.0", false)
  add_release("🎧", "SpectroNote", "linux",   "amd64", "v0.8.0", false)
  add_release("🎧", "SpectroNote", "macos",   "arm64", "v0.8.0", false)

  // Redirect the user's platform download section on load
  document.addEventListener('DOMContentLoaded', function() {
    const userAgent = navigator.userAgent.toLowerCase()
    var option = ""

    if (userAgent.includes("win"))
      option = "#installing-windows"
    else if (userAgent.includes("mac"))
      option = "#installing-macos"
    else if (userAgent.includes("linux"))
      option = "#installing-linux"
    else
      option = "#installing-windows"

    const base = window.location.href.split("#")[0]
    window.location.href = base + option
  })
</script>

## ⭐️ Usage

Simply **double click** and run the executable on your platform. It will install or update everything and run the software. Go back to the project tab of your interest for more info!

## 🚀 Upgrading

Download a newer release from here, or your package manager[^1].

[^1]: You know what you are doing if using this. Reach me if you want to package for any package manager, we could make it official and write a proper page and guide for it!

## ♻️ Uninstalling

See the <a href="site:get/uninstalling"><b>uninstalling</b></a> page.
