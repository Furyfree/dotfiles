#!/bin/bash

# Fail safety
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# HELPERS
# Simple log helper
log() { echo -e "\e[32m[*]\e[0m $1"; }

# Simple section helper
section() { echo -e "\n\e[1;34m==>\e[0m $1"; }

check_connectivity() {
    if ! ping -c 1 8.8.8.8 &>/dev/null; then
        log "ERROR: No internet connectivity detected"
        exit 1
    fi
}

# Paru setup
install_paru() {
    if ! command -v paru &>/dev/null; then
        log "Updating system and cloning paru from AUR"
        sudo pacman -Syu --noconfirm --needed git base-devel
        rm -rf /tmp/paru
        git clone https://aur.archlinux.org/paru.git /tmp/paru

        cd /tmp/paru
        log "Building package..."
        makepkg -s --noconfirm
        log "Installing package..."
        sudo pacman -U --noconfirm *.pkg.tar.zst

        log "Deleting paru directory"
        cd -
        rm -rf /tmp/paru
    else
        log "Paru already installed, skipping"
    fi
}


install_pkgs() {
    log "Making sure paru cache doesn't stop Helium Browser installation"
    rm -rf ~/.cache/paru/clone/helium-browser-bin

    log "Removing 1password-beta to make room for 1password"
    if pacman -Q 1password-beta &>/dev/null; then
        log "Removing conflicting 1password-beta..."
        paru -Rns 1password-beta --noconfirm
    fi

    log "Installing packages with paru..."
    paru -S --needed --noconfirm \
        zsh \
        nano \
        tmux \
        seahorse \
        pacman-contrib \
        mono \
        kdeconnect \
        python-sphinx \
        python-sphinx_rtd_theme \
        python-breathe \
        python-graphviz \
        graphviz \
        jetbrains-toolbox \
        ghostty \
        visual-studio-code-bin \
        wootility 1password wlogout \
        helium-browser-bin \
        chromium-widevine \
        handlr \
        mimeo \
        standardnotes-bin \
        networkmanager \
        network-manager-applet \
        proton-vpn-gtk-app \
        openconnect \
        networkmanager-openconnect \
        bat \
        mise \
        lmstudio \
        dotnet-sdk

    log "Installing Zed via Curl"
    if ! command -v zed &>/dev/null; then
        if curl -f https://zed.dev/install.sh | sh; then
            log "Zed installed successfully"
        else
            log "WARNING: Failed to install Zed"
        fi
    else
        log "Zed already installed, skipping..."
    fi
}


# Development setup
install_python_tools() {
    log "Installing uv for Python management..."
    if ! command -v uv &>/dev/null; then
        curl -fsSL https://astral.sh/uv/install.sh | sh
    else
        log "uv already installed, skipping..."
    fi
}

install_rustup() {
    log "Installing Rustup..."
    if ! command -v rustc &>/dev/null; then
        bash -c "$(curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs)" -- -y
    else
        log "Rustup already installed, skipping..."
    fi
}

install_java() {
    log "Installing different Java versions via mise..."
    if ! command -v mise &>/dev/null; then
        log "mise not found; install_pkgs should have installed mise-bin. Aborting Java setup."
        return 1
    fi

    mise use -g java@latest
    mise use -g java@21
    mise use -g java@25
    mise use -g java@corretto-21
    mise use -g java@corretto-25
    log "Setting Corretto 25 as default global..."
    mise use -g java@corretto-25
}

# Application setup
setup_desktop_entries() {

    local APPLICATION_DIR="$SCRIPT_DIR/.local/share/applications"
    local ICONS_DIR="$APPLICATION_DIR/icons"

    log "Making Desktop Entries"
    mkdir -p -- "$HOME/.local/share/applications"

    for file in "$APPLICATION_DIR"/*.desktop; do
        if [ -f "$file" ]; then
            local basename_file="$(basename "$file")"
            log "Templating $file to $HOME/.local/share/applications/$basename_file"
            sed "s|/home/pby|$HOME|g" "$file" > "$HOME/.local/share/applications/$basename_file"
        fi
    done

    mkdir -p -- "$HOME/.local/share/applications/icons"
    for file in "$ICONS_DIR"/*.png; do
        if [ -f "$file" ]; then
            log "Copying $file to $HOME/.local/share/applications/icons/$(basename "$file")"
            cp -- "$file" "$HOME/.local/share/applications/icons/"
        fi
    done
}

has_amd_gpu() {
  lspci | grep -iE "VGA|3D|Display" | grep -qi "AMD"
}

install_amd_gpu_stack() {
  if has_amd_gpu; then
    log "AMD GPU detected — installing Mesa/Vulkan drivers"
    sudo pacman -S --needed --noconfirm \
      mesa lib32-mesa \
      vulkan-radeon lib32-vulkan-radeon \
      vulkan-icd-loader lib32-vulkan-icd-loader \
      libva-mesa-driver lib32-libva-mesa-driver \
      vulkan-tools mesa-demos
  else
    log "No AMD GPU detected — skipping Mesa/Vulkan install"
  fi
}



nm_iwd() {
    local backend
    backend=$(detect_backend)
    echo "Active backend: $backend"  # DEBUG

    if [[ "$backend" == "nm-iwd" ]]; then
        echo "NetworkManager with iwd is already active"
    else
        echo "Switching to NetworkManager with iwd..."

        echo "Installing dependencies..."
        sudo pacman -S --needed networkmanager iwd --noconfirm
        echo "Done installing."

        echo "Disabling wpa_supplicant + systemd-networkd"
        sudo systemctl disable --now wpa_supplicant.service systemd-networkd.service systemd-networkd-wait-online.service systemd-networkd.socket systemd-networkd-varlink.socket || true
        sudo systemctl mask wpa_supplicant.service || true

        echo "Unmasking + enabling iwd"
        sudo systemctl unmask iwd.service || true
        sudo systemctl enable --now iwd.service

        echo "Writing NetworkManager config"
        sudo install -d /etc/NetworkManager/conf.d
        sudo sh -c 'cat > /etc/NetworkManager/NetworkManager.conf' <<EOF
[main]
plugins=keyfile
dns=systemd-resolved
rc-manager=symlink
EOF
        sudo sh -c 'cat > /etc/NetworkManager/conf.d/wifi_backend.conf' <<EOF
[device]
wifi.backend=iwd
EOF

        echo "Enabling + restarting NetworkManager"
        sudo systemctl enable --now NetworkManager.service
        sudo systemctl restart NetworkManager.service
    fi

    rfkill unblock wifi || true
    nmcli networking on >/dev/null 2>&1 || true
    nmcli radio wifi on >/dev/null 2>&1 || true

    if systemctl is-active --quiet iwd; then
        echo "iwd: active"
    else
        echo "iwd: not active but should be active"
    fi

    if systemctl is-active --quiet systemd-networkd; then
        echo "systemd-networkd: active but should not be active"
    else
        echo "systemd-networkd: not active"
    fi

    if systemctl is-active --quiet wpa_supplicant; then
        echo "wpa_supplicant: active but should not be active"
    else
        echo "wpa_supplicant: not active"
    fi

    if systemctl is-active --quiet NetworkManager; then
        echo "NetworkManager: active"
    else
        echo "NetworkManager: not active but should be active"
    fi

    # Validation
    if systemctl is-active --quiet iwd &&
        systemctl is-active --quiet NetworkManager &&
        systemctl is-active --quiet systemd-resolved &&
        ! systemctl is-active --quiet wpa_supplicant &&
        ! systemctl is-active --quiet systemd-networkd; then
        echo "Netstack is now nm-iwd"
        echo "Verification: $(detect_backend)"
        resolvectl status | sed -n '1,8p' || true
    else
        echo "Netstack validation failed"
    fi
}

# Add personal background to Omarchy
add_personal_background() {
    log "Adding personal background to Catppuccin theme..."

    local DST_DIR="$HOME/.local/share/omarchy/themes/catppuccin/backgrounds"
    local SRC_DIR="$SCRIPT_DIR/.local/share/omarchy/themes/catppuccin/backgrounds"
    local SRC="$SRC_DIR/benjamin-voros-phIFdC6lA4E-unsplash.jpg"
    local DST="$DST_DIR/$(basename "$SRC")"

    mkdir -p -- "$DST_DIR"

    if [ -f "$DST" ]; then
        log "Background already exists at $DST, skipping copy"
    else
        cp -- "$SRC" "$DST"
        log "Copied $SRC to $DST"
    fi
}


setup_helium_default_browser() {
    log "Setting up Helium Browser as default..."
    xdg-settings set default-web-browser helium-browser.desktop

    log "Ensure all MIME types are set to Helium Browser"
    handlr set x-scheme-handler/http        helium-browser.desktop
    handlr set x-scheme-handler/https       helium-browser.desktop
    handlr set x-scheme-handler/chrome      helium-browser.desktop
    handlr set x-scheme-handler/about       helium-browser.desktop
    handlr set x-scheme-handler/unknown     helium-browser.desktop
    handlr set text/html                    helium-browser.desktop
    handlr set application/xhtml+xml        helium-browser.desktop
    handlr set application/x-extension-htm  helium-browser.desktop
    handlr set application/x-extension-html helium-browser.desktop
    handlr set application/x-extension-shtml helium-browser.desktop
    handlr set application/x-extension-xht   helium-browser.desktop
    handlr set application/x-extension-xhtml helium-browser.desktop

    command -v hyprctl &>/dev/null && hyprctl reload || true

    log "Adding DRM support for Helium Browser"
    if [ -d /usr/lib/chromium/WidevineCdm ] && [ -d /opt/helium-browser-bin ]; then
        sudo ln -sfn -- /usr/lib/chromium/WidevineCdm /opt/helium-browser-bin/WidevineCdm
    else
        log "WidevineCdm or Helium dir missing; skipping DRM link"
    fi
}

trusted_1password_browsers() {
    sudo mkdir -p /etc/1password
    sudo touch /etc/1password/custom_allowed_browsers
    printf "zen-bin\nchrome\nhelium-browser\n" | sudo tee /etc/1password/custom_allowed_browsers >/dev/null
}

setup_linux_configs() {
    log "Setting up Linux specific dotfiles..."

    local SRC_DIR="$SCRIPT_DIR/linux/.config"
    local DST_DIR="$HOME/.config"

    mkdir -p -- "$DST_DIR"

    for folder in "$SRC_DIR"/*; do
        [ -e "$folder" ] || continue
        local base=$(basename "$folder")
        ln -sfn -- "$SRC_DIR/$base" "$DST_DIR/$base"
    done
}

setup_common_configs() {
    log "Setting up common dotfiles..."

    local SRC_DIR="$SCRIPT_DIR/common/.config"
    local DST_DIR="$HOME/.config"

    mkdir -p -- "$DST_DIR"

    for folder in "$SRC_DIR"/*; do
        [ -e "$folder" ] || continue
        local base=$(basename "$folder")
        ln -sfn -- "$SRC_DIR/$base" "$DST_DIR/$base"
    done

    bat cache --build
}

setting_up_zsh() {
    log "Setting up zsh..."
    local file="$SCRIPT_DIR/linux/.zshrc"
    local dst="$HOME/.zshrc"
    if [ -f "$file" ]; then
        log "Symlinking $file to $dst"
        ln -sf -- "$file" "$dst"
    fi
}

setup_jetbrains_launch_scripts() {
    log "Setting up launch scripts for jetbrains IDEs"

    local LAUNCH_DIR="$SCRIPT_DIR/.local/bin"
    local DST_DIR="$HOME/.local/bin"

    mkdir -p -- "$DST_DIR"
    for file in "$LAUNCH_DIR"/*; do
        if [ -f "$file" ]; then
            local dst="$DST_DIR/$(basename "$file")"
            log "Copying $file to $dst"
            cp -- "$file" "$dst"
            chmod +x "$dst"
        fi
    done
}

hide_toolbox_entries() {
  local DIR="$HOME/.local/share/applications"
  shopt -s nullglob
  for file in "$DIR"/jetbrains-*-*.desktop; do
    # only hide if Exec references Toolbox installs
    grep -q "$HOME/.local/share/JetBrains/Toolbox/apps" "$file" || continue

    if grep -q '^[[:space:]]*NoDisplay=' "$file"; then
      sed -i 's/^[[:space:]]*NoDisplay=.*/NoDisplay=true/' "$file"
    else
      printf '\nNoDisplay=true\n' >> "$file"
    fi
  done
}

update_desktop_database() {
  if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" || true
  fi
}

detect_backend() {
    if systemctl is-active --quiet NetworkManager; then
        if systemctl is-active --quiet iwd; then
            if systemctl is-active --quiet systemd-networkd; then
                echo "systemd-iwd"
            else
                echo "nm-iwd"
            fi
        else
            echo "nm-wpa"
        fi
    elif systemctl is-active --quiet iwd && systemctl is-active --quiet systemd-networkd; then
        echo "systemd-iwd"
    else
        echo "none"
    fi
}


section "Starting PBY custom setup on top of Omarchy"

section "Checking Network Connectivity"
check_connectivity

section "AMD GPU setup"
install_amd_gpu_stack

section "Paru setup"
install_paru

section "Package setup"
install_pkgs

section "Application setup"
setup_desktop_entries

section "Jetbrains launch scripts setup"
setup_jetbrains_launch_scripts

section "Disabling old Jetbrains IDE desktop entries"
hide_toolbox_entries

section "Updating desktop database"
update_desktop_database

section "Setting up Development languages"
install_python_tools
install_rustup
install_java

section "Setting up personal background to be in Catppuccin theme"
add_personal_background

section "Dotfiles setup"
setup_linux_configs
setup_common_configs

section "Helium as default browser setup"
setup_helium_default_browser

section "zsh setup"
setting_up_zsh

section "1Password trusted browsers setup"
trusted_1password_browsers

section "Setting up NetworkManager + iwd"
nm_iwd

section "Installation of PBY custom setup on top of Omarchy complete"
