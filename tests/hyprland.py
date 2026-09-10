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
MODULES = tuple(sorted(path.stem for path in (CONFIG.parent / "conf.d").glob("*.lua")))
CHEZMOI = shutil.which("chezmoi")
LUA = shutil.which("lua")
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
                        result = self.run_command(
                            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
                            "--config", str(self.root / "chezmoi.toml"),
                            "--cache", str(self.root / "chezmoi-cache"),
                            "--persistent-state", str(self.root / "chezmoi.boltdb"),
                            "--skip-secrets", "--override-data", json.dumps(data),
                            "dump", "--format=json")
                        self.assertEqual(result.returncode, 0, result.stderr)
                        entries = json.loads(result.stdout)
                        targets = {name for name in entries
                                   if name == ".config/hypr" or name.startswith(".config/hypr/")}
                        enabled = platform == "linux" and "hyprland-noctalia" in (profiles or [])
                        expected = {".config/hypr", ".config/hypr/hyprland.lua", ".config/hypr/conf.d"}
                        expected.update(f".config/hypr/conf.d/{name}.lua" for name in MODULES)
                        self.assertEqual(targets, expected if enabled else set())
                        if enabled:
                            self.assertEqual(entries[".config/hypr/hyprland.lua"]["contents"],
                                             CONFIG.read_text())
                            for name in MODULES:
                                self.assertEqual(entries[f".config/hypr/conf.d/{name}.lua"]["contents"],
                                                 (CONFIG.parent / f"conf.d/{name}.lua").read_text())
                        self.assertEqual(".config/noctalia/config.toml" in entries, enabled)

    @unittest.skipUnless(LUA, "lua is not installed")
    def test_lua_bindings_and_startup_are_declarative(self):
        # A strict API double checks Lua execution, not Hyprland's native schema.
        modules = [str(CONFIG.parent / f"conf.d/{name}.lua") for name in MODULES]
        result = self.run_command(LUA, "-", str(CONFIG), *modules, input=r'''
local binds, hooks, spawned, environment = {}, {}, {}, {}
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
        self.env["PATH"] = str(binaries)
        for count in (None, 0, 1, 2):
            with self.subTest(adapters=count):
                if count is not None:
                    bluetooth.mkdir(exist_ok=True)
                if count:
                    (bluetooth / f"hci{count}").symlink_to(binaries, target_is_directory=True)
                result = self.run_command("/bin/sh", "-c", command)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "librepods:--hide\n" if count else "")

        # Adapters are present, but LibrePods is not installed.
        librepods.unlink()
        result = self.run_command("/bin/sh", "-c", command)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    @unittest.skipUnless(HYPRLAND, "Hyprland is not installed; native check needs 0.56+")
    def test_native_config(self):
        result = self.run_command(HYPRLAND, "--verify-config", "--config", str(CONFIG))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
