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
    -- Let launching an already-running app bring its window forward.
    misc = { focus_on_activate = true },
    cursor = {
        no_warps = false,
        warp_on_change_workspace = 1,
        warp_on_toggle_special = 1,
    },
    -- Persistent workspaces are a starting set, not a limit on swipe navigation.
    gestures = { workspace_swipe_create_new = true },
})

-- New windows already receive keyboard focus; move the pointer there too.
-- Background windows must not take the pointer away from the active window.
hl.on("window.open", function(window)
    if window.active then
        hl.dispatch(hl.dsp.cursor.move({
            x = window.at.x + window.size.x / 2,
            y = window.at.y + window.size.y / 2,
        }))
    end
end)

-- Swipe between workspaces vertically, matching their animations.
hl.gesture({ fingers = 3, direction = "vertical", action = "workspace" })

-- Scroll through window columns horizontally.
hl.gesture({ fingers = 3, direction = "horizontal", action = "scroll_move" })
