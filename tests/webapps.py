#!/usr/bin/env python3
"""Validate prepared webapps without launching browsers or using live state."""

import configparser
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
ENTRIES = REPO / "home/dot_local/share/applications"
ICONS = REPO / "home/dot_local/share/icons/hicolor/512x512/apps"
APPS = {
    "GoogleMaps": ("Google Maps", "https://www.google.com/maps", "google-maps"),
    "FotMob": ("FotMob", "https://www.fotmob.com/", "fotmob"),
}
CHEZMOI = shutil.which("chezmoi")
VALIDATOR = shutil.which("desktop-file-validate")


class Webapps(unittest.TestCase):
    def test_entries_and_icons(self):
        self.assertEqual({path.stem for path in ENTRIES.glob("*.desktop")}, set(APPS))
        expected_icons = set()
        for stem, (name, url, icon) in APPS.items():
            with self.subTest(app=stem):
                config = configparser.ConfigParser(interpolation=None)
                config.optionxform = str
                config.read(ENTRIES / f"{stem}.desktop")
                self.assertEqual(config.sections(), ["Desktop Entry"])
                entry = config["Desktop Entry"]
                self.assertEqual(set(entry), {"Type", "Name", "Comment", "Exec", "TryExec",
                                              "Icon", "Terminal", "Categories", "Keywords"})
                self.assertEqual(entry["Type"], "Application")
                self.assertEqual(entry["Name"], name)
                self.assertEqual(entry["Exec"], f"nimbus launch webapp {url}")
                self.assertEqual(entry["TryExec"], "nimbus")
                self.assertEqual(entry["Terminal"], "false")
                self.assertEqual(entry["Icon"], f"nimbus-webapp-{icon}")
                self.assertTrue(entry["Keywords"].endswith(";"))
                self.assertTrue(entry["Categories"].endswith(";"))
                filename = entry["Icon"] + ".png"
                expected_icons.add(filename)
                data = (ICONS / filename).read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(data[12:16], b"IHDR")
                self.assertEqual(struct.unpack(">II", data[16:24]), (512, 512))
                self.assertLess(len(data), 100_000)
        self.assertEqual({path.name for path in ICONS.iterdir()}, expected_icons)

    @unittest.skipUnless(VALIDATOR, "desktop-file-validate is not installed")
    def test_native_desktop_syntax(self):
        result = subprocess.run([VALIDATOR, *(str(ENTRIES / f"{stem}.desktop") for stem in APPS)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout + result.stderr, "")

    @unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
    def test_deferred_and_future_platform_gates(self):
        with tempfile.TemporaryDirectory(prefix="dotfiles-webapps-") as temp:
            root = Path(temp)
            source = root / "source"
            shutil.copytree(REPO / "home", source)
            home = root / "home with spaces"
            home.mkdir()
            env = {"HOME": str(home), "USERPROFILE": str(home), "PATH": "",
                   "XDG_CONFIG_HOME": str(root / "config"), "XDG_DATA_HOME": str(root / "data"),
                   "XDG_CACHE_HOME": str(root / "cache"), "XDG_STATE_HOME": str(root / "state")}
            ignore = source / ".chezmoiignore"
            original = ignore.read_text()
            marker = "# Webapps are prepared but disabled until Nimbus's launch helper is tested.\n"
            before, found, rest = original.partition(marker)
            self.assertTrue(found)
            block, separator, after = rest.partition("\n\n")
            self.assertTrue(separator)
            self.assertEqual(len([line for line in block.splitlines() if not line.startswith("#")]), 5)
            expected = {f".local/share/applications/{stem}.desktop" for stem in APPS}
            expected.update(f".local/share/icons/hicolor/512x512/apps/nimbus-webapp-{icon}.png"
                            for _, _, icon in APPS.values())
            expected_targets = expected | {str(parent) for name in expected
                                           for parent in Path(name).parents if str(parent) != "."}
            for enabled in (False, True):
                # Only the disposable copy loses the temporary ignore block.
                ignore.write_text(before + after if enabled else original)
                for platform in ("linux", "darwin", "windows"):
                    for managed in (None, False, True):
                        with self.subTest(enabled=enabled, platform=platform, managed=managed):
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
                            targets = {name for name in entries
                                       if name == ".local" or name.startswith(".local/")}
                            available = enabled and platform == "linux" and managed is True
                            self.assertEqual(targets, expected_targets if available else set())
                            files = {name for name, entry in entries.items() if entry["type"] == "file"
                                     and name.startswith((".local/share/applications/", ".local/share/icons/"))}
                            self.assertEqual(files, expected if available else set())
                            for stem in APPS:
                                target = f".local/share/applications/{stem}.desktop"
                                if target in files:
                                    self.assertEqual(entries[target]["contents"], (ENTRIES / f"{stem}.desktop").read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
