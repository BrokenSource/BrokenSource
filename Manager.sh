#!/usr/bin/bash
# This script should only be run under Linux or MINGW, MSYS, CYGWIN on Windows

# Change directory to root of the repo
cd "$(dirname "$0")"

# Get commit short hash
commit=$(git rev-parse --short HEAD | tr 'a-z' 'A-Z')

# # Get which Linux Distro we are running
distro=$(lsb_release -is)

case $distro in
    Arch)
        # yay -S base-devel mingw-w64-toolchain rustup --needed --noconfirm upx -y
        ;;

    *) echo "Distro [$distro] for Cross Compilation not supported";;
esac

# Rust
rustup default stable

for arg in "$@"; do
    case "$arg" in

        # ----------------------------------------------------------------------------| Build
        ;; build) echo ":: Executing Build routine"

            # Targets to build
            targets=(
                # The two apocalypse warriors
                "x86_64-unknown-linux-gnu"
                "x86_64-pc-windows-gnu"

                # # Hard
                # "x86_64-apple-darwin"
            )

            binaries=(
                "HypeWord"
                "PhasorFlow"
                "ShaderFlow"
                "ViyLine"
            )

            for target in "${targets[@]}"; do

                # Add toolchain
                rustup target add $target

                for binary in "${binaries[@]}"; do
                    profile="ultra"

                    # Build binary on ultra release mode
                    cargo build --bin $binary --target $target --profile $profile --all-features

                    # Get operating system suffix
                    case $target in
                        x86_64-unknown-linux-gnu)
                            finalSuffix=".bin"
                            compileSuffix=""
                            platform="Linux"
                            ;;

                        x86_64-pc-windows-gnu)
                            compileSuffix=".exe"
                            finalSuffix=".exe"
                            platform="Windows"
                            ;;
                    esac

                    compiled="./Releases/Build/$target/$profile/$binary$compileSuffix"
                    final="./Releases/$binary $platform ($commit)"
                    cp -v "$compiled" "$final$finalSuffix"

                    # UPX
                    # upx --best --lzma $compiled
                    # mv -v "$compiled" "$final-UPX$finalSuffix"
                done
            done
        ;;
    esac
done
