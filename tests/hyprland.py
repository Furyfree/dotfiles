#!/usr/bin/env python3
"""Check the Hyprland starter without launching a desktop or applications."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "home/dot_config/hypr/hyprland.lua"
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
                        self.assertEqual(targets, {".config/hypr", ".config/hypr/hyprland.lua"}
                                         if enabled else set())
                        if enabled:
                            self.assertEqual(entries[".config/hypr/hyprland.lua"]["contents"],
                                             CONFIG.read_text())
                        self.assertEqual(".config/noctalia/config.toml" in entries, enabled)

    @unittest.skipUnless(LUA, "lua is not installed")
    def test_lua_bindings_and_startup_are_declarative(self):
        # A strict API double checks Lua execution, not Hyprland's native schema.
        result = self.run_command(LUA, "-", str(CONFIG), input=r'''
local binds, hooks, spawned, environment = {}, {}, {}, {}
local function action(name)
    return function(value) return { name = name, value = value } end
end
hl = {
    env = function(key, value) environment[key] = value end,
    monitor = function(value) assert(value.output == "" and value.mode == "preferred") end,
    config = function(value) assert(value.general.layout == "dwindle") end,
    on = function(event, callback)
        assert(event == "hyprland.start" and not hooks[event])
        hooks[event] = callback
    end,
    exec_cmd = function(command) table.insert(spawned, command) end,
    bind = function(key, value, options)
        assert(not binds[key], "duplicate shortcut: " .. key)
        assert(options and type(options.description) == "string" and #options.description > 0,
               "missing description: " .. key)
        binds[key] = value
        if key:find("mouse:") then assert(options.mouse) end
    end,
    dsp = {
        exec_cmd = action("exec"), focus = action("focus"), layout = action("layout"),
        window = {
            close = action("close"), float = action("float"), pseudo = action("pseudo"),
            move = action("move"), drag = action("drag"), resize = action("resize"),
        },
    },
}
assert(loadfile(arg[1]))()
assert(environment.PATH:find("/usr/bin", 1, true))
assert(environment.QT_QPA_PLATFORMTHEME == "qt5ct")
assert(#spawned == 0, "loading/reloading must not launch processes")
assert(binds["SUPER + Q"].value == "ghostty")
assert(binds["SUPER + B"].value == "brave-origin")
assert(binds["SUPER + E"].value == "nautilus")
assert(binds["SUPER + R"].value == "noctalia msg panel-toggle launcher")
assert(binds["SUPER + C"].name == "close")
assert(binds["SUPER + M"].value == "noctalia msg panel-toggle session")
for i = 1, 10 do
    local key = tostring(i % 10)
    assert(binds["SUPER + " .. key].value.workspace == i)
    assert(binds["SUPER + SHIFT + " .. key].value.workspace == i)
end
hooks["hyprland.start"]()
assert(#spawned == 2 and spawned[1] == "noctalia --daemon")
assert(spawned[2] == "librepods --hide")
''')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(HYPRLAND, "Hyprland is not installed; native check needs 0.55+")
    def test_native_config(self):
        result = self.run_command(HYPRLAND, "--verify-config", "--config", str(CONFIG))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
