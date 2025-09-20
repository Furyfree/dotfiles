# Arch Linux Post-Install Setup

This guide documents the steps to configure an Arch Linux Omarchy Hyprland system with Zsh, development tools, editors, drivers, and desktop integrations.
It assumes you’ve already installed Arch with a bootloader (GRUB) and the Omarchy installer.

---
```bash
mkdir -p git
git clone git@github.com:Furyfree/dotfiles.git
```

## 1. Essentials
Install `zsh`, `nano`, `tmux`, `seahorse`, `pacman-contrib`, `mono` and `kdeconnect` (for device integration):
```bash
sudo pacman -S zsh nano tmux seahorse pacman-contrib mono kdeconnect
```

## 2. Shell
```bash
chsh -s $(which zsh)
```

## 3. Development Dependencies
Install core development libraries and headers required for building packages and Python:
```bash
sudo pacman -S --needed base-devel tk bzip2 zlib xz libffi sqlite gdbm openssl
```

## 4. Editors
**Zed Editor**
```bash
curl -f https://zed.dev/install.sh | sh
```
**Rustup (skip if using Omarchy)**
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup default stable
```

## 5. AUR Helper (Paru)
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
paru -S jetbrains-toolbox ghostty visual-studio-code-bin wootility zen-browser-bin 1password os-prober wlogout helium-browser-bin chromium-widevine
```

## 6. Add Helium and Zen Browser to 1Password trusted
```bash
sudo mkdir /etc/1password
sudo touch /etc/1password/custom_allowed_browsers
echo -e "zen-bin\nchrome" | sudo tee -a /etc/1password/custom_allowed_browsers
```

## 7. Pacman Configuration
Enable multilib (for 32-bit packages):
```bash
[multilib]
Include = /etc/pacman.d/mirrorlist
```

## 8. AMD Drivers (HP EliteBook)
Install drivers and Vulkan support:
```bash
sudo pacman -S --needed mesa lib32-mesa vulkan-radeon lib32-vulkan-radeon vulkan-icd-loader lib32-vulkan-icd-loader libva-mesa-driver lib32-libva-mesa-driver vulkan-tools mesa-demos
```

## 9. GRUB Configuration
Set GRUB timeout to -1 (no timeout) and enable `os-prober`:
```bash
GRUB_TIMEOUT=-1
GRUB_DISABLE_OS_PROBER=false
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

## 10. Python (Pyenv)
Install Pyenv and multiple Python versions:
```bash
curl -fsSL https://pyenv.run | bash
pyenv install 3.11 && pyenv install 3.12 && pyenv install 3.13
pyenv global 3.13
```

## 11. Desktop Integrations
Copy custom `.desktop` launchers:
```bash
cp ~/git/dotfiles/.local/share/applications/{Chess.desktop,DisneyPlus.desktop,HBOmax.desktop,Impala.desktop,Messenger.desktop,Netflix.desktop,nvim.desktop,PrimeVideo.desktop,ProtonApps.desktop,ProtonMail.desktop,TV2Play.desktop,Twitch.desktop,Viaplay.desktop,1password.desktop,jetbrains-toolbox.desktop} ~/.local/share/applications
```

Copy icons:
```bash
cp ~/git/dotfiles/.local/share/applications/icons/{Chess.png,Disneyplus.png,HBOmax.png,Messenger.png,Netflix.png,PrimeVideo.png,ProtonApps.png,ProtonMail.png,TV2Play.png,Twitch.png,Viaplay.png,Wifi.png} ~/.local/share/applications/icons
```
JetBrains Toolbox icon:
```bash
sudo cp ~/git/dotfiles/.local/share/applications/icons/toolbox.svg /opt/jetbrains-toolbox/
```

## 12. After Dotfiles
Once your dotfiles are symlinked/applied, most configs should be ready to use.

## 13. After all configs
```bash
bat cache --build
```

## 14. Enable Widevine DRM in Helium Browser
**Create symbolic link for Widevine DRM module:**
```bash
sudo ln -s /usr/lib/chromium/WidevineCdm /opt/helium-browser-bin/WidevineCdm
```

**Verify and configure Widevine:**

1. **Check Widevine component status:**
   - Open `chrome://components` in Helium
   - Verify "Widevine Content Decryption Module" is listed with a version number
   - **Note:** Status may show "Update error" - this is expected for non-Google builds
   - Updates will be handled through the `chromium-widevine` package

2. **Enable protected content:**
   - Navigate to: `chrome://settings/content/protectedContent`
   - Ensure "Allow sites to play protected content" is enabled

3. **Apply changes:**
   ```bash
   pkill chrome  # Completely close Helium
   # Then restart Helium from your application launcher
   ```

## 15. Make Helium standard browser
```bash
# symlink din custom webapp launcher
ln -s ~/git/dotfiles/.local/bin/omarchy-launch-webapp ~/.local/bin

# sæt Helium som systemets default browser
xdg-settings set default-web-browser helium-browser.desktop

# sørg for at alle http/https-links åbner i Helium
xdg-mime default helium-browser.desktop x-scheme-handler/http
xdg-mime default helium-browser.desktop x-scheme-handler/https

# reload Hyprland så ændringer træder i kraft
hyprctl reload
```
