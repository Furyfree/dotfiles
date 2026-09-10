-- Window and layer rules for applications and Noctalia surfaces.

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
