#!/bin/sh

# # Install Rustup if not found
if [ -z $(which rustup 2> /dev/null) ]; then
    curl -sSL https://sh.rustup.rs | sh -s -- -y
fi

if [ -z $(which python 2> /dev/null) ]; then
    echo "Please install Python first."
    exit
fi

# Fix to find rustup as PATH doesn't update
export PATH=$PATH:$USERPROFILE/.cargo/bin:$CARGO_HOME/bin
source $CARGO_HOME/env

# Download Rust stable
rustup default stable

# Clone bare Protostar Repo
git clone https://www.github.com/BrokenSource/Protostar
cd Protostar

# Make manager script executable
chmod +x ./nebula

# Init public submodules projects
projects=(
    "Ardmin"
    "Assets"
    # "Harper"
    # "HypeWord"
    # "PhasorFlow"
    # "ShaderFlow"
    "ViyLine"
)

# Init submodules
for project in "${projects[@]}"; do
    git submodule update --init $project
done

# Just in case we miss a repo?
git submodule update

printf "\n:: Now type (cd Protostar) and run projects with (cargo projectName)"
