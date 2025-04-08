
✅ Download executables for all platforms:

!!! abstract ""
    === ":material-microsoft: Windows"
        <div align="center">
          <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg">
          <div>
            <b>Note:</b> Executables are <b><a target="_blank" href="https://github.com/ofek/pyapp">safe</a></b> and <b><a target="_blank" href="https://github.com/BrokenSource/BrokenSource/actions">auditable</a></b>, but might trigger false antivirus alerts
            <code>
              [<a target="_blank" href="https://github.com/ofek/pyapp/">1</a>]
              [<a target="_blank" href="https://news.ycombinator.com/item?id=19330062">2</a>]
              [<a target="_blank" href="https://www.reddit.com/r/csharp/comments/qh546a/do_we_really_need_to_buy_a_certificate_for_a/">3</a>]
              [<a target="_blank" href="https://github.com/pyinstaller/pyinstaller/issues/6754#issuecomment-1100821249">4</a>]
            </code>
            <div><small><b>I will not</b> destroy my reputation by distributing malware, and I don't have money for code signing</small></div>
          </div>
        </div>
        === ":octicons-cpu-16: x86-64 :octicons-cpu-16:"
            <table id="windows-amd64"><tbody class="slim-table"/></table>
    === ":simple-linux: Linux"
        <div align="center">
          <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg">
          <div><b>Note:</b> Open a terminal in the download path, extract it with `cat *.tar.gz | tar -xzvf - -i`</div>
          <div><sup>And then run `./project-name-*.bin` shown in the previous output for executing it!</sup></div>
        </div>
        === ":octicons-cpu-16: x86-64"
            <table id="linux-amd64"><tbody class="slim-table"/></table>
        === ":octicons-cpu-16: ARM64"
            <table id="linux-arm64"><tbody class="slim-table"/></table>
    === ":simple-apple: MacOS"
        <div align="center">
          <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg">
          <div><b>Note:</b> [Open a terminal](https://apple.stackexchange.com/a/438999) in the download path, extract it with `cat *.tar.gz | tar -xzvf - -i`</div>
          <div><sup>And then run `./project-name-*.bin` shown in the previous output for executing it!</sup></div>
        </div>
        === ":octicons-cpu-16: Apple Silicon"
            <table id="macos-arm64"><tbody class="slim-table"/></table>
        === ":octicons-cpu-16: Intel Macs"
            <table id="macos-amd64"><tbody class="slim-table"/></table>

<sup>:material-arrow-right: **Note**: You can [contact me](site:/about/contact) for a free copy of a paid executable if you have a valid or altruistic reason!</sup>

<script>
  const download_icon = `<span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M2.75 14A1.75 1.75 0 0 1 1 12.25v-2.5a.75.75 0 0 1 1.5 0v2.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 1.5 0v2.5A1.75 1.75 0 0 1 13.25 14Z"></path><path d="M7.25 7.689V2a.75.75 0 0 1 1.5 0v5.689l1.97-1.969a.749.749 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 6.78a.749.749 0 1 1 1.06-1.06z"></path></svg></span>`

  function add_release(emoji, project, platform, architecture, version, members, enabled) {

    // Create the project name left button
    const project_cell = Object.assign(document.createElement('td'), {style: 'width: 50%'});
    const project_link = Object.assign(document.createElement('a'), {
      className: 'md-button md-button--stretch md-button--thin',
      href: `https://brokensrc.dev/${project.toLowerCase()}`,
      innerHTML: `${emoji} ${project}`,
    });
    project_cell.appendChild(project_link)

    // Create the big clickable download button users love
    const download_cell = Object.assign(document.createElement('td'), {style: 'width: 50%'});
    const download_link = Object.assign(document.createElement('a'), {
      className: 'md-button md-button--primary md-button--stretch',
    })
    download_cell.appendChild(download_link)

    if (enabled && !members) {
      const extension = {windows: 'exe', linux: 'tar.gz', macos: 'tar.gz'}[platform];
      download_link.innerHTML = `${download_icon} Free ${version}`
      download_link.href = [
        `https://github.com/BrokenSource/${project}/releases/download/${version}/`,
        `${project.toLowerCase()}-${platform}-${architecture}-${version}.${extension}`
      ].join('')
    } else if (enabled && members) {
      download_link.innerHTML = `${download_icon} Cheap ${version}`
      download_link.href = "https://www.patreon.com/tremeschin/membership"
    } else {
      download_link.classList.add('md-button--disabled')
      download_link.innerHTML = 'Eventually'
    }

    // Create the hierarchy of elements of this row
    const row = document.createElement('tr')
    row.appendChild(project_cell)
    row.appendChild(download_cell)

    // Append to the table if it exists
    const table = document.querySelector(`#${platform}-${architecture} tbody`)
    if (table) {table.appendChild(row)}
  }

  add_release("🌊", "DepthFlow",   "windows", "amd64", "v0.9.0", 1, true)
  add_release("🌊", "DepthFlow",   "windows", "arm64", "v0.9.0", 0, false)
  add_release("🌊", "DepthFlow",   "linux",   "amd64", "v0.9.0", 0, true)
  add_release("🌊", "DepthFlow",   "linux",   "arm64", "v0.9.0", 0, true)
  add_release("🌊", "DepthFlow",   "macos",   "amd64", "v0.9.0", 0, true)
  add_release("🌊", "DepthFlow",   "macos",   "arm64", "v0.9.0", 0, true)
  add_release("🔥", "ShaderFlow",  "windows", "amd64", "v0.9.0", 0, true)
  add_release("🔥", "ShaderFlow",  "windows", "arm64", "v0.9.0", 0, false)
  add_release("🔥", "ShaderFlow",  "linux",   "amd64", "v0.9.0", 0, true)
  add_release("🔥", "ShaderFlow",  "linux",   "arm64", "v0.9.0", 0, true)
  add_release("🔥", "ShaderFlow",  "macos",   "amd64", "v0.9.0", 0, true)
  add_release("🔥", "ShaderFlow",  "macos",   "arm64", "v0.9.0", 0, true)
  add_release("🎹", "Pianola",     "windows", "amd64", "v0.9.0", 0, true)
  add_release("🎹", "Pianola",     "windows", "arm64", "v0.9.0", 0, false)
  add_release("🎹", "Pianola",     "linux",   "amd64", "v0.9.0", 0, true)
  add_release("🎹", "Pianola",     "linux",   "arm64", "v0.9.0", 0, true)
  add_release("🎹", "Pianola",     "macos",   "amd64", "v0.9.0", 0, true)
  add_release("🎹", "Pianola",     "macos",   "arm64", "v0.9.0", 0, true)
  add_release("🎧", "SpectroNote", "windows", "amd64", "v0.9.0", 0, true)
  add_release("🎧", "SpectroNote", "windows", "arm64", "v0.9.0", 0, false)
  add_release("🎧", "SpectroNote", "linux",   "amd64", "v0.9.0", 0, true)
  add_release("🎧", "SpectroNote", "linux",   "arm64", "v0.9.0", 0, true)
  add_release("🎧", "SpectroNote", "macos",   "amd64", "v0.9.0", 0, true)
  add_release("🎧", "SpectroNote", "macos",   "arm64", "v0.9.0", 0, true)
</script>

## ♻️ Uninstalling

--8<-- "include/uninstall/workspace.md"

<b>Note</b>: This should be the only directory used by Installers

