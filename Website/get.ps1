#!/usr/bin/env pwsh
# (c) MIT License, Tremeschin
# Script version: 2024.10.5

# This function reloads the "PATH" environment variable so that we can
# find newly installed applications on the same script execution
function Reload-Path {
    $wingetPath  = $env:LocalAppData + "\Microsoft\WindowsApps"
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath    = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path    = $machinePath + ";" + $userPath + ";" + $wingetPath
}

# Option to continue normally even on errors
function Ask-Continue {
    echo "`nPress Enter to continue normally, or Ctrl+C to exit"
    Read-Host
}

# Consistency in showing steps
function Print-Step {
    echo "`n:: $args`n"
}

# This function immediately exits if Winget is found, else it tries to install it with
# the official Microsoft docs 'Add-AppxPackage' method. If it still fails, it tries
# to download the Appx package (.msibundle) and install it manually.
function Have-Winget {
    Reload-Path
    if ((Get-Command winget -ErrorAction SilentlyContinue)) {
        return
    }

    Print-Step "Installing Winget"

    # Attempt via: https://learn.microsoft.com/en-us/windows/package-manager/winget/
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
        Print-Step "Winget was not found, and installation failed with Add-AppxPackage"
        echo "Winget was installed but still not found. Probably a Path issue or installation failure"
        echo "> Please get it at https://learn.microsoft.com/en-us/windows/package-manager/winget"
        echo "> Alternatively, install manually what previously failed"
        Ask-Continue
    }
}

# Install Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Print-Step "Git was not found, installing with Winget"
    Have-Winget
    winget install -e --id Git.Git
    Reload-Path
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Print-Step "Git was not found, and installation failed with Winget"
        echo "Git was installed but still not found. Probably a Path issue or installation failure"
        echo "> Please get it at https://git-scm.com"
        Ask-Continue
    } else {
        echo "Git was installed successfully"
    }
}

# Install Rye
if (-not (Get-Command rye -ErrorAction SilentlyContinue)) {
    Print-Step "Rye was not found, installing with Winget"
    Have-Winget
    winget install --id=Rye.Rye -e
    Reload-Path
    if (-not (Get-Command rye -ErrorAction SilentlyContinue)) {
        Print-Step "Rye was not found, and installation failed with Winget"
        echo "Rye was installed but still not found. Probably a Path issue or installation failure"
        echo "> Please get it at https://rye.astral.sh"
        Ask-Continue
    } else {
        echo "Rye was installed successfully"
    }
}

# Add %USERPROFILE%\.rye\shims to PATH permanently if not there
# This is where the main 'rye' tool is located, make it available
$ryePath = $env:USERPROFILE + "\.rye\shims"
if ($env:Path -notlike "*$ryePath*") {
    Print-Step "Adding Rye Shims to PATH as it was not found"
    [System.Environment]::SetEnvironmentVariable("Path", $env:Path + ";" + $ryePath, "User")
    Reload-Path
}

Reload-Path

# # Clone the Repositories, Install Python Dependencies on venv and Spawn a new Shell

# Skip cloning if already on a cloned directory
if (-not (Test-Path -Path "Broken")) {
    Print-Step "Cloning BrokenSource Repository and all Submodules"
    git clone https://github.com/BrokenSource/BrokenSource --recurse-submodules --jobs 4
    cd BrokenSource

    Print-Step "Checking out main branch for all submodules"
    git submodule foreach --recursive 'git checkout main || true'
} else {
    Print-Step "Already in a Cloned Directory, Skipping Cloning"
}

Print-Step "Creating Virtual Environment and Installing Dependencies"
rye self update
rye config --set-bool behavior.autosync=true
rye config --set-bool behavior.use-uv=true
rye config --set-bool global-python=false
rye sync

Print-Step "Spawning a new Shell in the Virtual Environment"
powershell -NoLogo -NoExit -File .\.venv\Scripts\Activate.ps1
