#!/usr/bin/env pwsh

# # Utility functions

# Workaround: Add expected path if we can't find winget
$wingetPath = $env:LocalAppData + "\Microsoft\WindowsApps"

function Reload-Path {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath    = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path    = $machinePath + ";" + $userPath + ";" + $wingetPath
}

function Print-Step {
    echo "`n:: $args`n"
}

# Have Winget installed
function Have-Winget {
    Reload-Path
    if ((Get-Command winget -ErrorAction SilentlyContinue)) {
        return
    }

    Print-Step "Installing Winget"

    # Try installing with Add-AppxPackage
    Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe
    Reload-Path

    # Attempt manual method if still not found
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        echo "Winget installation with Add-AppxPackage failed, trying 'manual' method.."
        Print-Step "Downloading Winget installer, might take a while."

        # Why tf does disabling progress bar yields 50x faster downloads????? https://stackoverflow.com/a/43477248
        $msi="https://github.com/microsoft/winget-cli/releases/download/v1.7.10582/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
        $tempFile = [System.IO.Path]::GetTempPath() + "\winget.msixbundle"
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $msi -OutFile $tempFile

        # Install the Appx package
        echo "Finished download, now installing it.."
        Add-AppxPackage -Path $tempFile
        Reload-Path
    }

    # If Winget is still not available, exit
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        echo "`n:: Winget Installation Error`n"
        echo "Winget was installed but still not found. Probably a Path issue or installation failure"
        echo "> Please get it at https://learn.microsoft.com/en-us/windows/package-manager/winget"
        echo "> Alternatively, install manually what previously failed"
        exit
    }
}

# # Install basic dependencies
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Print-Step "Git was not found, installing with Winget"
    Have-Winget
    winget install -e --id Git.Git
    Reload-Path
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        echo "`n:: Git Installation Error`n"
        echo "Git was installed but still not found. Probably a Path issue or installation failure"
        echo "> Please get it at https://git-scm.com/download/win"
        exit
    } else {
        echo "Git was installed successfully"
    }
}

if (-not (Get-Command rye -ErrorAction SilentlyContinue)) {
    Print-Step "Rye was not found, installing with Winget"
    Have-Winget
    winget install --id=Rye.Rye -e
    Reload-Path
    if (-not (Get-Command rye -ErrorAction SilentlyContinue)) {
        echo "`n:: Rye Installation Error`n"
        echo "Rye was installed but still not found. Probably a Path issue or installation failure"
        echo "> Please get it at https://rye-up.com"
        exit
    } else {
        echo "Rye was installed successfully"
    }
}

# Add %USERPROFILE%\.rye\shims to PATH permanently if not there
$ryePath = $env:USERPROFILE + "\.rye\shims"
if ($env:Path -notlike "*$ryePath*") {
    echo "Adding Rye Shims to PATH"
    [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";" + $ryePath, "User")
    Reload-Path
}

Reload-Path

# # Bootstrap BrokenSource Monorepo

Print-Step "Cloning BrokenSource Repository"
git clone https://github.com/BrokenSource/BrokenSource --recurse-submodules --jobs 4
cd BrokenSource

Print-Step "Checking out Master branch for all submodules"
git submodule foreach --recursive 'git checkout Master || true'

Print-Step "Creating Virtual Environment and Installing Dependencies"
rye self update
rye sync

Print-Step "Spawning a new Shell in the Virtual Environment"
powershell -NoLogo -NoExit -File .\.venv\Scripts\Activate.ps1
