# PBY's Dotfiles

Personal dotfiles and automated setup script for Arch Linux with Omarchy.

## 🚀 Quick Start

```bash
mkdir -p git && cd git
git clone https://github.com/Furyfree/dotfiles.git
cd dotfiles
chmod +x install.sh
./install.sh
```

> **Note:** Script is idempotent and safe to run multiple times

## 📋 What This Does

- **Package Management**: Installs additional packages via Paru (AUR helper)
- **Development Tools**: Sets up Python/uv, Rust, and Java environments via mise
- **Applications**: Configures Helium Browser, Ghostty, Zed, JetBrains Toolbox, and more
- **Browser Setup**: Sets Helium as default with DRM support for streaming
- **Dotfiles**: Symlinks configurations for tmux, zsh, starship, yazi, bat, and others
- **Desktop Integration**: Adds custom .desktop entries and icons
- **Network**: Configures NetworkManager with iwd backend
- **Hardware**: Installs AMD GPU drivers (Mesa/Vulkan) when detected

## 📁 Project Structure

```
├── common/.config/     # Cross-platform configs (starship, tmux, ghostty, etc.)
├── linux/.config/      # Linux-specific configs (hypr, waybar, fastfetch)
├── linux/.zshrc        # Zsh configuration with custom aliases
├── .local/share/       # Desktop entries and Omarchy theme additions
├── .local/bin/         # Utility scripts and launchers
└── install.sh          # Main automated setup script
```

## 📋 Requirements

- **OS**: Arch Linux with Omarchy pre-installed
- **Network**: Active internet connection
- **Permissions**: Sudo privileges for package installation

## ⚙️ Manual Configuration

After running the installation script, complete these configuration steps:

### 🖥️ Hyprland Display Setup

**Monitor Configuration:**
Use `hyprctl monitors` to discover your display layout, then edit monitors.conf with your specific setup:
```bash
cp ~/.config/hypr/monitors.example.conf ~/.config/hypr/monitors.conf
```

**Workspace Configuration:**
Configure workspace assignments for multi-monitor setups (leave workspaces.conf empty for single monitor):
```bash
cp ~/.config/hypr/workspaces.example.conf ~/.config/hypr/workspaces.conf
```

After configuring both files, reload Hyprland to apply changes:
```bash
hyprctl reload
```

---

## 👤 Personal Preferences & Setup

The following sections contain personal preferences and configurations. Adapt to your needs:

### 🔐 Git SSH Setup (Personal)

For repository maintainer with SSH keys configured:
Switch from HTTPS to SSH for authenticated operations:
```bash
git remote set-url origin git@github.com:Furyfree/dotfiles.git
```

### 🌐 Browser Configuration

**Helium Browser Extensions:**
- **Bookmarkhub** - Centralized bookmark management
- **1Password** - Secure password manager integration
- **Dark Reader** - Universal dark mode (disable dark reader turning on by default)

### 🛠️ Development Environment

**JetBrains IDEs Setup:**
Hide individual IDE desktop entries (use Toolbox launcher instead):
```bash
~/./git/dotfiles/scripts/hide-toolbox-entries
```

**JetBrains Settings Synchronization:**
- Login to JetBrains account for settings sync
- Enable Settings Repository for cross-machine consistency

**Zed Editor Configuration:**
- **Theme**: Catppuccin Mocha (consistent with system theme)
- **Icons**: Catppuccin Mocha icon set
- **Extensions**: Install language support as needed

### 🔒 VPN Configuration

**Proton VPN:**
- Launch app and login with credentials
- Configure connection preferences

**Personal WireGuard VPN:**
1. Access your Unifi Console web interface
2. Navigate: Settings → VPN → VPN Server → Byrne VPN Wireguard
3. Add new client (name it before downloading)
4. Install configuration:
```bash
mv ~/Downloads/Byrne-VPN-Wireguard-* ~/Downloads/wg0.conf
nmcli connection import type wireguard file ~/Downloads/wg0.conf
nmcli connection modify wg0 connection.id "unifi-wg"
```

**Usage:**
```bash
nmcli connection up unifi-wg
nmcli connection down unifi-wg
```

**DTU VPN Setup:**
```bash
# Add DTU VPN connection
nmcli connection add type vpn vpn-type openconnect con-name dtu-vpn +vpn.data "gateway=vpn.dtu.dk,protocol=anyconnect"
```

Configure User Agent:
- Open NetworkManager tray applet
- Edit "dtu-vpn" connection settings
- Set User Agent field to: `AnyConnect`

**Usage:**
```bash
nmcli connection up dtu-vpn
nmcli connection down dtu-vpn
```

---

**Happy coding!** 🎉
