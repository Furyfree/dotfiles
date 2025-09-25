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
paru -S jetbrains-toolbox ghostty visual-studio-code-bin wootility zen-browser-bin 1password os-prober wlogout helium-browser-bin chromium-widevine handlr mimeo standardnotes-bin
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

## 10. Move to NetworkManager
```bash
sudo pacman -S networkmanager network-manager-applet
sudo systemctl disable --now iwd.service
sudo systemctl mask iwd
sudo systemctl enable --now wpa_supplicant
sudo systemctl enable --now NetworkManager.service

sudo systemctl disable --now iwd systemd-networkd systemd-networkd-wait-online
```
Edit this file:
```bash
sudo nano /etc/NetworkManager/conf.d/wifi_backend.conf
```
And add this to it:
```bash
[device]
wifi.backend=wpa_supplicant
```
Edit this file:
```bash
sudo nano /etc/NetworkManager/NetworkManager.conf
```
And add this to it:
```bash
[main]
plugins=keyfile

[device]
wifi.backend=wpa_supplicant
```
```bash
sudo systemctl restart NetworkManager
```

Verify (Should only show wpa):
```bash
ps -e | grep -E "iwd|wpa"
```

```bash
nmcli networking on
nmcli radio wifi on
```

Verify:
```bash
nmcli general status
nmcli device status
```

```bash
sudo reboot
```

Connect to wifi:
```bash
nmcli device
nmcli connection show
nmcli device wifi list
nmcli device wifi connect "SSID"
```

## 11. Download VPNs
1. Download Proton VPN
```bash
paru -S proton-vpn-gtk-app
```

2. Download DTU VPNs
```bash
sudo pacman -S openconnect networkmanager-openconnect
```
Add DTU VPN
```bash
nmcli connection add type vpn vpn-type openconnect con-name dtu-vpn +vpn.data "gateway=vpn.dtu.dk,protocol=anyconnect"
```
Go to tray and edit dtu-vpn and add to User Agent: `AnyConnect`

Now you can connect and disconnectvia:
```bash
nmcli connection up dtu-vpn
nmcli connection down dtu-vpn
```

3. Download Unifi VPN
Go to Unifi Website --> Settings --> VPN --> VPN Server --> Byrne VPN Wireguard --> Add Client --> Name first before Download:
```bash
mv ~/Downloads/Byrne-VPN-Wireguard-* ~/Downloads/wg0.conf
```

Create connection:
```bash
nmcli connection import type wireguard file ~/Downloads/wg0.conf
```
Rename:
```bash
nmcli connection modify wg0 connection.id "unifi-wg"
```
Connect and disconnect:
```bash
nmcli connection up unifi-wg
nmcli connection down unifi-wg
```

## 12. Python (Pyenv)
Install Pyenv and multiple Python versions:
```bash
curl -fsSL https://pyenv.run | bash
pyenv install 3.11 && pyenv install 3.12 && pyenv install 3.13
pyenv global 3.13
```

## 13. Desktop Integrations
Copy custom `.desktop` launchers:
```bash
cp ~/git/dotfiles/.local/share/applications/{Chess.desktop,DisneyPlus.desktop,HBOmax.desktop,Impala.desktop,Messenger.desktop,Netflix.desktop,nvim.desktop,PrimeVideo.desktop,ProtonApps.desktop,ProtonMail.desktop,TV2Play.desktop,Twitch.desktop,Viaplay.desktop,1password.desktop,jetbrains-toolbox.desktop,signal-desktop.desktop,GoogleMaps.desktop,LazyGit.desktop,Rider.desktop,PyCharm.desktop,IntelliJ.desktop} ~/.local/share/applications
```

Remove not needed desktop entries:
```bash
for f in ~/.local/share/applications/{Basecamp.desktop,dropbox.desktop,Figma.desktop,Google\ Contacts.desktop,Google\ Messages.desktop,Google\ Photos.desktop,HEY.desktop,Impala.desktop,WhatsApp.desktop}; do
  [ -e "$f" ] && mv "$f" "$f.bak"
done
```

Add personal background:
```bash
cp ~/git/dotfiles/.local/share/omarchy/themes/catppuccin/backgrounds/benjamin-voros-phIFdC6lA4E-unsplash.jpg .local/share/omarchy/themes/catppuccin/backgrounds
```

Copy icons:
```bash
cp ~/git/dotfiles/.local/share/applications/icons/{Chess.png,Disneyplus.png,HBOmax.png,Messenger.png,Netflix.png,PrimeVideo.png,ProtonApps.png,ProtonMail.png,TV2Play.png,Twitch.png,Viaplay.png,Wifi.png,GoogleMaps.png,LazyGit.png,toolbox.png,IntelliJ.png,PyCharm.png,Rider.png} ~/.local/share/applications/icons
```

Remove display of all jetbrains desktop apps:
```bash
for f in ~/.local/share/applications/jetbrains-*-*.desktop; do
  grep -q "^NoDisplay=true" "$f" || echo "NoDisplay=true" >> "$f"
done
```

## 14. After Dotfiles
Once your dotfiles are symlinked/applied, most configs should be ready to use.

## 15. Download pwvucontrol
Disable pyenv using function from .zshrc:
```bash
 toggle-pyenv
 ```

Install pwvucontrol:
```bash
paru -S pwvucontrol
```

Enable pyenv again:
```bash
 toggle-pyenv
 ```

## 15. After all configs
```bash
bat cache --build
```

## 16. Enable Widevine DRM in Helium Browser
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

## 17. Set default browser
Choose either Zen Browser or Helium Browser

**Symlink your custom webapp launcher**
```bash
ln -s ~/git/dotfiles/.local/bin/omarchy-launch-webapp ~/.local/bin
```

### Make Helium Default Browser

**Set Helium as the system's default browser**
```bash
xdg-settings set default-web-browser helium-browser.desktop
```

**Ensure all MIME types are set to Helium**
```bash
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
```

**Reload Hyprland so changes take effect**
```
hyprctl reload
```
### Make Zen Default Browser
**Set Zen as the system's default browser**
```bash
xdg-settings set default-web-browser zen.desktop
```

**Ensure all MIME types are set to Zen**
```bash
handlr set x-scheme-handler/http         zen.desktop
handlr set x-scheme-handler/https        zen.desktop
handlr set x-scheme-handler/chrome       zen.desktop
handlr set x-scheme-handler/about        zen.desktop
handlr set x-scheme-handler/unknown      zen.desktop

handlr set text/html                     zen.desktop
handlr set application/xhtml+xml         zen.desktop
handlr set application/x-extension-htm   zen.desktop
handlr set application/x-extension-html  zen.desktop
handlr set application/x-extension-shtml zen.desktop
handlr set application/x-extension-xht   zen.desktop
handlr set application/x-extension-xhtml zen.desktop
```

**Reload Hyprland so changes take effect**
```
hyprctl reload
```

## 18. Bookmark Synchronization with BookmarkHub

To share bookmarks between Helium (Chromium) and Zen (Gecko) across computers, use [BookmarkHub](https://github.com/dudor/BookmarkHub).
The backend is a **GitHub Gist**, and credentials are stored in **1Password**.

### Setup

1. **Install extension**
   - Download BookmarkHub from Chrome Web Store.
   - Install in both Helium and Zen.

2. **Configure BookmarkHub in browser**
   - Open extension settings.
   - **1Password Entry**: `GitHub Personal Access Token GIST Bookmark Hub`
   - **Github Token**: retrieve from 1Password (`bookmarkhub-gist.token`).
   - **Gist ID**: retrieve from 1Password (`bookmarkhub-gist.gist-id`).

4. **Initial sync**
   - Click **Delete all bookmarks** in BookmarkHub (to start clean).
   - Click **Download bookmarks** to fetch from the gist.
   - Going forward: when you add a bookmark in one browser, you can **Upload bookmarks** → then **Download bookmarks** in the other.

## 19. Setup btrfs-grub Snapshots

1. Download snapshot packages
```bash
sudo pacman -S grub-btrfs snapper snap-pac
```

2. Remove all timeshift backups if any - Abort if it asks to abort
```bash
sudo timeshift --delete-all
```

3. Remove timeshift
```bash
sudo pacman -Rns timeshift
```

4. Create snapper config for root:
```bash
sudo snapper -c root create-config /
```

5. Delete standard config
```bash
sudo rm -f /etc/snapper/configs/root
```

6. Symlink dotfiles config
```bash
sudo cp ~/git/dotfiles/etc/snapper/configs/root /etc/snapper/configs/root
```

7. Give correct permissions
```bash
sudo chown root:root /etc/snapper/configs/root
sudo chmod 640 /etc/snapper/configs/root
```

8. Enable quotas (required for proper space reporting and cleanup):
```bash
sudo btrfs quota enable /
```

9. Create initial snapshots
```bash
sudo snapper -c root create -d "initial"
```

10. Enable grub-btrfs
```bash
sudo systemctl enable --now grub-btrfsd.service
```

11. Rebuild GRUB
```bash
sudo grub-mkconfig -o /boot/grub/grub.cfg
```

12. Verify
```bash
sudo snapper -c root get-config
```
```bash
sudo snapper -c root list
```

### Rollback workflow
1. Reboot → select **"Arch Linux snapshots"** in GRUB and boot into the snapshot from before the update.
2. Once you’ve confirmed the system works, make the rollback permanent:
```bash
sudo snapper -c root rollback <snapshot-ID>
sudo reboot
```

### Cleanup
- After a rollback, the snapshot you restored from will still exist in `/.snapshots`
- You can delete it manually if you don’t need it anymore:
```bash
sudo snapper -c root delete <snapshot-ID>
```
- This step is optional: Snapper’s cleanup rules (`NUMBER_LIMIT`, `NUMBER_MIN_AGE`) will eventually remove older snapshots automatically.

# Not necessary
## 20. Steps if long shutdown time

### Reduce systemd shutdown timeout to 15s
1. Edit system.conf:
```bash
sudo nano /etc/systemd/system.conf
```
Uncomment or add the line:
```bash
DefaultTimeoutStopSec=15s
```
Save and exit.

2. Edit user.conf
```bash
sudo nano /etc/systemd/user.conf
```
Add or uncomment the same line:
```bash
DefaultTimeoutStopSec=15s
```

3. Reload systemd
For system services:
```bash
sudo systemctl daemon-reexec
```
For user services:
```bash
systemctl --user daemon-reexec
```

4. Verify

For system services:
```bash
systemctl show -p DefaultTimeoutStopUSec
```
Expected output:
```bash
DefaultTimeoutStopUSec=15s
```
For user services:
```bash
systemctl --user show -p DefaultTimeoutStopUSec
```
Expected output:
```bash
DefaultTimeoutStopUSec=15s
```

### Ultimate fix for long shutdown delays
Edit user service:
```bash
sudo systemctl edit user@.service
```

Add this to the config:
```bash
[Service]
TimeoutStopSec=15s
```
Reload daemon:
```
sudo systemctl daemon-reload
```

Go into tty and do these steps (`ctrl+alt+f3`)
```bash
sudo nano /etc/systemd/logind.conf
```
Uncomment or add this line:
```bash
KillUserProcesses=yes
```
Restart systemd-logind
```bash
sudo systemctl restart systemd-logind
```
And reboot
```bash
sudo reboot
```
