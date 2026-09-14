#!/usr/bin/env python3
"""Check the Hyprland starter without launching a desktop or applications."""

import json
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import tomllib
import unittest


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "home/dot_config/hypr/hyprland.lua"
MODULES = {path.name.removesuffix(".tmpl").removesuffix(".lua"): path
           for path in sorted((CONFIG.parent / "conf.d").glob("*.lua*"))}
CHEZMOI = shutil.which("chezmoi")
LUA = shutil.which("lua") or shutil.which("luajit")
HYPRLAND = shutil.which("Hyprland")


class Hyprland(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-hyprland-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.env = {"HOME": str(self.home), "USERPROFILE": str(self.home), "PATH": "",
                    "XDG_CONFIG_HOME": str(self.home / ".config"),
                    "XDG_CONFIG_DIRS": str(self.root / "system-config"),
                    "XDG_DATA_HOME": str(self.root / "data"),
                    "XDG_CACHE_HOME": str(self.root / "cache"),
                    "XDG_STATE_HOME": str(self.root / "state"),
                    "XDG_RUNTIME_DIR": str(self.root / "runtime")}

    def run_command(self, *args, input=None):
        return subprocess.run(args, input=input, cwd=self.root, env=self.env,
                              capture_output=True, text=True, timeout=30)

    def dump_config(self, data):
        result = self.run_command(
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--cache", str(self.root / "chezmoi-cache"),
            "--persistent-state", str(self.root / "chezmoi.boltdb"),
            "--skip-secrets", "--override-data", json.dumps(data),
            "dump", "--format=json")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def render_config(self, machine):
        entries = self.dump_config({
            "chezmoi": {"os": "linux"}, "Machine": machine,
            "profiles": ["hyprland-noctalia"], "ManagedByNimbus": False,
            "onePasswordSsh": False,
        })
        target = self.root / machine / "hypr"
        for name, entry in entries.items():
            if name.startswith(".config/hypr/") and "contents" in entry:
                path = target / name.removeprefix(".config/hypr/")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(entry["contents"])
        return target / "hyprland.lua"

    @unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
    def test_platform_and_profile_gate(self):
        for platform in ("linux", "darwin", "windows"):
            for profiles in (None, ["common"], ["niri-dms"], ["hyprland-noctalia"],
                             ["hyprland-noctalia", "niri-dms"]):
                for managed in (False, True):
                    with self.subTest(platform=platform, profiles=profiles, managed=managed):
                        data = {"chezmoi": {"os": platform}, "ManagedByNimbus": managed,
                                "onePasswordSsh": False}
                        if profiles is not None:
                            data["profiles"] = profiles
                        entries = self.dump_config(data)
                        targets = {name for name in entries
                                   if name == ".config/hypr" or name.startswith(".config/hypr/")}
                        enabled = platform == "linux" and "hyprland-noctalia" in (profiles or [])
                        expected = {".config/hypr", ".config/hypr/hyprland.lua", ".config/hypr/conf.d",
                                    ".config/hypr/plugins.toml"}
                        expected.update(f".config/hypr/conf.d/{name}.lua" for name in MODULES)
                        self.assertEqual(targets, expected if enabled else set())
                        if enabled:
                            self.assertEqual(
                                tomllib.loads(entries[".config/hypr/plugins.toml"]["contents"]),
                                {"schema": 1, "enabled": ["scrolloverview"]})
                            self.assertEqual(entries[".config/hypr/hyprland.lua"]["contents"],
                                             CONFIG.read_text())
                            for name, source in MODULES.items():
                                if source.suffix != ".tmpl":
                                    self.assertEqual(entries[f".config/hypr/conf.d/{name}.lua"]["contents"],
                                                     source.read_text())
                        self.assertEqual(".config/noctalia/config.toml" in entries, enabled)
                        self.assertEqual(".config/uwsm/env" in entries, enabled)
                        self.assertEqual(".config/uwsm/env-hyprland" in entries, enabled)
                        self.assertEqual(".config/systemd" in entries, enabled)
                        for unit in ("app-noctalia.service", "app-udiskie.service"):
                            target = f".config/systemd/user/{unit}.d/20-graceful-stop.conf"
                            self.assertEqual(target in entries, enabled)
                            if enabled:
                                self.assertIn("TimeoutStopFailureMode=terminate", entries[target]["contents"])

    @unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
    def test_monitor_machine_gate(self):
        for machine in (None, "desktop", "laptop"):
            with self.subTest(machine=machine):
                data = {"chezmoi": {"os": "linux"}, "profiles": ["hyprland-noctalia"],
                        "ManagedByNimbus": False, "onePasswordSsh": False}
                if machine is not None:
                    data["Machine"] = machine
                contents = self.dump_config(data)[".config/hypr/conf.d/monitors.lua"]["contents"]
                self.assertIn('output = ""', contents)
                self.assertEqual('output = "eDP-1"' in contents, machine == "laptop")
                self.assertEqual('scale = 1.5' in contents, machine == "laptop")
                if machine == "desktop":
                    self.assertIn('output = "DP-4"', contents)
                    self.assertIn('output = "DP-3"', contents)
                else:
                    self.assertNotIn('output = "DP-', contents)
                    self.assertNotIn("default_monitor", contents)

    @unittest.skipUnless(LUA and CHEZMOI, "lua or chezmoi is not installed")
    def test_lua_bindings_and_startup_are_declarative(self):
        # A strict API double checks Lua execution, not Hyprland's native schema.
        config = self.render_config("desktop")
        modules = [str(config.parent / f"conf.d/{name}.lua") for name in MODULES]
        result = self.run_command(LUA, "-", str(config), *modules, input=r'''
local binds, hooks, spawned, environment = {}, {}, {}, {}
local dispatched = {}
local windows, gestures = {}, {}
local active_window
local monitor = { name = "DP-4" }
local active_workspace = { id = 2, monitor = monitor }
local previous_workspace = { id = 1, monitor = monitor }
local curves, animations = { default = true }, {}
-- Model Hyprland 0.56's explicit-path require with the actual module files.
for i = 2, #arg do
    local name = assert(arg[i]:match("/conf%.d/([^/]+)$"))
    package.preload["./conf.d/" .. name] = assert(loadfile(arg[i]))
end
local function action(name)
    return function(value) return { name = name, value = value } end
end
hl = {
    plugin = {},
    env = function(key, value)
        assert(type(key) == "string" and type(value) == "string")
        environment[key] = value
    end,
    curve = function(name, value)
        assert(not curves[name], "duplicate animation curve: " .. name)
        curves[name] = value
    end,
    animation = function(value)
        assert(not animations[value.leaf], "duplicate animation: " .. value.leaf)
        if value.bezier then assert(curves[value.bezier], "undefined animation curve") end
        if value.speed then assert(value.speed > 0, "animation speed must be positive") end
        animations[value.leaf] = value
    end,
    layer_rule = function(value) assert(type(value.match) == "table") end,
    window_rule = function(value) assert(type(value.match) == "table") end,
    workspace_rule = function(value)
        assert(type(value.workspace) == "string" and #value.workspace > 0)
    end,
    gesture = function(value)
        assert(type(value.fingers) == "number" and value.fingers > 0)
        assert(type(value.direction) == "string" and type(value.action) == "function")
        assert(not gestures[value.direction], "duplicate gesture direction")
        gestures[value.direction] = value.action
    end,
    monitor = function(value) assert(type(value.output) == "string") end,
    config = function(value)
        for section, entries in pairs(value) do
            assert(type(section) == "string" and type(entries) == "table")
        end
    end,
    on = function(event, callback)
        hooks[event] = hooks[event] or {}
        table.insert(hooks[event], callback)
    end,
    exec_cmd = function(command) table.insert(spawned, command) end,
    get_active_window = function() return active_window end,
    get_active_workspace = function() return active_workspace end,
    get_active_monitor = function() return monitor end,
    get_last_workspace = function(selected)
        assert(selected == monitor)
        return previous_workspace
    end,
    get_workspaces = function() return { previous_workspace, active_workspace } end,
    get_windows = function(filter)
        assert(filter.mapped == true)
        local mapped = {}
        for _, window in ipairs(windows) do
            if window.mapped then table.insert(mapped, window) end
        end
        return mapped
    end,
    dispatch = function(command) table.insert(dispatched, command) end,
    bind = function(key, value, options)
        local normalized = key:upper():gsub("%s+", "")
        assert(not binds[normalized], "duplicate shortcut: " .. key)
        assert(options and type(options.description) == "string" and #options.description > 0,
               "missing description: " .. key)
        assert(type(value) == "table" or type(value) == "function")
        binds[normalized] = value
        if key:find("mouse:") then assert(options.mouse) end
    end,
    dsp = {
        cursor = { move = action("cursor.move") },
        exec_cmd = action("exec"), focus = action("focus"), layout = action("layout"),
        window = {
            close = action("close"), float = action("float"), fullscreen = action("fullscreen"),
            move = action("move"), swap = action("swap"), drag = action("drag"), resize = action("resize"),
        },
    },
}
assert(loadfile(arg[1]))()
for i = 2, #arg do
    local name = arg[i]:match("/conf%.d/([^/]+)$")
    assert(package.loaded["./conf.d/" .. name], "module is not loaded: " .. name)
end
assert(next(environment) == nil, "session environment belongs to UWSM")
assert(#spawned == 0, "loading/reloading must not launch processes")
assert(#dispatched == 0, "loading/reloading must not move the pointer")
-- Only the selected app shortcuts use compositor focus-or-launch.
local apps = {
    { "O", "com.obsproject.Studio", "obs" },
    { "A", "Chatgpt", "chatgpt" },
    { "R", "zeron", "zeron" },
    { "T", "t3code" },
    { "D", "vesktop", "vesktop" },
    { "G", "signal", "signal-desktop" },
    { "E", "com.fastmail.Fastmail", "flatpak run com.fastmail.Fastmail" },
}
for _, app in ipairs(apps) do
    local binding = binds["SUPER+SHIFT+" .. app[1]]
    windows, spawned, dispatched = {}, {}, {}
    binding()
    assert(#spawned == 1 and #dispatched == 0, "missing app must launch")
    if app[3] then
        assert(spawned[1] == "uwsm-app -- " .. app[3])
    else
        assert(spawned[1]:find("for app in t3code-nightly t3code", 1, true))
    end
    local recent = { class = app[2], mapped = true, focus_history_id = 2 }
    windows = {
        { class = app[2], mapped = true, focus_history_id = -1 },
        { class = app[2], mapped = true, focus_history_id = 8 },
        { class = app[2], mapped = true, hidden = true, focus_history_id = 0 },
        { class = app[2], mapped = false, focus_history_id = 0 },
        { class = app[2] .. ".other", mapped = true, focus_history_id = 0 },
        recent,
    }
    spawned, dispatched = {}, {}
    binding()
    assert(#spawned == 0 and #dispatched == 1, "existing app must focus without launch")
    assert(dispatched[1].name == "focus" and dispatched[1].value.window == recent,
           "focus must select the most recently used eligible window")
    recent.active = true
    dispatched = {}
    binding()
    assert(#spawned == 0 and #dispatched == 0, "active app must be a no-op")
end
for key, command in pairs({
    ["SUPER+SHIFT+B"] = "brave-origin", ["SUPER+SHIFT+F"] = "nautilus",
    ["SUPER+SHIFT+Z"] = "zed", ["SUPER+SHIFT+V"] = "codium",
    ["SUPER+RETURN"] = "ghostty", ["SUPER+SHIFT+P"] = "1password",
    ["CTRL+SHIFT+SPACE"] = "1password --quick-access",
}) do
    assert(binds[key].name == "exec" and binds[key].value == "uwsm-app -- " .. command,
           "native launch/activation must be preserved: " .. key)
end
-- A fresh installation must keep the keymap usable before HyprPM setup.
spawned, dispatched = {}, {}
binds["SUPER+O"]()
assert(#spawned == 1 and #dispatched == 0)
assert(spawned[1]:find("Workspace overview unavailable", 1, true))
local overview_calls = {}
hl.plugin.scrolloverview = {
    -- In a keybind callback the plugin executes directly and returns nothing.
    overview = function(value) table.insert(overview_calls, value) end,
}
spawned, dispatched = {}, {}
binds["SUPER+O"]()
assert(#overview_calls == 1 and overview_calls[1] == "toggle all")
assert(#spawned == 0 and #dispatched == 0)
windows, spawned, dispatched = {}, {}, {}
-- Opening a background window must not move the pointer.
for _, callback in ipairs(hooks["window.open"] or {}) do
    callback({ active = false })
end
assert(#dispatched == 0, "background windows must not take the pointer")
for _, callback in ipairs(hooks["window.open"] or {}) do
    callback({ active = true, at = { x = 100, y = 200 }, size = { x = 800, y = 600 } })
end
assert(#dispatched == 1, "a foreground window should receive the pointer once")
assert(dispatched[1].name == "cursor.move")
assert(dispatched[1].value.x == 500 and dispatched[1].value.y == 500)
-- The final picker mapping must not regress to direct window cycling.
assert(binds["SUPER+TAB"].name == "exec")
assert(binds["SUPER+TAB"].value == "noctalia msg window-switcher")
assert(not binds["SUPER+SHIFT+TAB"] and not binds["SUPER+CTRL+TAB"])
dispatched = {}
binds["ALT+TAB"]()
assert(#dispatched == 1 and dispatched[1].value.workspace == previous_workspace)

-- Each swipe calls exactly one directional action, in natural-scroll direction.
for direction, expected in pairs({ left = "r", right = "l" }) do
    dispatched = {}
    gestures[direction]()
    assert(#dispatched == 1 and dispatched[1].name == "focus")
    assert(dispatched[1].value.direction == expected)
end
for direction, expected in pairs({ up = "r+1", down = "r-1" }) do
    dispatched = {}
    gestures[direction]()
    assert(#dispatched == 1 and dispatched[1].value.workspace == expected)
end
assert(not gestures.horizontal and not gestures.vertical)
active_workspace = previous_workspace
dispatched = {}
gestures.down()
assert(#dispatched == 0, "swiping down at the first workspace must not wrap")

-- Regression: scrolling-only bindings used to raise errors in Dwindle.
active_window = { mapped = true, floating = false, fullscreen = 0,
    workspace = active_workspace, layout = { name = "dwindle" } }
windows = { active_window }
for _, key in ipairs({ "SUPER+R", "SUPER+C", "SUPER+ALT+LEFT", "SUPER+ALT+RIGHT", "SUPER+J" }) do
    dispatched = {}
    binds[key]()
    assert(#dispatched == 0, "unsupported/single-tile action must be ignored: " .. key)
end
dispatched = {}
binds["SUPER+F"]()
assert(dispatched[1].name == "fullscreen" and dispatched[1].value.mode == "maximized")
local second = { mapped = true, floating = false, layout = { name = "dwindle" } }
windows[2] = second
dispatched = {}
binds["SUPER+J"]()
assert(#dispatched == 1 and dispatched[1].value == "togglesplit")

active_window.layout = { name = "scrolling", column = { width = 0.5, index = 0 } }
active_window.layout.column.windows = { active_window }
second.layout = { name = "scrolling", column = { index = 1 } }
dispatched = {}
binds["SUPER+J"]()
binds["SUPER+ALT+LEFT"]()
assert(#dispatched == 0, "no split action or nonexistent previous column")
binds["SUPER+ALT+RIGHT"]()
assert(#dispatched == 1 and dispatched[1].value == "consume_or_expel next")
active_window.layout.column.windows = { active_window, second }
dispatched = {}
binds["SUPER+ALT+LEFT"]()
assert(dispatched[1].value == "consume_or_expel prev")
for _, floating in ipairs({ true, false }) do
    active_window.floating = floating
    active_window.fullscreen = floating and 0 or 2
    dispatched = {}
    binds["SUPER+R"](); binds["SUPER+C"](); binds["SUPER+J"](); binds["SUPER+ALT+RIGHT"]()
    assert(#dispatched == 0, "floating/fullscreen window must skip tiled layout commands")
end
active_window, windows, dispatched = nil, {}, {}
for _, callback in ipairs(hooks["hyprland.start"] or {}) do callback() end
-- Exercise the conditional Bluetooth startup without pinning other startup commands.
local bluetooth = {}
for _, command in ipairs(spawned) do
    if command:find("/sys/class/bluetooth", 1, true) then table.insert(bluetooth, command) end
end
assert(#bluetooth == 1, "expected one conditional Bluetooth startup")
print(bluetooth[1])
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        bluetooth = self.root / "bluetooth adapters"
        command = result.stdout.replace("/sys/class/bluetooth", shlex.quote(str(bluetooth)))
        binaries = self.root / "bin"
        binaries.mkdir()
        librepods = binaries / "librepods"
        librepods.write_text('#!/bin/sh\nprintf "librepods:%s\\n" "$@"\n')
        librepods.chmod(0o755)
        systemctl = binaries / "systemctl"
        systemctl.write_text('#!/bin/sh\n'
                             'if [ "$2" = cat ]; then exit "${SERVICE_MISSING:-0}"; fi\n'
                             'printf "systemctl:%s %s %s\\n" "$1" "$2" "$3"\n')
        systemctl.chmod(0o755)
        self.env["PATH"] = str(binaries)
        for count in (None, 0, 1, 2):
            with self.subTest(adapters=count):
                if count is not None:
                    bluetooth.mkdir(exist_ok=True)
                if count:
                    (bluetooth / f"hci{count}").symlink_to(binaries, target_is_directory=True)
                result = self.run_command("/bin/sh", "-c", command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout,
                                 "systemctl:--user start librepods.service\n" if count else "")

        self.env["SERVICE_MISSING"] = "1"
        result = self.run_command("/bin/sh", "-c", command)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        del self.env["SERVICE_MISSING"]

        # Adapters are present, but LibrePods is not installed.
        librepods.unlink()
        result = self.run_command("/bin/sh", "-c", command)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    @unittest.skipUnless(LUA and shutil.which("mkdir"), "lua or mkdir is not installed")
    def test_workspace_layout_choices_persist_as_local_data(self):
        state = self.root / "state with ' quote"
        self.env["XDG_STATE_HOME"] = str(state)
        self.env["PATH"] = str(Path(shutil.which("mkdir")).parent)
        module = CONFIG.parent / "conf.d/workspace-layouts.lua"
        result = self.run_command(LUA, "-", str(module), input=r'''
local current = { id = 1, tiled_layout = "dwindle" }
local rules = {}
hl = {
    get_active_workspace = function() return current end,
    workspace_rule = function(rule) rules[rule.workspace] = rule.layout end,
    exec_cmd = function(_) end,
}
local actions = assert(loadfile(arg[1]))()
assert(next(rules) == nil)
actions.toggle()
assert(rules["1"] == "scrolling")
current = { id = 2, tiled_layout = "scrolling" }
actions.toggle()
assert(rules["2"] == "dwindle")
local path = os.getenv("XDG_STATE_HOME") .. "/hypr/workspace-layouts/choices.tsv"
local file = assert(io.open(path, "r"))
assert(file:read("*a") == "1\tscrolling\n2\tdwindle\n")
file:close()
file = assert(io.open(path, "a"))
file:write("invalid\tmaster\n3\tunknown\nthis is not Lua code\n")
file:close()
rules = {}
assert(loadfile(arg[1]))()
assert(rules["1"] == "scrolling" and rules["2"] == "dwindle")
assert(rules["3"] == nil and rules.invalid == nil)
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(HYPRLAND and CHEZMOI, "Hyprland or chezmoi is not installed; native check needs 0.56+")
    def test_native_config(self):
        for machine in ("desktop", "laptop"):
            with self.subTest(machine=machine):
                config = self.render_config(machine)
                result = self.run_command(HYPRLAND, "--verify-config", "--config", str(config))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
