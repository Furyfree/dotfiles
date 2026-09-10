-- Reference only: this entire file is a comment and is not loaded or deployed.
-- Curated from ~/compare/ryoku-arch at e76a32d474a467d45e0dc67a46d1c6057d024f5b.
-- https://github.com/Ryoku-dev/ryoku-arch/tree/e76a32d474a467d45e0dc67a46d1c6057d024f5b/ryoku/hyprland
-- Adapted excerpts from Ryoku Arch and its contributors: shortened sections,
-- helper key remapping removed, and independent options kept separate.
-- SPDX-License-Identifier: GPL-3.0-only
-- No warranty; preserve the upstream license when reusing these excerpts.

--[=[
-- INPUT: modules/input.lua
-- Pointer location is decoupled from keyboard focus. Compare Omarchy's
-- follow_mouse=1; test new-window focus and click behavior before choosing.
hl.config({ input = {
    follow_mouse = 2,
    sensitivity = 0,
    touchpad = { natural_scroll = false },
} })

-- FOCUS AND RESIZING: modules/misc.lua
-- Activation requests can focus windows, including ones on another monitor.
-- This is a preference with focus-stealing implications, not always desirable.
hl.config({ misc = {
    focus_on_activate = true,
    disable_hyprland_logo = true,
    animate_manual_resizes = true,
} })
-- Both Ryoku and Omarchy set allow_session_lock_restore=true to let a new
-- locker recover after failure. Retain this as a recovery idea pending testing
-- with our Noctalia locker, not as an automatic security-policy change.
-- Ryoku also uses xwayland.force_zero_scaling=true and use_nearest_neighbor=true.
-- Crisp pixels can come with incorrectly sized X11 apps: test fractional DPI.

-- DECORATION: modules/decoration.lua
-- A more spacious alternative to Omarchy. Ryoku reads generated colors and
-- performance flags; those runtime readers are deliberately not included.
hl.config({
    general = {
        gaps_in = 12, gaps_out = 18, border_size = 2,
        layout = "dwindle", resize_on_border = true,
    },
    decoration = {
        rounding = 0, rounding_power = 4,
        active_opacity = 1, inactive_opacity = 0.94,
        shadow = { enabled = true, range = 45, render_power = 4, color = 0xd10a0807 },
        blur = {
            enabled = true, size = 4, passes = 1,
            vibrancy = 0.17, noise = 0.01, new_optimizations = true,
        },
    },
})
-- Alternative for battery/weak GPUs: modules/perf_saver.lua.
-- The upstream shell decides when this applies; no flag files or polling here.
hl.config({ decoration = { blur = { enabled = false }, shadow = { enabled = false } } })

-- SHELL SURFACES: modules/decoration.lua
-- Let shell animations own the motion. Limit blur to visible pixels so a
-- transparent shadow margin does not become a frosted rectangle.
-- These are Ryoku namespaces, not Noctalia namespaces; remap after inspection.
hl.layer_rule({ name = "launcher-noanim", match = { namespace = "^launcher" }, no_anim = true })
hl.layer_rule({ name = "launcher-blur", match = { namespace = "^launcher$" },
    blur = true, ignore_alpha = 0.05,
})
hl.layer_rule({ name = "notifications-noanim", match = { namespace = "^ryoku-notifications$" },
    no_anim = true,
})
-- Ryoku also gives wallpaper layers a fade rather than the global layer pop-in.
-- Keep the transition idea; use the actual Noctalia layer names if needed.

-- MOTION: modules/animations/ryoku.lua
-- A slight overshoot on opening, then a calmer settling curve.
hl.config({ animations = { enabled = true } })
hl.curve("easeOutQuint", { type = "bezier", points = { { 0.23, 1 }, { 0.32, 1 } } })
hl.curve("quick", { type = "bezier", points = { { 0.15, 0 }, { 0.1, 1 } } })
hl.curve("almostLinear", { type = "bezier", points = { { 0.5, 0.5 }, { 0.75, 1 } } })
hl.curve("ryokuBloom", { type = "bezier", points = { { 0.16, 1.12 }, { 0.24, 1 } } })
hl.curve("ryokuSettle", { type = "bezier", points = { { 0.18, 0.86 }, { 0.24, 1 } } })
hl.animation({ leaf = "global", enabled = true, speed = 3.2, bezier = "ryokuSettle" })
hl.animation({ leaf = "windows", enabled = true, speed = 3.2, bezier = "ryokuSettle" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 3.8, bezier = "ryokuBloom", style = "popin 78%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 2.4, bezier = "ryokuSettle", style = "popin 86%" })
hl.animation({ leaf = "border", enabled = true, speed = 3.5, bezier = "quick" })
hl.animation({ leaf = "fade", enabled = true, speed = 3, bezier = "almostLinear" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 3.2, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 2.2, bezier = "almostLinear" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 3.5, bezier = "easeOutQuint", style = "slide" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 6, bezier = "easeOutQuint", style = "slidefadevert 20%" })
-- Reduced-motion alternative: modules/animations/{minimal,disable}.lua.
-- The preset loader and its GUI-written selection file are not required to
-- adopt one preset. Avoid global layer animation on self-animating Noctalia UI.

-- FLOATING DIALOGS THAT FIT: modules/window_rules.lua
-- Size relative to the target monitor, keeping space around the window.
local function fit(w, h)
    return {
        "min(" .. w .. ", monitor_w * 0.92)",
        "min(" .. h .. ", monitor_h * 0.88)",
    }
end
hl.window_rule({
    name = "float-system-dialogs",
    match = { class = "(pavucontrol|nm-connection-editor|blueman-manager|org.kde.polkit-kde-authentication-agent-1|xdg-desktop-portal-gtk)" },
    float = true,
})
hl.window_rule({ name = "float-polkit-agent", match = { class = "hyprpolkitagent" }, float = true, center = true })
hl.window_rule({ name = "float-file-pickers",
    match = { title = "(Open File|Save File|Save As|Choose Files|Open Folder)" }, float = true,
})
-- Title-only file-picker rules are broad and language-dependent; class-scoped
-- rules are preferable when the installed application exposes a stable class.
hl.window_rule({ name = "float-qemu", match = { class = "[Qq]emu" },
    float = true, size = fit(1280, 800), center = true,
})
hl.window_rule({ name = "float-looking-glass", match = { class = "looking-glass-client" },
    float = true, size = fit(1600, 900), center = true,
})
-- Ryoku floats Nautilus at fit(1500,850). Retain the fit() technique without
-- assuming every file-manager window should float in our workflow.

-- GAME PRESENTATION: modules/window_rules.lua
-- Keep games opaque and free from desktop blur/shadow. Fullscreen-only idle
-- inhibition supports controller play without suppressing idle on the desktop.
hl.window_rule({ name = "steam-native",
    match = { class = "^(steam|steam_app_.*|gamescope)$" },
    no_blur = true, no_shadow = true, opaque = true, idle_inhibit = "fullscreen",
})
-- Upstream also pairs immediate=true with general.allow_tearing=true.
-- That trades tearing for latency and needs display/GPU testing; it is not
-- included in this visual-only excerpt as a default.

-- XWAYLAND DRAG WORKAROUND: modules/window_rules.lua
hl.window_rule({ name = "fix-xwayland-drags", match = {
    class = "^$", title = "^$", xwayland = true,
    float = true, fullscreen = false, pin = false,
}, no_focus = true })

-- RESIZE MODE: modules/resize.lua and modules/binds.lua
-- A bounded submap with obvious exits, plus repeatable directional resizing.
-- SUPER+R currently opens our launcher; choose a chord before adopting this.
local step = 40
hl.bind("SUPER + R", hl.dsp.submap("resize"), { description = "Enter resize mode" })
hl.define_submap("resize", function()
    hl.bind("Left", hl.dsp.window.resize({ x = -step, y = 0, relative = true }), { repeating = true })
    hl.bind("Right", hl.dsp.window.resize({ x = step, y = 0, relative = true }), { repeating = true })
    hl.bind("Up", hl.dsp.window.resize({ x = 0, y = -step, relative = true }), { repeating = true })
    hl.bind("Down", hl.dsp.window.resize({ x = 0, y = step, relative = true }), { repeating = true })
    hl.bind("Escape", hl.dsp.submap("reset"))
    hl.bind("Return", hl.dsp.submap("reset"))
    hl.bind("SUPER + R", hl.dsp.submap("reset"))
end)
-- Upstream adds h/j/k/l aliases and SUPER+CTRL+arrows outside the submap.
hl.bind("SUPER + CTRL + Left", hl.dsp.window.resize({ x = -40, y = 0, relative = true }),
    { repeating = true, description = "Resize window narrower" })
hl.bind("SUPER + SHIFT + Left", hl.dsp.window.move({ direction = "left" }),
    { description = "Move window left" })
hl.bind("SUPER + SHIFT + P", hl.dsp.window.pin(), { description = "Pin floating window" })
-- Omarchy uses swap for SHIFT+direction; Ryoku uses move. Choose that behavior
-- deliberately instead of keeping conflicting bindings from both collections.

-- NATIVE MEDIA ACTIONS: modules/binds.lua
-- wpctl and playerctl are external dependencies, but no Ryoku daemon is needed.
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
    { locked = true, description = "Mute audio" })
hl.bind("XF86AudioPlay", hl.dsp.exec_cmd("playerctl play-pause"),
    { locked = true, description = "Play or pause" })
hl.bind("XF86AudioNext", hl.dsp.exec_cmd("playerctl next"), { locked = true, description = "Next track" })
hl.bind("XF86AudioPrev", hl.dsp.exec_cmd("playerctl previous"), { locked = true, description = "Previous track" })
hl.bind("SUPER + SHIFT + C", hl.dsp.exec_cmd("hyprpicker -a"), { description = "Pick color" })
-- Ryoku's volume helper caps amplification unless boost is explicitly enabled;
-- preserve that principle when choosing our volume commands.

-- HOTPLUG AND LID: modules/displays.lua and modules/lid.lua
-- Re-evaluate surviving outputs after removal as well as new outputs on add.
-- This example REQUIRES ryoku-monitor; it is not provided by these dotfiles.
local function rescale()
    hl.exec_cmd("command -v ryoku-monitor >/dev/null 2>&1 && ryoku-monitor autoscale")
end
hl.on("monitor.added", rescale)
hl.on("monitor.removed", rescale)
-- Locked lid bindings call ryoku-clamshell; its daemon/logind policy owns
-- suspend decisions. A compositor monitor command alone is not clamshell support.

-- LOADING AND SESSION NOTES: hyprland.lua; modules/{autostart,env}.lua
-- Load required defaults, then optional generated theme/hardware, then deliberate
-- user overrides. Probe missing optional files before requiring them, but report
-- malformed existing files. Our existing Noctalia palette guard follows this idea.
-- Startup commands are asynchronous: separate env-import and service-start calls
-- can race. Preserve ordering where it matters; our UWSM/Nimbus session must keep
-- its own service lifecycle instead of importing Ryoku's systemctl restart chain.
-- Gate hardware workarounds on the actual affected device. Do not blindly copy
-- NVIDIA decode hints, AQ_NO_MODIFIERS, GSK_RENDERER, or Ryoku's QML search paths.
-- Keep shell IPC ideas (overview, lock, launcher, clipboard, screenshots) mapped
-- to Noctalia rather than importing Ryoku's global shortcuts and daemon commands.
-- Not selected: hidden screen-share indicators; the unconditional fullscreen
-- reset hook; first-boot installers; JSON parsing by pattern matching; generated
-- rebind/state overlays; or the shell-specific desktop-block workspace helper.
]=]
