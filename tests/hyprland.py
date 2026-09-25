"""Check the Hyprland starter without launching a desktop or applications."""

import json
import shlex
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

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
                              capture_output=True, text=True, timeout=30, check=False)

    def dump_config(self, data):
        result = self.run_command(
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--cache", str(self.root / "chezmoi-cache"),
            "--persistent-state", str(self.root / "chezmoi.boltdb"),
            "--skip-secrets", "--override-data", json.dumps(data),
            "dump", "--format=json", str(self.home / ".config"))
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
                            tomllib.loads(entries[".config/hypr/plugins.toml"]["contents"])
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

    @unittest.skipUnless(LUA and CHEZMOI, "lua or chezmoi is not installed")
    def test_monitor_rendering_per_machine(self):
        for machine in (None, "desktop", "laptop"):
            with self.subTest(machine=machine):
                data = {"chezmoi": {"os": "linux"}, "profiles": ["hyprland-noctalia"],
                        "ManagedByNimbus": False, "onePasswordSsh": False}
                if machine is not None:
                    data["Machine"] = machine
                contents = self.dump_config(data)[".config/hypr/conf.d/monitors.lua"]["contents"]
                result = self.run_command(LUA, "-e", "assert(load(io.read('*a')))", input=contents)
                self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(LUA and CHEZMOI, "lua or chezmoi is not installed")
    def test_lua_bindings_and_startup_are_declarative(self):
        # A strict API double checks Lua execution, not Hyprland's native schema.
        config = self.render_config("desktop")
        modules = [str(config.parent / f"conf.d/{name}.lua") for name in MODULES]
        result = self.run_command(LUA, "-", str(config), *modules, input=r'''
local binds, named_bindings, hooks, spawned, environment = {}, {}, {}, {}, {}
local dispatched = {}
local windows, gestures = {}, {}
local active_window
local actions
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
        local key = value.fingers .. ":" .. value.direction .. ":" .. (value.mods or "")
        assert(not gestures[key], "duplicate gesture: " .. key)
        gestures[key] = value.action
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
        named_bindings[options.description] = value
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
actions = assert(package.loaded["./conf.d/window-actions.lua"])
assert(next(environment) == nil, "session environment belongs to UWSM")
assert(#spawned == 0, "loading/reloading must not launch processes")
assert(#dispatched == 0, "loading/reloading must not move the pointer")
-- Exercise native/XWayland class matching without pinning a shortcut or app inventory.
local apps = {
    { "Focus or open ChatGPT", "chatgpt", "chatgpt" },
    { "Focus or open ChatGPT", "Chatgpt", "chatgpt" },
}
for _, app in ipairs(apps) do
    local binding = named_bindings[app[1]]
    windows, spawned, dispatched = {}, {}, {}
    binding()
    assert(#spawned == 1 and #dispatched == 0, "missing app must launch")
    assert(spawned[1] == "uwsm-app -- " .. app[3])
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
-- A fresh installation must keep the keymap usable before HyprPM setup.
spawned, dispatched = {}, {}
named_bindings["Toggle workspace overview on all monitors"]()
assert(#spawned == 1 and #dispatched == 0)
assert(spawned[1]:find("Workspace overview unavailable", 1, true))
local overview_calls = {}
hl.plugin.scrolloverview = {
    -- In a keybind callback the plugin executes directly and returns nothing.
    overview = function(value) table.insert(overview_calls, value) end,
}
spawned, dispatched = {}, {}
named_bindings["Toggle workspace overview on all monitors"]()
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
dispatched = {}
actions.previous_workspace()
assert(#dispatched == 1 and dispatched[1].value.workspace == previous_workspace)

-- Exercise workspace navigation independently of gesture or shortcut preferences.
local workspaces = assert(package.loaded["./conf.d/workspaces.lua"])
for _, step in ipairs({ -1, 1 }) do
    dispatched = {}
    workspaces.step(step, false)
    assert(#dispatched == 1 and dispatched[1].value.workspace == (step == 1 and "r+1" or "r-1"))
end
active_workspace = previous_workspace
dispatched = {}
workspaces.step(-1, false)
assert(#dispatched == 0, "stepping back at the first workspace must not wrap")

-- Regression: scrolling-only bindings used to raise errors in Dwindle.
active_window = { mapped = true, floating = false, fullscreen = 0,
    workspace = active_workspace, layout = { name = "dwindle" } }
windows = { active_window }
for _, callback in ipairs({ actions.column_width, actions.center_column, actions.split,
    function() actions.join("prev") end, function() actions.join("next") end }) do
    dispatched = {}
    callback()
    assert(#dispatched == 0, "unsupported/single-tile action must be ignored")
end
dispatched = {}
actions.maximize()
assert(dispatched[1].name == "fullscreen" and dispatched[1].value.mode == "maximized")
local second = { mapped = true, floating = false, layout = { name = "dwindle" } }
windows[2] = second
dispatched = {}
actions.split()
assert(#dispatched == 1 and dispatched[1].value == "togglesplit")

active_window.layout = { name = "scrolling", column = { width = 0.5, index = 0 } }
active_window.layout.column.windows = { active_window }
second.layout = { name = "scrolling", column = { index = 1 } }
dispatched = {}
actions.split()
actions.join("prev")
assert(#dispatched == 0, "no split action or nonexistent previous column")
actions.join("next")
assert(#dispatched == 1 and dispatched[1].value == "consume_or_expel next")
active_window.layout.column.windows = { active_window, second }
dispatched = {}
actions.join("prev")
assert(dispatched[1].value == "consume_or_expel prev")
for _, floating in ipairs({ true, false }) do
    active_window.floating = floating
    active_window.fullscreen = floating and 0 or 2
    dispatched = {}
    actions.column_width(); actions.center_column(); actions.split(); actions.join("next")
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
local dictation = {}
for _, command in ipairs(spawned) do
    if command:find("voxtype", 1, true) then table.insert(dictation, command) end
end
assert(#dictation == 1, "expected one conditional dictation startup")
print(bluetooth[1])
print("\0")
print(dictation[1])
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        bluetooth_command, dictation_command = result.stdout.split("\0\n")
        bluetooth = self.root / "bluetooth adapters"
        command = bluetooth_command.replace("/sys/class/bluetooth", shlex.quote(str(bluetooth)))
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

        # Dictation starts only with the daemon installed and a model downloaded.
        data_home = self.root / "data home"
        self.env["XDG_DATA_HOME"] = str(data_home)
        models = data_home / "voxtype" / "models"
        voxtype = binaries / "voxtype"
        for stage in ("missing-daemon", "missing-unit", "missing-models", "empty-models", "model"):
            with self.subTest(stage=stage):
                if stage == "missing-unit":
                    voxtype.write_text("#!/bin/sh\nexit 0\n")
                    voxtype.chmod(0o755)
                    self.env["SERVICE_MISSING"] = "1"
                if stage == "missing-models":
                    del self.env["SERVICE_MISSING"]
                if stage == "empty-models":
                    models.mkdir(parents=True)
                if stage == "model":
                    (models / "ggml-small.bin").write_text("fixture")
                result = self.run_command("/bin/sh", "-c", dictation_command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                self.assertEqual(result.stdout,
                                 "systemctl:--user start voxtype.service\n" if stage == "model" else "")
        del self.env["XDG_DATA_HOME"]

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
