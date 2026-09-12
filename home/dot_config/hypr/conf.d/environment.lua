-- Session environment variables used by Hyprland and its applications.
local homeDir = os.getenv("HOME")

-- greetd skips shell profiles; retain the inherited PATH or supply a system fallback.
local searchPath = os.getenv("PATH")
if not searchPath or searchPath == "" then
    searchPath = "/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin"
end

-- GUI-launched apps need user commands and Mise tools without interactive shell activation.
local miseDataDir = os.getenv("MISE_DATA_DIR")
if not miseDataDir or miseDataDir == "" then
    local dataHome = os.getenv("XDG_DATA_HOME")
    miseDataDir = (
        dataHome and dataHome ~= "" and dataHome
        or homeDir .. "/.local/share"
    ) .. "/mise"
end
for _, directory in ipairs({ miseDataDir .. "/shims", homeDir .. "/.local/bin" }) do
    if
        not (":" .. searchPath .. ":"):find(":" .. directory .. ":", 1, true)
    then
        searchPath = directory .. ":" .. searchPath
    end
end
hl.env("PATH", searchPath)

-- Prefer native Wayland, with X11 available as a fallback.
hl.env("GDK_BACKEND", "wayland,x11,*")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")

-- Enable GTK compose and dead keys, including apps activated through D-Bus.
hl.env("GTK_IM_MODULE", "simple", true)

-- qt6ct also accepts qt5ct, allowing both Qt generations to load their plugin.
hl.env("QT_QPA_PLATFORMTHEME", "qt5ct")

-- Use Nimbus's Bibata theme with a consistent cursor size.
hl.env("XCURSOR_THEME", "Bibata-Modern-Ice")
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_THEME", "Bibata-Modern-Ice")
hl.env("HYPRCURSOR_SIZE", "24")

-- Give session-launched programs an editor while respecting inherited choices.
hl.env("EDITOR", os.getenv("EDITOR") or "nvim")
hl.env("VISUAL", os.getenv("VISUAL") or os.getenv("EDITOR") or "nvim")

-- Hyprland already supplies session identity; retain these only as reference.
-- hl.env("XDG_SESSION_TYPE", "wayland")
-- hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
-- hl.env("XDG_SESSION_DESKTOP", "Hyprland")

-- Older or app-specific Wayland overrides; modern Electron removed its hint variable.
-- hl.env("MOZ_ENABLE_WAYLAND", "1")
-- hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")
-- hl.env("OZONE_PLATFORM", "wayland")

-- Qt alternatives: use only when deliberately changing theming, scaling, or titlebars.
-- hl.env("QT_QPA_PLATFORMTHEME", "gtk3")
-- hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")
-- hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
-- hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")

-- Renderer/GPU workarounds: enable individually only for a reproduced hardware issue.
-- hl.env("GSK_RENDERER", "gl")
-- hl.env("AQ_NO_MODIFIERS", "1")
-- hl.env("LIBVA_DRIVER_NAME", "nvidia")
-- hl.env("NVD_BACKEND", "direct") -- Omarchy uses "egl" on some older NVIDIA hardware.
-- hl.env("__GLX_VENDOR_LIBRARY_NAME", "nvidia")
-- hl.env("__GL_GSYNC_ALLOWED", "0")
-- hl.env("__GL_VRR_ALLOWED", "0")

-- Custom compose sequences, only if this file has been created.
-- hl.env("XCOMPOSEFILE", homeDir .. "/.XCompose")

-- Reference-specific integration; these belong to Omarchy/Ryoku, not Noctalia.
-- hl.env("OMARCHY_PATH", homeDir .. "/.local/share/omarchy")
-- hl.env("QML_IMPORT_PATH", homeDir .. "/.local/lib/qt6/qml")
-- hl.env("QML2_IMPORT_PATH", homeDir .. "/.local/lib/qt6/qml")
-- hl.env("RYOKU_POLKIT_AGENT", "1")
