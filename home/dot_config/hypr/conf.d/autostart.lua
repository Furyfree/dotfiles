-- Start session processes once; config reloads do not restart them.
hl.on("hyprland.start", function()
    -- Ghostty reads this GTK preference when each terminal surface is created.
    hl.exec_cmd("gsettings set org.gnome.desktop.interface gtk-enable-primary-paste true")

    hl.exec_cmd("noctalia --daemon")

    -- Automount removable drives; Noctalia provides the drive UI and notifications.
    hl.exec_cmd("udiskie --no-tray --no-notify")

    -- The compatible fork supplies a headless user service; older builds are skipped.
    hl.exec_cmd([[command -v librepods >/dev/null 2>&1 || exit 0
    systemctl --user cat librepods.service >/dev/null 2>&1 || exit 0
    for adapter in /sys/class/bluetooth/hci*; do
        if [ -d "$adapter" ]; then exec systemctl --user start librepods.service; fi
    done]])
end)
