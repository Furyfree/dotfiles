#!/bin/bash

# Arch Linux system maintenance script with log file, snapshots and Btrfs scrub

# Setup log directory and file with timestamp
LOG_DIR="$HOME/system-maintenance-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/maintenance-$(date +'%Y-%m-%d_%H-%M-%S').log"

exec > >(tee -a "$LOG_FILE") 2>&1

# Temporarily disable pyenv and use system Python
echo "[INFO] Temporarily disabling pyenv and using system Python"
ORIG_PATH="$PATH"
unset PYENV_ROOT
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v '\.pyenv' | command paste -sd ':' -)
hash -r

echo "===== Arch System Maintenance Started: $(date) ====="

echo "Creating Timeshift snapshot before maintenance..."
sudo timeshift --create --comments "Pre-maintenance snapshot" --tags D

echo "Updating system packages (pacman and AUR via paru)..."
if command -v paru >/dev/null 2>&1; then
  paru -Syu --noconfirm
else
  echo "paru not found — only pacman will be used"
  sudo pacman -Syu --noconfirm
fi

echo "Removing orphaned packages..."
orphans=$(pacman -Qtdq)
if [[ -n "$orphans" ]]; then
  echo "$orphans" | sudo pacman -Rns - --noconfirm
else
  echo "No orphans found."
fi

echo "Cleaning up package cache (keeping latest 3 versions)..."
sudo paccache -r -k3

echo "Updating Flatpak apps..."
flatpak update -y || echo "Flatpak update failed."

echo "Checking disk usage..."
df -h

echo "Checking system logs for critical errors..."
sudo journalctl -p 3 -xb

echo "Checking SMART status of drives..."
sudo smartctl --scan | awk '{print $1}' | while read disk; do
  echo "SMART status for $disk:"
  sudo smartctl -H "$disk"
done

echo "Running Btrfs scrub on mounted btrfs filesystems..."
for mount in $(findmnt -t btrfs -n -o TARGET -r); do
  echo "Scrubbing $mount ..."
  sudo btrfs scrub start -Bd "$mount"
done

# Re-enable pyenv
echo "[INFO] Re-enabling pyenv"
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$ORIG_PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
hash -r

echo "===== Arch System Maintenance Finished: $(date) ====="
echo "Log saved to: $LOG_FILE"
