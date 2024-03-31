#!/bin/bash

git=""
if [ -x "$(command -v git)" ]; then
  git=$(readlink -f $(which git))
  echo "• Found Git at ($git)"
else
  echo "• Git wasn't found, please get it at (https://git-scm.com)"
  exit 1
fi

rye=""
for attempt in $(seq 1 2); do
  if [ -x "$(command -v rye)" ]; then
    rye=$(readlink -f $(which rye))
    echo "• Found Rye at ($rye)"
    break
  fi

  if [ $attempt -eq 2 ]; then
    echo "Rye wasn't found after an installation attempt"
    echo "• Do you have the Shims directory on PATH?"
    echo "• Try restarting the Shell and retrying"
    echo "• Get it at (https://rye-up.com)"
    exit 1
  fi

  echo "• Rye wasn't found, will attempt to install it"
  export RYE_TOOLCHAIN_VERSION="cpython@3.11"
  export RYE_INSTALL_OPTION="--yes"
  /bin/bash -c "$(curl -sSf https://rye-up.com/get)"
done

# # Get Code, Install Dependencies and Spawn Shell

printf "\n:: Cloning BrokenSource Repository\n\n"
$git clone https://github.com/BrokenSource/BrokenSource --recurse-submodules --jobs 4
cd BrokenSource

printf "\n:: Checking out all submodules to Master\n"
$git submodule foreach --recursive 'git checkout Master || true'

printf "\n:: Creating Virtual Environment and Installing Dependencies\n"
$rye self update
$rye sync

printf "\n:: Spawning a new Shell in the Virtual Environment\n"
source .venv/bin/activate
exec $SHELL
