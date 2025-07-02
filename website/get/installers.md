
!!! danger "The v0.8 executables are old <small>(October 2024)</small>, prefer [wheels](site:get/wheels) until a [new release](https://github.com/BrokenSource/BrokenSource/issues/27) is made."
    Months of improvements and changes were made ever since, sorry for the inconvenience.

!!! abstract ""
    === ":material-microsoft: Windows"
        <div align="center">
          <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/windows.svg">
          <div>
            <b>Note:</b> Executables are <b><a href="https://pyaket.dev/faq/windows">safe</a></b> and <b><a href="https://github.com/BrokenSource/BrokenSource/actions">auditable</a></b>, but might trigger false antivirus alerts
            <div><small><b>I will not</b> destroy my reputation by distributing malware, code signing is infeasible.</small></div>
          </div>
        </div>
        === "x86-64"
            <table id="windows-amd64"><tbody class="slim-table"/></table>
    === ":simple-linux: Linux"
        <div align="center">
          <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linux.svg">
          <div><b>Note:</b> Open a terminal in the download path, extract it with `cat *.tar.gz | tar -xzvf - -i`</div>
          <div><sup>And then run `./project-name-*.bin` shown in the previous output for executing it!</sup></div>
        </div>
        === "x86-64"
            <table id="linux-amd64"><tbody class="slim-table"/></table>
        === "ARM64"
            <table id="linux-arm64"><tbody class="slim-table"/></table>
    === ":simple-apple: MacOS"
        <div align="center">
          <img class="os-logo" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/apple.svg">
          <div><b>Note:</b> [**Open a terminal**](https://apple.stackexchange.com/a/438999) in the download path, extract it with `cat *.tar.gz | tar -xzvf - -i`</div>
          <div><sup>And then run `./project-name-*.bin` shown in the previous output for executing it!</sup></div>
        </div>
        === "Apple Silicon"
            <table id="macos-arm64"><tbody class="slim-table"/></table>
        === "Intel Macs"
            <table id="macos-amd64"><tbody class="slim-table"/></table>

<sup>:material-arrow-right: ❤️ **Note**: You can [contact me](site:about/contact) for a free copy of a paid executable with a valid or altruistic reason!</sup>

<script>
  const download_icon = `<span class="twemoji"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M2.75 14A1.75 1.75 0 0 1 1 12.25v-2.5a.75.75 0 0 1 1.5 0v2.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 1.5 0v2.5A1.75 1.75 0 0 1 13.25 14Z"></path><path d="M7.25 7.689V2a.75.75 0 0 1 1.5 0v5.689l1.97-1.969a.749.749 0 1 1 1.06 1.06l-3.25 3.25a.75.75 0 0 1-1.06 0L4.22 6.78a.749.749 0 1 1 1.06-1.06z"></path></svg></span>`

  function add_release(emoji, project, platform, architecture, version, members, enabled) {
    const extension = {windows: 'exe', linux: 'tar.gz', macos: 'tar.gz'}[platform];
    const filename = `${project.toLowerCase()}-${platform}-${architecture}-${version}.${extension}`

    // Create the big clickable download button users love
    const download_cell = Object.assign(document.createElement('td'), {style: 'width: 50%'});
    const download_link = Object.assign(document.createElement('a'), {
      className: 'md-button md-button--primary md-button--stretch',
    })
    download_cell.appendChild(download_link)

    if (enabled && !members) {
      download_link.innerHTML = `${download_icon} Download Free ${version}`
      download_link.href = `https://github.com/BrokenSource/${project}/releases/download/${version}/${filename}`
    } else if (enabled && members) {
      download_link.innerHTML = `${download_icon} Download Cheap ${version}`
      download_link.href = "https://www.patreon.com/tremeschin/membership"
    } else {
      download_link.classList.add('md-button--disabled')
      download_link.innerHTML = 'Eventually'
    }

    // Create the hierarchy of elements of this row
    const row = document.createElement('tr')
    row.appendChild(download_cell)

    // Append to the table if it exists
    const table = document.querySelector(`#${platform}-${architecture} tbody`)
    if (table) {table.appendChild(row)}
  }
</script>

## ♻️ Uninstalling

--8<-- "include/uninstall/workspace.md"

<b>Note</b>: This should be the only directory used by Installers

