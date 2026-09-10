-- Start session processes once; config reloads do not restart them.
hl.on("hyprland.start", function()
    hl.exec_cmd("noctalia --daemon")

    -- Automount removable drives; Noctalia provides the drive UI and notifications.
    hl.exec_cmd("udiskie --no-tray --no-notify")

    -- Start LibrePods only when installed and a Bluetooth adapter is present at login.
    hl.exec_cmd([[command -v librepods >/dev/null 2>&1 || exit 0
    for adapter in /sys/class/bluetooth/hci*; do
        if [ -d "$adapter" ]; then exec librepods --hide; fi
    done]])
end)
