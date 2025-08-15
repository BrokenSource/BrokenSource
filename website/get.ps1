#!/usr/bin/env pwsh
# (c) MIT License, Tremeschin
# Script version: 2025.7.2

# This function reloads the "PATH" environment variable so that we can
# find newly installed applications without re-executing the script
function Reload-Path {
    $wingetPath  = $env:LocalAppData + "\Microsoft\WindowsApps"
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath    = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path    = $machinePath + ";" + $userPath + ";" + $wingetPath
}

# Common function to ask the user to continue or exit
function Ask-Continue {
    echo "`nPress Enter to continue normally, or Ctrl+C to exit"
    Read-Host
}

# Common function to separate steps in the output
function Print-Step {
    echo "`n:: $args`n"
}

# This function immediately exits if WinGet is installed - Microsoft's official package manager.
# - Most likely, you already have it on your system. As such, this function rarely runs fully
# - Otherwise, it tries to install it with the official Microsoft docs 'Add-AppxPackage' method
# - Still failing, it downloads the Appx package (.msibundle) to a temp file and install it
function Have-WinGet {
    Reload-Path

    # Early exit if WinGet is already installed
    if ((Get-Command winget -ErrorAction SilentlyContinue)) {
        return
    }

    Print-Step "Installing WinGet"

    # Attempt via: https://learn.microsoft.com/en-us/windows/package-manager/winget/
    Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe
    Reload-Path

    # Attempt manual method if still not found
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        echo "WinGet installation with Add-AppxPackage failed, trying 'manual' method.."
        Print-Step "Downloading WinGet installer, might take a while.."

        # Why tf does disabling progress bar yields 50x faster downloads????? https://stackoverflow.com/a/43477248
        $msi="https://github.com/microsoft/winget-cli/releases/latest/download/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"
        $tempFile = [System.IO.Path]::GetTempPath() + "\winget.msixbundle"
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $msi -OutFile $tempFile

        # Install the Appx package and clean temporary file
        echo "Finished download, now installing it, can take a while on HDDs systems.."
        Add-AppxPackage -Path $tempFile
        Remove-Item -Path $tempFile -Force
        Reload-Path
    }

    # If WinGet is still not available, exit
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Print-Step "Couldn't install or find 'winget' with current methods"
        echo "Either installation failure or pathing issues were encountered"
        echo "> Please get it at https://learn.microsoft.com/en-us/windows/package-manager/winget"
        echo "> Alternatively, install manually what was meant to be installed but failed"
        Ask-Continue
    }
}

# Ensure powershell is installed (some users might not have it, somehow?)
if (-not (Get-Command powershell -ErrorAction SilentlyContinue)) {
    Print-Step "PowerShell was not found, installing with WinGet"
    Have-WinGet
    winget install -e --id Microsoft.PowerShell
    Reload-Path
    if (-not (Get-Command powershell -ErrorAction SilentlyContinue)) {
        Print-Step "Couldn't install or find 'powershell.exe' executable"
    }
}

# Ensure git is installed - to download the repository's code
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Print-Step "Git was not found, installing with WinGet"
    Have-WinGet
    winget install -e --id Git.Git
    Reload-Path
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Print-Step "Couldn't install or find 'git' with current methods"
        echo "Either installation failure or pathing issues were encountered"
        echo "> Please get it at https://git-scm.com"
        Ask-Continue
    } else {
        echo "Git was installed successfully"
    }
} else {
    Print-Step "Updating git"
    winget upgrade --id Git.Git
}

# Ensure uv is installed - to manage python and its dependencies
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Print-Step "uv was not found, installing with WinGet"
    Have-WinGet
    winget install -e --id=astral-sh.uv
    Reload-Path
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Print-Step "Couldn't install or find 'uv' with current methods"
        echo "Either installation failure or pathing issues were encountered"
        echo "> Please get it at https://docs.astral.sh/uv/"
        Ask-Continue
    } else {
        echo "uv was installed successfully"
    }
} else {
    Print-Step "Updating uv"
    winget upgrade --id astral-sh.uv
}

# # Clone the Repositories, Install Python Dependencies on venv and Spawn a new Shell

# Skip cloning if already inside the repository
if (-not (Test-Path -Path "broken")) {
    Print-Step "Cloning BrokenSource Repository and all Submodules"
    git clone https://github.com/BrokenSource/BrokenSource --recurse-submodules --jobs 4
    cd BrokenSource

    Print-Step "Checking out main branch for all submodules"
    git submodule foreach --recursive 'git checkout main || true'
} else {
    Print-Step "Already in a Cloned Directory, Skipping Cloning"
}

# The PowerShell execution policy must allow for the Python activation script to run
if ((Get-ExecutionPolicy) -notin @("Unrestricted", "RemoteSigned", "Bypass")) {
    echo "`n(Warning) The current PowerShell ExecutionPolicy disallows activating the Python venv"
    echo "> More info: https://github.com/microsoft/vscode-python/issues/2559"
    echo "> Need any of: 'Unrestricted', 'RemoteSigned', or 'Bypass'"
    echo "> Current ExecutionPolicy: '$(Get-ExecutionPolicy)'"

    echo "`nDon't worry, we just need to run as admin the following:"
    echo "> 'Set-ExecutionPolicy RemoteSigned'`n"
    Read-Host "Press Enter to do it, or Ctrl+C to exit"

    Start-Process powershell -Verb RunAs -ArgumentList "-Command Set-ExecutionPolicy RemoteSigned"
}

Print-Step "Creating Virtual Environment and Installing Dependencies"
uv sync --all-packages

Print-Step "Spawning a new Shell in the Virtual Environment"
powershell -ExecutionPolicy Bypass -NoLogo -NoExit -File .\.venv\Scripts\Activate.ps1
