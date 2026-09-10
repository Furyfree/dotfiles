-- Scrolling columns, window widths, and focus behavior.
hl.config({
    general = { layout = "scrolling" },
    scrolling = {
        -- A lone column fills the workspace; additional columns use half-width.
        column_width = 0.5,
        fullscreen_on_one_column = true,
        direction = "right",

        -- Bring focused columns into view without centering or scrolling on hover.
        focus_fit_method = 1,
        follow_focus = true,
        follow_min_visible = 1.0,

        -- Match Niri's width presets and stop column navigation at either end.
        explicit_column_widths = "0.33333, 0.5, 0.66667",
        wrap_focus = false,
        wrap_swapcol = false,
    },
})
