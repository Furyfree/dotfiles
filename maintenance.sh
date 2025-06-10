#!/bin/bash

# Arch Linux system maintenance script med logfil, snapshots og Btrfs scrub

# Setup logfil med dato
LOG_DIR="$HOME/system-maintenance-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/maintenance-$(date +'%Y-%m-%d_%H-%M-%S').log"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "===== Arch System Maintenance Startet: $(date) ====="

echo "Tager Timeshift snapshot før evt. vedligeholdelse..."
sudo timeshift --create --comments "Pre-maintenance snapshot" --tags D

echo "Opdaterer systemet (pacman og AUR via paru)..."
if command -v paru >/dev/null 2>&1; then
  paru -Syu --noconfirm
else
  echo "paru ikke fundet — kun pacman opdateres"
  sudo pacman -Syu --noconfirm
fi

echo "Rydder op i forældreløse pakker..."
orphans=$(pacman -Qtdq)
if [[ -n "$orphans" ]]; then
  echo "$orphans" | sudo pacman -Rns - --noconfirm
else
  echo "Ingen orphans."
fi

echo "Rydder op i pakkecache (beholder seneste 3 versioner)..."
sudo paccache -r -k3

echo "Opdaterer Flatpak apps..."
flatpak update -y || echo "Flatpak opdatering fejlede."

echo "Tjekker diskforbrug..."
df -h

echo "Tjekker systemstatus (kritiske fejl)..."
sudo journalctl -p 3 -xb

echo "Tjekker SMART-status på diske..."
sudo smartctl --scan | awk '{print $1}' | while read disk; do
  echo "SMART-status for $disk:"
  sudo smartctl -H "$disk"
done

echo "Kører Btrfs scrub på mounted btrfs-enheder..."
for mount in $(findmnt -t btrfs -n -o TARGET -r); do
  echo "Scrubber $mount ..."
  sudo btrfs scrub start -Bd "$mount"
done

echo "===== Arch System Maintenance Færdig: $(date) ====="
echo "Log gemt i: $LOG_FILE"
