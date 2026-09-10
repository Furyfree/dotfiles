-- Reference only: this entire file is a comment and is not loaded or deployed.
-- Curated from ~/compare/omarchy at 8ea51516390320f8e768808b230098e67bdaa82c.
-- https://github.com/omacom/omarchy/tree/8ea51516390320f8e768808b230098e67bdaa82c/default/hypr
-- Adapted excerpts: helpers expanded to native hl calls, unrelated settings omitted.
-- These are independent ideas to review, not a proposed complete configuration.
-- SPDX-License-Identifier: MIT
--[=[
Copyright (c) David Heinemeier Hansson

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
]=]

--[=[
-- INPUT: default/hypr/input.lua
-- Fast key repeat, two-finger right-click, and restrained touchpad scrolling.
-- follow_mouse=1 is Omarchy's focus-follows-pointer choice; compare Ryoku's 2.
-- Keep our system keyboard layout. Omarchy also reads /etc/vconsole.conf and
-- puts a Latin layout first for keysym bindings when the selected layout is
-- non-Latin; its parser and layout list are not copied here.
hl.config({
    input = {
        follow_mouse = 1,
        repeat_rate = 40,
        repeat_delay = 250,
        numlock_by_default = true,
        touchpad = {
            natural_scroll = false,
            clickfinger_behavior = true,
            scroll_factor = 0.4,
        },
    },
    misc = { key_press_enables_dpms = true, mouse_move_enables_dpms = true },
})
-- Optional typing preference: Caps becomes Compose; both Shifts enable Caps.
-- A lone Shift clears it, reducing accidental persistent Caps Lock.
hl.config({ input = { kb_options = "compose:caps,shift:both_capslock_cancel" } })
-- Application-specific scrolling instead of changing every application.
hl.window_rule({ match = { class = "com.mitchellh.ghostty" }, scroll_touchpad = 0.2 })

-- APPEARANCE AND LAYOUT: default/hypr/looknfeel.lua
-- A low-cost visual baseline: no compositor blur/shadow, compact gaps.
-- Keep Noctalia's generated border colors; the static Omarchy palette is omitted.
hl.config({
    general = {
        gaps_in = 5, gaps_out = 10, border_size = 2,
        resize_on_border = false, allow_tearing = false, layout = "dwindle",
    },
    decoration = {
        rounding = 0,
        shadow = { enabled = false },
        blur = { enabled = false },
    },
    dwindle = { preserve_split = true, force_split = 2 },
    scrolling = { column_width = 0.49 },
    master = { new_status = "master" },
    cursor = { hide_on_key_press = true, warp_on_change_workspace = 1 },
    binds = { hide_special_on_workspace_change = true },
})
-- Scrolling and master are alternatives to dwindle, not simultaneous layouts.
-- Omarchy persists per-workspace layout choices through its own toggle helper
-- and default/hypr/workspace-layouts.lua; that state machinery is not portable.

-- GROUPED WINDOWS: default/hypr/looknfeel.lua and bindings/tiling.lua
-- Visible tab labels plus explicit group navigation.
hl.config({ group = { groupbar = {
    font_size = 12, font_family = "monospace",
    font_weight_active = "ultraheavy", font_weight_inactive = "normal",
    indicator_height = 1, indicator_gap = 5, height = 22,
    gaps_in = 5, gaps_out = 0,
} } })
hl.bind("SUPER + G", hl.dsp.group.toggle(), { description = "Toggle window grouping" })
hl.bind("SUPER + ALT + G", hl.dsp.window.move({ out_of_group = true }), { description = "Leave group" })
hl.bind("SUPER + ALT + TAB", hl.dsp.group.next(), { description = "Next grouped window" })
hl.bind("SUPER + ALT + SHIFT + TAB", hl.dsp.group.prev(), { description = "Previous grouped window" })

-- MOTION: default/hypr/looknfeel.lua
-- Short window/fade transitions; workspace motion disabled for a steady desktop.
hl.config({ animations = { enabled = true } })
hl.curve("easeOutQuint", { type = "bezier", points = { { 0.23, 1 }, { 0.32, 1 } } })
hl.curve("linear", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })
hl.curve("almostLinear", { type = "bezier", points = { { 0.5, 0.5 }, { 0.75, 1 } } })
hl.curve("quick", { type = "bezier", points = { { 0.15, 0 }, { 0.1, 1 } } })
hl.animation({ leaf = "windows", enabled = true, speed = 3.79, bezier = "easeOutQuint" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 4.1, bezier = "easeOutQuint", style = "popin 87%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 1.49, bezier = "linear", style = "popin 87%" })
hl.animation({ leaf = "border", enabled = true, speed = 5.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 1.73, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.46, bezier = "almostLinear" })
hl.animation({ leaf = "fade", enabled = true, speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "fadeSwitch", enabled = false })
hl.animation({ leaf = "workspaces", enabled = false })
-- Global layer animations are omitted: Noctalia animates its own surfaces.

-- WORKSPACES AND WINDOW MOVEMENT: default/hypr/bindings/tiling.lua
-- Physical number-row keycodes keep workspace shortcuts independent of symbols.
-- Check the actual keyboard before adopting these example keycodes.
for workspace = 1, 10 do
    local key = "code:" .. tostring(workspace + 9)
    hl.bind("SUPER + " .. key, hl.dsp.focus({ workspace = tostring(workspace) }),
        { description = "Switch to workspace " .. workspace })
    hl.bind("SUPER + SHIFT + ALT + " .. key,
        hl.dsp.window.move({ workspace = tostring(workspace), follow = false }),
        { description = "Send silently to workspace " .. workspace })
end
hl.bind("SUPER + S", hl.dsp.workspace.toggle_special("scratchpad"), { description = "Toggle scratchpad" })
hl.bind("SUPER + ALT + S", hl.dsp.window.move({ workspace = "special:scratchpad", follow = false }),
    { description = "Send to scratchpad" })
hl.bind("SUPER + TAB", hl.dsp.focus({ workspace = "e+1" }), { description = "Next occupied workspace" })
hl.bind("SUPER + SHIFT + TAB", hl.dsp.focus({ workspace = "e-1" }), { description = "Previous occupied workspace" })
hl.bind("SUPER + CTRL + TAB", hl.dsp.focus({ workspace = "previous" }), { description = "Previous workspace" })
hl.bind("SUPER + SHIFT + LEFT", hl.dsp.window.swap({ direction = "l" }), { description = "Swap window left" })
hl.bind("SUPER + SHIFT + ALT + LEFT", hl.dsp.workspace.move({ monitor = "l" }),
    { description = "Move workspace to left monitor" })
hl.bind("SUPER + F", hl.dsp.window.fullscreen({ mode = "fullscreen" }), { description = "Fullscreen" })
hl.bind("SUPER + ALT + F", hl.dsp.window.fullscreen({ mode = "maximized" }), { description = "Maximize" })
-- Omarchy repeats direction bindings for right/up/down and supports window
-- resizing in 25/100/300 pixel steps. Keep the graduated-step idea when mapping
-- our keybinds; avoid importing every alias and conflicting chord.

-- PICTURE-IN-PICTURE: default/hypr/apps/pip.lua
-- Floating, pinned, opaque video that preserves its aspect ratio.
-- Portability: verify title matching and monitor fit before adopting fixed size.
hl.window_rule({ match = { title = "(Picture.?in.?[Pp]icture)" }, tag = "+pip" })
hl.window_rule({ match = { tag = "pip" },
    float = true, pin = true, size = { 600, 338 }, keep_aspect_ratio = true,
    border_size = 0, opacity = "1 1",
    move = { "(monitor_w-window_w-40)", "(monitor_h*0.04)" },
})

-- DIALOGS, MEDIA AND PRIVACY: default/hypr/apps/{system,1password,jetbrains}.lua
-- Portal dialogs should float rather than rearrange the tiled workspace.
hl.window_rule({ match = { class = "xdg-desktop-portal-gtk" }, float = true, center = true })
hl.window_rule({ match = { class = "^(1[p|P]assword)$" }, no_screen_share = true, float = true })
-- Upstream's class pattern is retained for reference; inspect the installed app
-- class before adoption. no_screen_share is compositor behavior to test, not a
-- guarantee against every capture mechanism.
hl.window_rule({ match = { class = "^(jetbrains-.*)$" }, no_follow_mouse = true })
hl.window_rule({
    match = { class = "^(zoom|vlc|mpv|org.kde.kdenlive|com.obsproject.Studio|imv)$" },
    opacity = "1 1",
})
-- If default-opacity tags are adopted, remove that tag for these exceptions
-- before applying the default rule (see default/hypr/windows.lua).

-- FOCUS CORRECTIONS: default/hypr/windows.lua
hl.window_rule({ match = { class = ".*" }, suppress_event = "maximize" })
hl.window_rule({ match = {
    class = "^$", title = "^$", xwayland = true,
    float = true, fullscreen = false, pin = false,
}, no_focus = true })

-- MEDIA AND ACCESSIBILITY: default/hypr/bindings/{media,utilities}.lua
-- Keep lock-screen media keys and repeat only continuous changes. These commands
-- need Omarchy's helpers; select Noctalia/native equivalents before adoption.
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("omarchy-audio-output-volume raise"),
    { locked = true, repeating = true, description = "Volume up" })
hl.bind("ALT + XF86AudioRaiseVolume", hl.dsp.exec_cmd("omarchy-audio-output-volume +1"),
    { locked = true, repeating = true, description = "Volume up precisely" })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("omarchy-audio-input-mute"),
    { locked = true, description = "Mute microphone" })
hl.bind("SUPER + CTRL + Z", function()
    local zoom = hl.get_config("cursor.zoom_factor") or 1
    hl.config({ cursor = { zoom_factor = zoom + 1 } })
end, { description = "Zoom in" })
hl.bind("SUPER + CTRL + ALT + Z", function()
    hl.config({ cursor = { zoom_factor = 1 } })
end, { description = "Reset zoom" })

-- CONDITIONAL SHORTCUTS: default/hypr/bindings/utilities.lua
-- Screenshot selection binds exist only while its layer is open. It counts
-- per-monitor layers and unbinds each returned handle after the last closes,
-- preserving unrelated bindings on the same keys. That lifecycle is reusable;
-- the actual commands require omarchy-capture-region.
-- Clipboard reference: default/hypr/bindings/clipboard.lua uses terminal tags
-- to select CTRL+Insert/SHIFT+Insert instead of GUI CTRL+C/CTRL+V, and balances
-- injected key-down with a key-up timer. Keep explicit releases if porting it;
-- first check whether native app shortcuts already cover our workflow.

-- DISPLAY AND SESSION NOTES: config/hypr/monitors.lua; default/hypr/{envs,autostart}.lua
hl.monitor({ output = "", mode = "preferred", position = "auto", scale = "auto" })
-- Omarchy also sets GDK_SCALE=2 and xwayland.force_zero_scaling=true. Those are
-- monitor/application-dependent choices, not universal HiDPI fixes.
-- Prefer native Wayland with X11 fallback where necessary; retain our existing
-- Qt theme and UWSM environment ownership instead of copying Omarchy's gtk3
-- platform theme, PATH injection, NVIDIA hints, or session-service startup.
-- Useful architecture: defaults first, user settings later, generated theme
-- loaded optionally, startup inside hyprland.start rather than on every reload.
-- Not selected: hiding screen-sharing indicators, automatic first-run setup,
-- runtime flag/state loaders, package integration, or shell-specific launchers.
]=]
