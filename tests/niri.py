#!/usr/bin/env python3
"""Check modular Niri configuration without contacting a compositor session."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "home/dot_config/niri"
CHEZMOI = shutil.which("chezmoi")
NIRI = shutil.which("niri")
SH = shutil.which("sh")


class Niri(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-niri-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.env = {
            "HOME": str(self.home), "USERPROFILE": str(self.home), "PATH": "",
            "LANG": "C.UTF-8", "NO_COLOR": "1",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_CONFIG_DIRS": str(self.root / "system-config"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_STATE_HOME": str(self.root / "state"),
            "XDG_RUNTIME_DIR": str(self.root / "runtime"),
        }
        self.files = {path.name: path.read_text() for path in SOURCE.glob("*.kdl")}

    def run_command(self, *args):
        return subprocess.run(args, cwd=self.root, env=self.env,
                              stdin=subprocess.DEVNULL, text=True,
                              capture_output=True, timeout=30)

    def test_explicit_modules_and_ownership(self):
        expected = {"input.kdl", "outputs.kdl", "layout.kdl", "rules.kdl",
                    "autostart.kdl", "shell.kdl", "keybinds.kdl"}
        includes = re.findall(r'^include "([^"]+)"$', self.files["config.kdl"], re.M)
        self.assertEqual(set(includes), expected)
        self.assertEqual(len(includes), len(expected))
        self.assertEqual(set(self.files), expected | {"config.kdl"})
        generated = re.findall(r'^include optional=true "([^"]+)"$',
                               self.files["shell.kdl"], re.M)
        self.assertEqual(generated, ["dms/colors.kdl"])
        source = "\n".join(self.files.values())
        self.assertNotRegex(source, r"nirius|niriland-|\.local/share/niriland|/home/[^/]+/")
        self.assertNotIn("honor-xdg-activation-with-invalid-serial", source)
        self.assertNotRegex(self.files["outputs.kdl"], r'(?m)^output\s')
        self.assertEqual(re.findall(r'^spawn-at-startup .+$', source, re.M),
                         ['spawn-at-startup "dms" "run"'])
        self.assertFalse((SOURCE / "dms").exists(), "Generated DMS files stay unmanaged")

    def test_keybinds_are_unique_and_native(self):
        source = self.files["keybinds.kdl"]
        keys = re.findall(r'^\s+([A-Za-z0-9_+]+)(?:\s+[^{}]*)?\s*\{', source, re.M)
        keys = [key for key in keys if key != "binds"]
        self.assertEqual(len(keys), len(set(keys)), "Duplicate key combinations")
        self.assertNotRegex(source, r"WheelScroll|Mod\+[UI] \{|XF86Launch1|Ctrl\+Alt\+Delete")
        self.assertIn('Mod+L repeat=false hotkey-overlay-title="Lock"', source)
        self.assertIn('Mod+Shift+Page_Up { move-column-to-workspace-up; }', source)
        self.assertIn('Alt+Tab { next-window scope="output"; }', source)
        for line in source.splitlines():
            if "allow-when-locked=true" in line:
                self.assertRegex(line.strip(), r"^XF86(Audio|MonBrightness)")
        actions = re.findall(r'\{ ([a-z][a-z-]*(?: "[^"]*"| \d+)?); \}', source)
        self.assertEqual(len(actions), len(set(actions)), "Duplicate native actions")
        self.assertNotIn("skip-confirmation", source)

    @unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
    def test_platform_profile_targets(self):
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
                        targets = {name: entry["contents"]
                                   for name, entry in json.loads(result.stdout).items()
                                   if name.startswith(".config/niri/") and entry["type"] == "file"}
                        expected = {".config/niri/" + name: content
                                    for name, content in self.files.items()}
                        enabled = platform == "linux" and "niri-dms" in (profiles or [])
                        self.assertEqual(targets, expected if enabled else {})

    @unittest.skipUnless(NIRI, "niri is not installed; native parsing needs Niri 26.04+")
    def test_native_optional_palette(self):
        config = self.home / ".config/niri"
        shutil.copytree(SOURCE, config)
        result = self.run_command(NIRI, "validate", "--config", str(config / "config.kdl"))
        self.assertEqual(result.returncode, 0, result.stderr)
        generated = config / "dms/colors.kdl"
        generated.parent.mkdir()
        generated.write_text('layout { focus-ring { active-color "#aaccee"; }; }\n')
        result = self.run_command(NIRI, "validate", "--config", str(config / "config.kdl"))
        self.assertEqual(result.returncode, 0, result.stderr)
        # Optional means absent is safe, not that invalid generated content is ignored.
        generated.write_text('layout { definitely-not-a-niri-setting; }\n')
        result = self.run_command(NIRI, "validate", "--config", str(config / "config.kdl"))
        self.assertNotEqual(result.returncode, 0)

    @unittest.skipUnless(SH, "sh is not installed")
    def test_default_browser_and_files_launch_without_shell_aliases(self):
        binaries = self.root / "bin"
        binaries.mkdir()
        self.env["PATH"] = str(binaries)
        fixtures = {
            "xdg-settings": '#!/bin/sh\nprintf "%s" "$TEST_BROWSER"\nexit "${TEST_EXIT:-0}"\n',
            "gtk-launch": '#!/bin/sh\nprintf "launched:%s\\n" "$@"\n',
            "xdg-open": '#!/bin/sh\nprintf "opened:%s\\n" "$@"\n',
        }
        for name, content in fixtures.items():
            target = binaries / name
            target.write_text(content)
            target.chmod(0o755)
        browser = re.search(r'spawn-sh r#"(.+)"#;', self.files["keybinds.kdl"]).group(1)
        self.env["TEST_BROWSER"] = "browser with spaces.desktop"
        result = self.run_command(SH, "-c", browser)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "launched:browser with spaces.desktop\n")
        self.env["TEST_BROWSER"] = ""
        result = self.run_command(SH, "-c", browser)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.env["TEST_BROWSER"] = "browser.desktop"
        self.env["TEST_EXIT"] = "1"
        result = self.run_command(SH, "-c", browser)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        files = re.search(r'spawn-sh ("(?:[^"\\]|\\.)*");',
                          self.files["keybinds.kdl"]).group(1)
        result = self.run_command(SH, "-c", json.loads(files))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "opened:" + str(self.home) + "\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
