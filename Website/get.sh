#!/bin/bash
# (c) MIT License, Tremeschin
# Script version: 2024.9.5

{ # Prevent execution if partially downloaded

# Exit on any error or failed command (includes pipes)
set -euo pipefail

# Detect current system
MACOS=false
[[ "$OSTYPE" == "darwin"* ]] && MACOS=true

# macOS: Must have 'Xcode Command Line Tools' installed
if $MACOS; then
  if ! xcode-select -p &> /dev/null; then
    printf "(Error) Xcode Command Line Tools are not installed\n"
    printf "• Install them with 'xcode-select --install'\n"
    printf "• Run again this script after installation\n"
    exit 0
  fi
fi

# Must have 'git' installed
git=""
if [ -x "$(command -v git)" ]; then
  git=$(readlink -f $(which git))
  printf "\n• Found Git at ($git)\n"
else
  printf "\n(Error) Git wasn't found, and is required to clone the repositories\n"
  printf "• Get it at (https://git-scm.com/), or from your distro:\n"
  printf "• macOS:  'brew install git' - needs (https://brew.sh/)\n"
  printf "• Ubuntu: 'sudo apt update && sudo apt install git'\n"
  printf "• Arch:   'sudo pacman -Syu git'\n"
  printf "• Fedora: 'sudo dnf install git'\n"
  exit 1
fi

# Must have 'rye' installed
rye=""
for attempt in $(seq 1 2); do
  if [ -x "$(command -v rye)" ]; then
    rye=$(readlink -f $(which rye))
    printf "\n• Found Rye at ($rye)\n"
    break
  fi

  if [ $attempt -eq 2 ]; then
    printf "\n(Error) Rye wasn't found after an installation attempt\n"
    printf "• Do you have the Shims directory on PATH?\n"
    printf "• Try restarting the Shell and retrying\n"
    printf "• Get it at (https://rye.astral.sh/)\n"
    exit 1
  fi

  printf "\n• Rye wasn't found, will attempt to install it\n\n"
  export RYE_TOOLCHAIN_VERSION="cpython@3.12"
  export RYE_INSTALL_OPTION="--yes"
  export RYE_VERSION="latest"
  /bin/bash -c "$(curl -sSf https://rye.astral.sh/get/)"
done

# # Clone the Repositories, Install Python Dependencies on venv and Spawn a new Shell

# Already inside a git repository
if git rev-parse --is-inside-work-tree &> /dev/null; then
  work_tree=$(git rev-parse --show-toplevel)

  # Must be on BrokenSource to continue
  if (cd "$work_tree" && git remote get-url origin 2>/dev/null | grep -q "BrokenSource"); then
    printf "\n• Already inside the BrokenSource main repository\n"
    printf "  - For latest changes, run 'Scripts/update.sh'\n"
    cd "$work_tree"
  else
    printf "\n(Error) Currently in a non-BrokenSource main git epository, exiting\n"
    exit 1
  fi

# Directory exists
elif [ -d "BrokenSource" ]; then
  printf "\n• BrokenSource directory exists. Assuming it's the repository\n"
  printf "  - On errors, try deleting the directory and run again\n"
  printf "  - For latest changes, run 'Scripts/update.sh'\n"
  cd BrokenSource

# Fresh clone
else
  printf "\n• Cloning BrokenSource Repository and all Submodules\n\n"
  $git clone https://github.com/BrokenSource/BrokenSource/ --recurse-submodules --jobs 4
  cd BrokenSource

  printf "\n• Checking out main branch for all submodules\n\n"
  $git submodule foreach --recursive 'git checkout main || true'
fi

# Make scripts executable for later use
chmod +x Website/get.sh
chmod +x ./Scripts/activate.sh

printf "\n• Creating Virtual Environment and Installing Dependencies\n\n"
$rye config --set-bool behavior.autosync=true
$rye config --set-bool behavior.use-uv=true
$rye config --set-bool global-python=false
$rye self update || printf "\n• Rye self update failed, ignoring..\n\n"
$rye sync

printf "\n• Spawning a new Shell in the Virtual Environment\n"
printf "  - Source the Virtual Environment to get here again\n"
printf "  - Tip: Alternative, run 'Scripts/activate.sh'\n\n"
source .venv/bin/activate
exec $SHELL

}