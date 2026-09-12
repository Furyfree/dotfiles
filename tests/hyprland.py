#!/usr/bin/env python3
"""Check the Hyprland starter without launching a desktop or applications."""

import json
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
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
                        expected = {".config/hypr", ".config/hypr/hyprland.lua", ".config/hypr/conf.d"}
                        expected.update(f".config/hypr/conf.d/{name}.lua" for name in MODULES)
                        self.assertEqual(targets, expected if enabled else set())
                        if enabled:
                            self.assertEqual(entries[".config/hypr/hyprland.lua"]["contents"],
                                             CONFIG.read_text())
                            for name, source in MODULES.items():
                                if source.suffix != ".tmpl":
                                    self.assertEqual(entries[f".config/hypr/conf.d/{name}.lua"]["contents"],
                                                     source.read_text())
                        self.assertEqual(".config/noctalia/config.toml" in entries, enabled)

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
local windows = {}
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
        assert(type(value.direction) == "string" and type(value.action) == "string")
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
assert(environment.PATH and #environment.PATH > 0, "session PATH is empty")
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
        assert(spawned[1] == app[3])
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
    assert(binds[key].name == "exec" and binds[key].value == command,
           "native launch/activation must be preserved: " .. key)
end
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

    @unittest.skipUnless(HYPRLAND and CHEZMOI, "Hyprland or chezmoi is not installed; native check needs 0.56+")
    def test_native_config(self):
        for machine in ("desktop", "laptop"):
            with self.subTest(machine=machine):
                config = self.render_config(machine)
                result = self.run_command(HYPRLAND, "--verify-config", "--config", str(config))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
