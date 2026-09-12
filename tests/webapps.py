#!/usr/bin/env python3
"""Validate desktop entries and webapps without launching applications."""

import configparser
import json
from pathlib import Path
import shlex
import shutil
import struct
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit


REPO = Path(__file__).resolve().parents[1]
ENTRIES = REPO / "home/dot_local/share/applications"
ICONS = REPO / "home/dot_local/share/icons/hicolor/512x512/apps"
APPS = ("FotMob", "GoogleMaps")
CHEZMOI = shutil.which("chezmoi")
VALIDATOR = shutil.which("desktop-file-validate")


class Webapps(unittest.TestCase):
    def test_entries_and_icons(self):
        for stem in APPS:
            with self.subTest(app=stem):
                config = configparser.ConfigParser(interpolation=None)
                config.optionxform = str
                config.read(ENTRIES / f"{stem}.desktop")
                entry = config["Desktop Entry"]
                self.assertEqual(entry["Type"], "Application")
                self.assertTrue(entry["Name"].strip())
                command = shlex.split(entry["Exec"])
                self.assertEqual(command[:3], ["nimbus", "launch", "webapp"])
                self.assertEqual(len(command), 4)
                url = urlsplit(command[3])
                self.assertIn(url.scheme, ("http", "https"))
                self.assertTrue(url.hostname)
                self.assertEqual(entry["TryExec"], "nimbus")
                self.assertEqual(entry["Terminal"], "false")
                filename = entry["Icon"] + ".png"
                self.assertEqual(Path(filename).name, filename)
                data = (ICONS / filename).read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(data[12:16], b"IHDR")
                self.assertTrue(all(size > 0 for size in struct.unpack(">II", data[16:24])))

    @unittest.skipUnless(VALIDATOR, "desktop-file-validate is not installed")
    def test_native_desktop_syntax(self):
        if not APPS:
            self.skipTest("no webapps are declared")
        result = subprocess.run([VALIDATOR, "--no-hints",
                                 *(str(path) for path in sorted(ENTRIES.glob("*.desktop")))],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout + result.stderr, "")

    @unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
    def test_platform_gates_preserve_unrelated_local_targets(self):
        with tempfile.TemporaryDirectory(prefix="dotfiles-webapps-") as temp:
            root = Path(temp)
            source = root / "source"
            shutil.copytree(REPO / "home", source)
            shutil.copy2(REPO / "VSCODIUM_EXTENSIONS.json", root)
            # A normal Linux user file must not inherit the Nimbus webapp gate.
            fixture = source / "dot_local/bin/fixture-tool"
            fixture.parent.mkdir(parents=True)
            fixture.write_text("#!/bin/sh\nexit 0\n")
            home = root / "home with spaces"
            home.mkdir()
            env = {"HOME": str(home), "USERPROFILE": str(home), "PATH": "",
                   "XDG_CONFIG_HOME": str(root / "config"), "XDG_DATA_HOME": str(root / "data"),
                   "XDG_CACHE_HOME": str(root / "cache"), "XDG_STATE_HOME": str(root / "state")}
            for platform in ("linux", "darwin", "windows"):
                for managed in (None, False, True):
                    with self.subTest(platform=platform, managed=managed):
                        data = {"chezmoi": {"os": platform}, "onePasswordSsh": False,
                                "profiles": ["common"]}
                        if managed is not None:
                            data["ManagedByNimbus"] = managed
                        result = subprocess.run([
                            CHEZMOI, "--source", str(source), "--destination", str(home),
                            "--config", str(root / "chezmoi.toml"),
                            "--cache", str(root / "cache/chezmoi"),
                            "--persistent-state", str(root / "chezmoi-state.boltdb"),
                            "--skip-secrets", "--override-data", json.dumps(data),
                            "dump", "--format=json",
                        ], env=env, cwd=root, capture_output=True, text=True, timeout=20)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        entries = json.loads(result.stdout)
                        self.assertEqual(".local/bin/fixture-tool" in entries, platform == "linux")
                        if platform == "linux":
                            self.assertEqual(entries[".local/bin/fixture-tool"]["contents"],
                                             fixture.read_text())
                        self.assertFalse(any(name.endswith(".keep") for name in entries))
                        self.assertNotIn(".local/share/backgrounds", entries)
                        enabled = platform == "linux" and managed is True
                        targets = [f".local/share/applications/{stem}.desktop" for stem in APPS]
                        targets += [f".local/share/icons/hicolor/512x512/apps/{path.name}"
                                    for path in ICONS.glob("nimbus-webapp-*.png")]
                        for target in targets:
                            self.assertEqual(target in entries, enabled, target)


if __name__ == "__main__":
    unittest.main(verbosity=2)
