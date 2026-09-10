-- Quick window transitions and vertical workspace movement.
hl.config({ animations = { enabled = true } })

-- Start promptly and settle without overshooting. Speed is in 100 ms units.
hl.curve("easeOut", { type = "bezier", points = { { 0.16, 1 }, { 0.3, 1 } } })
hl.curve("linear", { type = "bezier", points = { { 0, 0 }, { 1, 1 } } })
hl.animation({
    leaf = "global",
    enabled = true,
    speed = 1.8,
    bezier = "easeOut",
})

-- Open from 95% size in 150 ms; close with a small shrink in 120 ms.
hl.animation({
    leaf = "windowsIn",
    enabled = true,
    speed = 1.5,
    bezier = "easeOut",
    style = "popin 95%",
})
hl.animation({
    leaf = "windowsOut",
    enabled = true,
    speed = 1.2,
    bezier = "easeOut",
    style = "popin 95%",
})
hl.animation({ leaf = "fadeIn", enabled = true, speed = 1.5, bezier = "linear" })
hl.animation({
    leaf = "fadeOut",
    enabled = true,
    speed = 1.2,
    bezier = "linear",
})

-- Keep moves, swaps, and resizing smooth, with a short focus-color transition.
hl.animation({
    leaf = "windowsMove",
    enabled = true,
    speed = 1.8,
    bezier = "easeOut",
})
hl.animation({ leaf = "border", enabled = true, speed = 1, bezier = "linear" })

-- Workspaces feel stacked vertically, with full travel in 220 ms.
hl.animation({
    leaf = "workspaces",
    enabled = true,
    speed = 2.2,
    bezier = "easeOut",
    style = "slidevert",
})
