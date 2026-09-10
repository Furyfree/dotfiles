-- Keyboard, mouse, touchpad, and gesture settings.

hl.config({
    input = {
        -- Danish layout, Num Lock, and responsive key repeat.
        kb_layout = "dk",
        numlock_by_default = true,
        repeat_rate = 40,
        repeat_delay = 250,

        -- Focus follows the pointer; keep traditional mouse-wheel scrolling.
        follow_mouse = 1,
        sensitivity = 0,
        natural_scroll = false,

        -- Scroll content directly and use finger count for physical clicks.
        touchpad = {
            natural_scroll = true,
            tap_to_click = true,
            clickfinger_behavior = true,
            disable_while_typing = true,
        },
    },
    -- Persistent workspaces are a starting set, not a limit on swipe navigation.
    gestures = { workspace_swipe_create_new = true },
})

-- Swipe between workspaces vertically, matching their animations.
hl.gesture({ fingers = 3, direction = "vertical", action = "workspace" })

-- Scroll through window columns horizontally.
hl.gesture({ fingers = 3, direction = "horizontal", action = "scroll_move" })
