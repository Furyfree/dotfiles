local wezterm = require("wezterm")
local config = wezterm.config_builder()

local platform = wezterm.target_triple

-- === General ===
-- Wayland: Kun relevant for Linux
if platform:find("linux") then
    config.enable_wayland = false
    config.font_size = 14.0
end

config.automatically_reload_config = true
config.scrollback_lines = 10000

-- === Font ===
config.font = wezterm.font_with_fallback {
    "FiraCode Nerd Font",
    "JetBrainsMono Nerd Font",
    "SF Mono",
}
config.font_size = config.font_size or 14.0

-- === Theme ===
config.color_scheme = "Catppuccin Mocha"

-- === Appearance ===
config.window_background_opacity = 0.90
config.window_decorations = "TITLE|RESIZE"
config.window_close_confirmation = "NeverPrompt"

if platform:find("apple") then
    config.macos_window_background_blur = 20
    config.font_size = 19.0
end

config.window_padding = {
    left = 8,
    right = 8,
    top = 6,
    bottom = 6,
}

-- === Tab Bar ===
config.enable_tab_bar = true
config.hide_tab_bar_if_only_one_tab = true
config.show_new_tab_button_in_tab_bar = false
config.use_fancy_tab_bar = true
config.tab_max_width = 25

-- === Scroll ===
config.enable_scroll_bar = false

-- === Tab Bar Colors (Catppuccin Mocha matched) ===
config.colors = {
    tab_bar = {
        background = "#1e1e2e",

        active_tab = {
            bg_color = "#89b4fa",
            fg_color = "#1e1e2e",
            intensity = "Bold",
        },

        inactive_tab = {
            bg_color = "#313244",
            fg_color = "#cdd6f4",
        },

        inactive_tab_hover = {
            bg_color = "#89dceb",
            fg_color = "#1e1e2e",
            italic = true,
        },

        new_tab = {
            bg_color = "#1e1e2e",
            fg_color = "#89b4fa",
        },

        new_tab_hover = {
            bg_color = "#89dceb",
            fg_color = "#1e1e2e",
        },
    },
}

-- === Icon Tab Titles ===
wezterm.on("format-tab-title", function(tab)
    local title = tab.active_pane.title
    local icon = ""
    if tab.is_active then
        return { { Text = "  " .. icon .. " " .. title .. "  " } }
    else
        return { { Text = "  " .. title .. "  " } }
    end
end)

return config
