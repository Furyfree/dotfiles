# PBY's Dotfiles

Personal dotfiles and setup script for Arch Linux with Omarchy.

## Quick Start

```bash
git clone <this-repo> ~/.dotfiles
cd ~/.dotfiles
chmod +x install.sh
./install.sh
```

## What This Does

- Installs additional packages via Paru (AUR helper)
- Sets up development tools (Python/uv, Rust, Java via mise)
- Configures preferred applications (Helium Browser, Ghostty, Zed, etc.)
- Symlinks dotfiles for common tools (tmux, zsh, starship, yazi, bat)
- Adds custom .desktop entries and icons
- Sets up NetworkManager configuration

## Structure

```
common/.config/    # Cross-platform configs (starship, tmux, ghostty, etc.)
linux/.config/     # Linux-specific configs (hypr, waybar, fastfetch)
linux/.zshrc       # Zsh configuration
.local/share/      # Desktop entries and Omarchy theme additions
install.sh         # Main setup script
```

## Requirements

- Arch Linux with Omarchy already installed
- Internet connection
- Sudo privileges

## Notes

- Script is designed to be idempotent (safe to run multiple times)
- Reboot required after NetworkManager setup
- Sets Helium Browser as default with DRM support