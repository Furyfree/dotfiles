# PBY's Dotfiles

Personal dotfiles and setup script for Arch Linux with Omarchy.

## Quick Start

```bash
mkdir -p git && cd git
git clone https://github.com/Furyfree/dotfiles.git
cd dotfiles
chmod +x install.sh
./install.sh
```

**Note:** Script is designed to be idempotent (safe to run multiple times)

## What This Does

- Installs additional packages via Paru (AUR helper)
- Sets up development tools (Python/uv, Rust, Java via mise)
- Configures preferred applications (Helium Browser, Ghostty, Zed, etc.)
- Sets Helium Browser as default with DRM support
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

## Manual Configuration Required

After running the script, you'll need to configure a few files for your specific setup:

### Hyprland Configuration
1. Copy and configure monitor setup:
   ```bash
   cp ~/.config/hypr/monitors.example.conf ~/.config/hypr/monitors.conf
   # Use 'hyprctl monitors' to see your current monitor layout
   # Edit monitors.conf for your specific display setup
   ```

2. Copy and configure workspace assignments:
   ```bash
   cp ~/.config/hypr/workspaces.example.conf ~/.config/hypr/workspaces.conf
   # Edit workspaces.conf for your preferred workspace layout
   # For single monitor setups, you can leave workspaces.conf empty
   ```

### Git Remote Setup (Personal)
If you're the repository owner and have SSH keys set up:
```bash
# Change remote from HTTPS to SSH for authenticated pushes
git remote set-url origin git@github.com:Furyfree/dotfiles.git
```

## Post-Installation

1. **Reboot required** after running install.sh
2. Configure the Hyprland files mentioned above
3. Adjust any other configs as needed


