# Arch Linux Post-Install Setup

This guide documents the steps to configure an Arch Linux Omarchy Hyprland system with Zsh, development tools, editors, drivers, and desktop integrations.
It assumes you’ve already installed Arch with a bootloader (GRUB) and the Omarchy installer.

---
```bash
mkdir -p git
git clone git@github.com:Furyfree/dotfiles.git
```

## 1. Shell & Essentials
Install `zsh`, `nano`, `tmux`, and `kdeconnect` (for device integration):
```bash
sudo pacman -S zsh nano tmux kdeconnect
chsh -s $(which zsh)
```

## 2. Development Dependencies
Install core development libraries and headers required for building packages and Python:
```bash
sudo pacman -S --needed base-devel tk bzip2 zlib xz libffi sqlite gdbm openssl
```

## 3. Editors
**Zed Editor**
```bash
curl -f https://zed.dev/install.sh | sh
```
**Rustup (skip if using Omarchy)**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
```

## 4. AUR Helper (Paru)
Install paru from AUR:
```bash
git clone https://aur.archlinux.org/paru.git
cd paru
makepkg -si
cd .. && rm -rf paru
```

Update package databases and install apps:
```bash
paru -Syy
paru -S jetbrains-toolbox ghostty visual-studio-code-bin wootility zen-browser-bin 1password os-prober wlogout
```

## 5. Pacman Configuration
Enable multilib (for 32-bit packages):
```bash
[multilib]
Include = /etc/pacman.d/mirrorlist
```

## 6. AMD Drivers (HP EliteBook)
Install drivers and Vulkan support:
```bash
sudo pacman -S --needed mesa lib32-mesa vulkan-radeon lib32-vulkan-radeon vulkan-icd-loader lib32-vulkan-icd-loader libva-mesa-driver lib32-libva-mesa-driver vulkan-tools mesa-demos
```

## 7. GRUB Configuration
Set GRUB timeout to -1 (no timeout) and enable `os-prober`:
```bash
GRUB_TIMEOUT=-1
GRUB_DISABLE_OS_PROBER=false
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

## 8. Python (Pyenv)
Install Pyenv and multiple Python versions:
```bash
curl -fsSL https://pyenv.run | bash
pyenv install 3.11 && pyenv install 3.12 && pyenv install 3.13
pyenv global 3.13
```

## 9. Desktop Integrations
Copy custom `.desktop` launchers:
```bash
cp git/dotfiles/.local/share/applications/{Chess.desktop,DisneyPlus.desktop,HBOmax.desktop,Impala.desktop,Jetbrains-Toolbox.desktop,Messenger.desktop,Netflix.desktop,nvim.desktop,PrimeVideo.desktop,ProtonApps.desktop,ProtonMail.desktop,TV2Play.desktop,Twitch.desktop,Viaplay.desktop} ~/.local/share/applications
```

Copy icons:
```bash
cp git/dotfiles/.local/share/applications/icons/{Chess.png,Disneyplus.png,HBOmax.png,Jetbrains-Toolbox.png,Messenger.png,Netflix.png,PrimeVideo.png,ProtonApps.png,ProtonMail.png,TV2Play.png,Twitch.png,Viaplay.png,Wifi.png} ~/.local/share/applications/icons
```

## 10. After Dotfiles
Once your dotfiles are symlinked/applied, most configs should be ready to use.
