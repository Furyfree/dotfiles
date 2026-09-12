-- Window and layer rules for applications and Noctalia surfaces.

-- Assign app tags before the shared rules that use them.
hl.window_rule({
    name = "1password",
    match = { class = "^com\\.onepassword\\.OnePassword$" },
    tag = "+centered-floating",
})
hl.window_rule({
    name = "screen-share-picker",
    match = { class = "^hyprland-share-picker$" },
    tag = "+centered-floating",
})
hl.window_rule({
    name = "terminal-presentation",
    match = { class = "^com\\.mitchellh\\.ghostty\\.presentation$" },
    tag = "+centered-floating",
})
hl.window_rule({
    name = "steam-settings-and-friends",
    -- Steam gives these and its main window the same class and window type.
    -- Keep the app match and narrow it to these two initial titles.
    match = {
        class = "^steam$",
        initial_title = "^(Steam Settings|Friends List)$",
    },
    tag = "+centered-floating",
})

-- Assign verified game classes tag = "+game" above this rule to start fullscreen.
hl.window_rule({
    name = "game",
    match = { tag = "game" },
    fullscreen = true,
})

-- Other apps can opt in with tag = "+centered-floating" above this rule.
hl.window_rule({
    name = "centered-floating",
    match = { tag = "centered-floating" },
    float = true,
    size = { "window_w", "min(700,monitor_h*0.8)" },
    center = true,
})

-- Keep Noctalia settings separate from the scrolling columns.
hl.window_rule({
    name = "noctalia-settings",
    match = { class = "^dev\\.noctalia\\.Noctalia$" },
    float = true,
    size = { 1080, 920 },
    center = true,
})

-- Blur Noctalia's visible surfaces while keeping its own panel animations.
hl.layer_rule({
    name = "noctalia",
    match = {
        namespace = "^noctalia-(bar-.+|notification|dock|panel|attached-panel|osd|window-switcher)$",
    },
    no_anim = true,
    blur = true,
    blur_popups = true,
    ignore_alpha = 0.5,
})
