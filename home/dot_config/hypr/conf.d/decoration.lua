-- Gaps, borders, rounding, opacity, blur, and shadows.
hl.config({
    -- Equal gaps keep off-screen scrolling columns outside the monitor edge.
    general = { gaps_in = 3, gaps_out = 3, border_size = 2 },
    decoration = {
        -- Rounded corners with no extra transparency or dimming on inactive windows.
        rounding = 12,
        rounding_power = 2,
        active_opacity = 1,
        inactive_opacity = 1,
        dim_inactive = false,

        -- Light blur behind transparent backgrounds; apps control their own opacity.
        blur = { enabled = true, size = 3, passes = 2 },

        -- Small, soft shadows give overlapping windows some separation.
        shadow = {
            enabled = true,
            range = 10,
            render_power = 3,
            color = 0x40000000,
        },
    },
})
