-- Minimal starter based on Hyprland 0.55's example/hyprland.lua.
-- https://github.com/hyprwm/Hyprland/blob/v0.55.0/LICENSE
--[[
BSD 3-Clause License

Copyright (c) 2022-2026, vaxerski
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
]]
-- Keep one file until the installed desktop has been tested.
local terminal = "ghostty"
local browser = "brave-origin"
local fileManager = "nautilus"
local mainMod = "SUPER"

-- greetd skips shell profiles; provide PATH when the login environment has none.
if not os.getenv("PATH") or os.getenv("PATH") == "" then
    hl.env("PATH", "/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin")
end
-- qt6ct also accepts qt5ct, allowing both Qt generations to load their plugin.
hl.env("QT_QPA_PLATFORMTHEME", "qt5ct")

hl.monitor({ output = "", mode = "preferred", position = "auto", scale = "auto" })

hl.config({
    general = {
        gaps_in = 5,
        gaps_out = 20,
        border_size = 2,
        layout = "dwindle",
    },
    decoration = { rounding = 10 },
    dwindle = { preserve_split = true },
})

-- Noctalia owns the generated palette. First login works before it exists.
if package.searchpath("noctalia", package.path) then
    require("noctalia").apply_theme()
end

-- Start once per session, not on config reload.
hl.on("hyprland.start", function()
    hl.exec_cmd("noctalia --daemon")
    hl.exec_cmd("librepods --hide")
end)

-- Standard starter keys, with B added for the selected browser.
hl.bind(mainMod .. " + Q", hl.dsp.exec_cmd(terminal), { description = "Open Ghostty terminal" })
hl.bind(mainMod .. " + B", hl.dsp.exec_cmd(browser), { description = "Open Brave browser" })
hl.bind(mainMod .. " + C", hl.dsp.window.close(), { description = "Close focused window" })
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd(fileManager), { description = "Open file manager" })
hl.bind(mainMod .. " + R", hl.dsp.exec_cmd("noctalia msg panel-toggle launcher"), { description = "Open Noctalia launcher" })
hl.bind(mainMod .. " + M", hl.dsp.exec_cmd("noctalia msg panel-toggle session"), { description = "Open Noctalia session menu" })
hl.bind(mainMod .. " + V", hl.dsp.window.float({ action = "toggle" }), { description = "Toggle floating window" })
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo(), { description = "Toggle pseudotiling" })
hl.bind(mainMod .. " + J", hl.dsp.layout("togglesplit"), { description = "Toggle split direction" })

-- Focus with arrows; switch workspaces with digits (0 means workspace 10).
hl.bind(mainMod .. " + left", hl.dsp.focus({ direction = "left" }), { description = "Focus window to the left" })
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }), { description = "Focus window to the right" })
hl.bind(mainMod .. " + up", hl.dsp.focus({ direction = "up" }), { description = "Focus window above" })
hl.bind(mainMod .. " + down", hl.dsp.focus({ direction = "down" }), { description = "Focus window below" })
for i = 1, 10 do
    local key = i % 10
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = i }), { description = "Switch to workspace " .. i })
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }), { description = "Move window to workspace " .. i })
end

-- Hold Super and drag with the left/right mouse button to move/resize.
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(), { mouse = true, description = "Move window with mouse" })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true, description = "Resize window with mouse" })
