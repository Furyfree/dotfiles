-- Keyboard and mouse bindings for applications, windows, and workspaces.
local mainMod = "SUPER"

-- Keep directional focus and swaps on this monitor; move between monitors explicitly.
hl.config({ binds = { window_direction_monitor_fallback = false } })

-- Application launchers, Noctalia panels, and basic window controls.
hl.bind(
    mainMod .. " + SHIFT + B",
    hl.dsp.exec_cmd("brave-origin"),
    { description = "Open Brave browser" }
)
hl.bind(
    mainMod .. " + SHIFT + F",
    hl.dsp.exec_cmd("nautilus"),
    { description = "Open file manager" }
)
hl.bind(
    mainMod .. " + SHIFT + O",
    hl.dsp.exec_cmd("obs"),
    { description = "Open OBS Studio" }
)
hl.bind(
    mainMod .. " + SHIFT + A",
    hl.dsp.exec_cmd("chatgpt"),
    { description = "Open ChatGPT" }
)
hl.bind(
    mainMod .. " + SHIFT + Z",
    hl.dsp.exec_cmd("zed"),
    { description = "Open Zed" }
)
hl.bind(
    mainMod .. " + SHIFT + V",
    hl.dsp.exec_cmd("codium"),
    { description = "Open VSCodium" }
)
hl.bind(
    mainMod .. " + SHIFT + D",
    hl.dsp.exec_cmd("vesktop"),
    { description = "Open Discord in Vesktop" }
)
hl.bind(
    mainMod .. " + SHIFT + E",
    hl.dsp.exec_cmd("flatpak run com.fastmail.Fastmail"),
    { description = "Open Fastmail" }
)
hl.bind(
    mainMod .. " + Return",
    hl.dsp.exec_cmd("ghostty"),
    { description = "Open Ghostty terminal" }
)
hl.bind(
    mainMod .. " + W",
    hl.dsp.window.close(),
    { description = "Close focused window" }
)
hl.bind(
    mainMod .. " + Q",
    hl.dsp.window.float({ action = "toggle" }),
    { description = "Toggle floating window" }
)
hl.bind(
    mainMod .. " + Space",
    hl.dsp.exec_cmd("noctalia msg panel-toggle launcher"),
    { description = "Open Noctalia launcher" }
)
hl.bind(
    mainMod .. " + comma",
    hl.dsp.exec_cmd("noctalia msg settings-toggle"),
    { description = "Toggle Noctalia settings" }
)
hl.bind(
    mainMod .. " + M",
    hl.dsp.exec_cmd("noctalia msg panel-toggle session"),
    { description = "Open Noctalia session menu" }
)
hl.bind(
    mainMod .. " + Escape",
    hl.dsp.exec_cmd(
        "noctalia msg panel-toggle kenn/keybind-cheatsheet:cheatsheet"
    ),
    { description = "Open keybind cheatsheet" }
)

-- Scrolling column controls and fullscreen.
hl.bind(
    mainMod .. " + R",
    hl.dsp.layout("colresize +conf"),
    { description = "Cycle column width" }
)
hl.bind(
    mainMod .. " + C",
    hl.dsp.layout("center"),
    { description = "Center column" }
)
hl.bind(
    mainMod .. " + F",
    hl.dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" }),
    { description = "Toggle fullscreen" }
)

-- Noctalia handles locking, window selection, and screenshot capture.
hl.bind(
    mainMod .. " + L",
    hl.dsp.exec_cmd("noctalia msg session lock"),
    { description = "Lock session" }
)
hl.bind(
    mainMod .. " + SHIFT + L",
    hl.dsp.exec_cmd("noctalia msg panel-toggle session"),
    { description = "Open Noctalia session menu" }
)
hl.bind(
    "ALT + Tab",
    hl.dsp.exec_cmd("noctalia msg window-switcher"),
    { description = "Open window switcher" }
)
hl.bind(
    mainMod .. " + SHIFT + S",
    hl.dsp.exec_cmd("noctalia msg screenshot-region"),
    { description = "Capture screen region" }
)
hl.bind(
    "Print",
    hl.dsp.exec_cmd("noctalia msg screenshot-region"),
    { description = "Capture screen region" }
)
hl.bind(
    "SHIFT + Print",
    hl.dsp.exec_cmd("noctalia msg screenshot-fullscreen"),
    { description = "Capture current monitor" }
)

-- Volume and brightness repeat while held and remain available on the lock screen.
for _, binding in ipairs({
    { "XF86AudioRaiseVolume", "volume-up", "Increase volume" },
    { "XF86AudioLowerVolume", "volume-down", "Decrease volume" },
    { "XF86MonBrightnessUp", "brightness-up", "Increase brightness" },
    { "XF86MonBrightnessDown", "brightness-down", "Decrease brightness" },
}) do
    hl.bind(
        binding[1],
        hl.dsp.exec_cmd("noctalia msg " .. binding[2]),
        { description = binding[3], locked = true, repeating = true }
    )
end
hl.bind(
    "XF86AudioMute",
    hl.dsp.exec_cmd("noctalia msg volume-mute"),
    { description = "Toggle speaker mute", locked = true }
)
hl.bind(
    "XF86AudioMicMute",
    hl.dsp.exec_cmd("noctalia msg mic-mute"),
    { description = "Toggle microphone mute", locked = true }
)

-- Super+arrows focuses; Shift swaps windows; Shift+Ctrl moves them between monitors.
for _, direction in ipairs({ "left", "right", "up", "down" }) do
    hl.bind(
        mainMod .. " + " .. direction,
        hl.dsp.focus({ direction = direction }),
        { description = "Focus window " .. direction }
    )
    hl.bind(
        mainMod .. " + SHIFT + " .. direction,
        hl.dsp.window.swap({ direction = direction }),
        { description = "Swap window " .. direction .. " on this monitor" }
    )
    hl.bind(
        mainMod .. " + SHIFT + CTRL + " .. direction,
        hl.dsp.window.move({ monitor = direction:sub(1, 1) }),
        { description = "Move window to monitor " .. direction }
    )
end

-- Super+digits switches workspaces; Shift moves the window there. 0 means workspace 10.
for i = 1, 10 do
    local key = i % 10
    hl.bind(
        mainMod .. " + " .. key,
        hl.dsp.focus({ workspace = i }),
        { description = "Switch to workspace " .. i }
    )
    hl.bind(
        mainMod .. " + SHIFT + " .. key,
        hl.dsp.window.move({ workspace = i }),
        { description = "Move window to workspace " .. i }
    )
end

-- Hold Super and drag with the left/right mouse button to move/resize.
hl.bind(
    mainMod .. " + mouse:272",
    hl.dsp.window.drag(),
    { mouse = true, description = "Move window with mouse" }
)
hl.bind(
    mainMod .. " + mouse:273",
    hl.dsp.window.resize(),
    { mouse = true, description = "Resize window with mouse" }
)
