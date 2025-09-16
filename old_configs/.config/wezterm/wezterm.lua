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
-- config.window_decorations = "TITLE|RESIZE"
-- config.window_decorations = "INTEGRATED_BUTTONS|RESIZE"



-- === Font ===
config.font = wezterm.font_with_fallback {
    "FiraCode Nerd Font",
    "JetBrainsMono Nerd Font",
    "SF Mono",
    "Noto Color Emoji",
    "Apple Color Emoji",
    "Segoe UI Emoji",
}
config.font_size = config.font_size or 14.0
config.warn_about_missing_glyphs = false

-- === Theme ===
config.color_scheme = "Catppuccin Mocha"

-- === Appearance ===
config.window_background_opacity = 0.50
config.window_decorations = "TITLE|RESIZE"
config.window_close_confirmation = "NeverPrompt"

if platform:find("apple") then
    config.macos_window_background_blur = 50
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
            bg_color = "#1e1e2e", -- Samme farve som terminal baggrund
            fg_color = "#cdd6f4", -- Lysere tekst for bedre kontrast
            intensity = "Bold",
            underline = "Single", -- Underline for at markere aktiv tab
        },

        inactive_tab = {
            bg_color = "#282838", -- Mere neutral grå farve
            fg_color = "#a0a0b0", -- Dæmpet tekst farve
        },

        inactive_tab_hover = {
            bg_color = "#353545", -- Mørkere grå ved hover
            fg_color = "#cdd6f4", -- Lysere tekst ved hover
            italic = true,
        },

        new_tab = {
            bg_color = "#1e1e2e",
            fg_color = "#89b4fa",
        },

        new_tab_hover = {
            bg_color = "#353545",
            fg_color = "#cdd6f4",
        },
    },
}

-- === Icon Tab Titles ===
wezterm.on("format-tab-title", function(tab)
    -- Get the current working directory
    local process_info = tab.active_pane.user_vars
    local cwd = tab.active_pane.current_working_dir
    local title = tab.active_pane.title
    local folder_name = title

    -- Extract folder name from the path if available
    if cwd then
        -- Convert URI to path if needed
        local path = cwd.file_path or cwd.path or ""

        -- Extract the last part of the path (folder name)
        if path and path ~= "" then
            -- Remove trailing slash if present
            if path:sub(-1) == "/" then
                path = path:sub(1, -2)
            end

            -- Get the last component of the path
            folder_name = path:match("([^/]+)$") or title
        end
    end

    local icon = ""
    if tab.is_active then
        return { { Text = "  " .. icon .. " " .. folder_name .. "  " } }
    else
        return { { Text = "  " .. folder_name .. "  " } }
    end
end)

return config
