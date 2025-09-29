#!/bin/bash

# Fail safety
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# HELPERS
# Simple log helper
log() { echo -e "\e[32m[*]\e[0m $1"; }

# Simple section helper
section() { echo -e "\n\e[1;34m==>\e[0m $1"; }

# Paru setup
install_paru() {
    if ! command -v paru &>/dev/null; then
        log "Updating system and cloning paru from AUR"
        sudo pacman -Syu --noconfirm --needed git base-devel
        git clone https://aur.archlinux.org/paru.git /tmp/paru

        cd /tmp/paru
        log "Building package..."
        makepkg -si --noconfirm

        log "Deleting paru directory"
        cd -
        rm -rf /tmp/paru
    else
        log "Paru already installed, skipping"
    fi
}


install_pkgs() {
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
        networkmanager-openconnect

    log "Installing Zed via Curl"
    if ! command -v zed &>/dev/null; then
        curl -f https://zed.dev/install.sh | sh
    else
        log "Zed already installed, skipping..."
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

    APPLICATION_DIR="$SCRIPT_DIR/.local/share/applications"
    ICONS_DIR="$APPLICATION_DIR/icons"

    log "Making Desktop Entries"
    mkdir -p "$HOME/.local/share/applications"
    for file in "$APPLICATION_DIR"/*.desktop; do
        if [ -f "$file" ]; then
            log "Copying $file to $HOME/.local/share/applications/$(basename "$file")"
            cp -- "$file" "$HOME/.local/share/applications/"
        fi
    done

    mkdir -p ~/.local/share/applications/icons
    for file in "$ICONS_DIR"/*.png; do
        if [ -f "$file" ]; then
            log "Copying $file to $HOME/.local/share/applications/icons/$(basename "$file")"
            cp -- "$file" "$HOME/.local/share/applications/icons/"
        fi
    done
}

install_amd_gpu_stack() {
    if lspci | grep -qi 'vga.*amd'; then
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

network_manager_setup() {
  log "Disabling iwd / systemd-networkd"
  sudo systemctl disable --now iwd.service systemd-networkd.service systemd-networkd-wait-online.service || true
  sudo systemctl mask iwd.service || true

  log "Enabling NetworkManager (and wpa_supplicant)"
  sudo systemctl enable --now NetworkManager.service
  sudo systemctl enable --now wpa_supplicant.service || true

  local FILE="/etc/NetworkManager/conf.d/NetworkManager.conf"
  sudo mkdir -p "$(dirname "$FILE")"

  log "Ensuring WiFi backend config in $FILE"
  if ! sudo grep -Fxq "plugins=keyfile" "$FILE" 2>/dev/null || \
     ! sudo grep -Fxq "wifi.backend=wpa_supplicant" "$FILE" 2>/dev/null; then
    sudo tee -a "$FILE" >/dev/null <<'EOF'
[main]
plugins=keyfile

[device]
wifi.backend=wpa_supplicant
EOF
    log "Appended config block to $FILE"
  else
    log "Config already present in $FILE"
  fi

  local FILE="/etc/NetworkManager/conf.d/wifi_backend.conf"
  sudo mkdir -p "$(dirname "$FILE")"

  log "Ensuring WiFi backend config in $FILE"
  if ! sudo grep -Fxq "wifi.backend=wpa_supplicant" "$FILE" 2>/dev/null; then
    sudo tee -a "$FILE" >/dev/null <<'EOF'
[device]
wifi.backend=wpa_supplicant
EOF
    log "Appended config block to $FILE"
  else
    log "Config already present in $FILE"
  fi


  log "Restarting NetworkManager"
  sudo systemctl restart NetworkManager.service

  # Sanity checks (more reliable than ps/grep)
  if systemctl is-active --quiet NetworkManager.service && \
     systemctl is-active --quiet wpa_supplicant.service; then
    log "NetworkManager and wpa_supplicant are active"
  else
    log "Warning: services not active as expected"
  fi

  nmcli networking on || true
  nmcli radio wifi on || true

  read -r -p "Reboot is needed - Want to reboot? [y/N] " ans; [[ $ans == [Yy]* ]] && sudo reboot
}

# Add personal background to Omarchy
add_personal_background() {
    log "Adding personal background to Catppuccin theme..."

    local DST_DIR="$HOME/.local/share/omarchy/themes/catppuccin/backgrounds"
    local SRC_DIR="$SCRIPT_DIR/.local/share/omarchy/themes/catppuccin/backgrounds"
    local SRC="$SRC_DIR/benjamin-voros-phIFdC6lA4E-unsplash.jpg"
    local DST="$DST_DIR/$(basename "$SRC")"

    mkdir -p "$DST_DIR"

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
        sudo ln -sfn /usr/lib/chromium/WidevineCdm /opt/helium-browser-bin/WidevineCdm
    else
        log "WidevineCdm or Helium dir missing; skipping DRM link"
    fi
}

trusted_1password_browsers() {
    sudo mkdir /etc/1password
    sudo touch /etc/1password/custom_allowed_browsers
    echo -e "zen-bin\nchrome" | sudo tee -a /etc/1password/custom_allowed_browsers
}

setup_linux_configs() {
    log "Setting up Linux specific dotfiles..."

    SRC_DIR="$SCRIPT_DIR/linux/.config"
    DST_DIR="$HOME/.config"

    mkdir -p "$DST_DIR"

    for folder in "$SRC_DIR"/*; do
        [ -e "$folder" ] || continue
        base=$(basename "$folder")
        ln -sfn "$SRC_DIR/$base" "$DST_DIR/$base"
    done
}

setup_common_configs() {
    log "Setting up common dotfiles..."

    SRC_DIR="$SCRIPT_DIR/common/.config"
    DST_DIR="$HOME/.config"

    mkdir -p "$DST_DIR"

    for folder in "$SRC_DIR"/*; do
        [ -e "$folder" ] || continue
        base=$(basename "$folder")
        ln -sfn "$SRC_DIR/$base" "$DST_DIR/$base"
    done

    bat cache --build
}

setting_up_zsh() {
    log "Setting up zsh..."
    file="$SCRIPT_DIR/linux/.zshrc"
    dst="$HOME/.zshrc"
    if [ -f "$file" ]; then
        log "Symlinking $file to $dst"
        ln -sf "$file" "$dst"
    fi
}


section "Starting PBY custom setup on top of Omarchy"

section "AMD GPU setup"
install_amd_gpu_stack

section "Paru setup"
install_paru

section "Package setup"
install_pkgs

section "Application setup"
setup_desktop_entries

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

section "Setting up NetworkManager"
network_manager_setup

section "Installation of PBY custom setup on top of Omarchy complete"
