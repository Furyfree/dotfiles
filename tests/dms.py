"""DMS preferences and ownership checks; never starts the live shell."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "home/dot_config/DankMaterialShell/settings.json"
CHEZMOI = shutil.which("chezmoi")


class Dms(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads(SOURCE.read_text())

    def test_lock_before_suspend(self):
        settings = self.settings
        self.assertFalse(settings["notificationHistoryEnabled"])
        self.assertFalse(settings["clipboardEnterToPaste"])
        self.assertFalse(settings["clipboardClickToPaste"])
        self.assertTrue(settings["lockBeforeSuspend"])
        for power in ("ac", "battery"):
            self.assertGreater(settings[f"{power}LockTimeout"], 0)
            self.assertLess(settings[f"{power}LockTimeout"], settings[f"{power}MonitorTimeout"])
            self.assertLess(settings[f"{power}MonitorTimeout"], settings[f"{power}SuspendTimeout"])

    def test_bar_widgets_are_unique_and_leave_updates_to_nimbus(self):
        for bar in self.settings["barConfigs"]:
            widgets = bar["leftWidgets"] + bar["centerWidgets"] + bar["rightWidgets"]
            self.assertEqual(len(widgets), len(set(widgets)))
            self.assertNotIn("systemUpdate", widgets)

    def test_only_niri_palette_generation(self):
        settings = self.settings
        self.assertTrue(settings["runDmsMatugenTemplates"])
        self.assertFalse(settings["runUserMatugenTemplates"])
        # DMS 1.6.0 defaults most integrations to true: explicitly turn them off.
        integrations = {
            "Gtk", "Niri", "Hyprland", "Mangowc", "Qt5ct", "Qt6ct", "Fcitx5", "Qtengine",
            "Firefox", "Pywalfox", "ZenBrowser", "Vesktop", "Vencord", "Equibop", "Ghostty",
            "Kitty", "Foot", "Alacritty", "Neovim", "Wezterm", "Dgop", "Kcolorscheme",
            "Vscode", "Emacs", "Zed",
        }
        for integration in integrations:
            self.assertIs(settings[f"matugenTemplate{integration}"], integration == "Niri")

    def test_no_private_runtime_or_stale_settings(self):
        self.assertFalse(self.settings["weatherEnabled"])
        self.assertFalse(self.settings["useAutoLocation"])
        forbidden = (
            "History", "Pins", "OutputSettings", "Profile", "Wallpaper", "Location", "Gpu",
            "plugin", "Plugin", "Command", "cursor", "keyboard", "touchpad", "niriLayout",
        )
        allowed = {"notificationHistoryEnabled", "useAutoLocation"}
        for key in self.settings:
            if key not in allowed:
                self.assertFalse(any(part in key for part in forbidden), key)
        self.assertNotIn("use24HourClock", self.settings)
        self.assertNotIn("gtkThemingEnabled", self.settings)
        self.assertNotIn("qtThemingEnabled", self.settings)
        self.assertNotIn("spotlightCloseNiriOverview", self.settings)
        self.assertNotIn("/home/", SOURCE.read_text())

    @unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
    def test_profile_gate_and_runtime_ownership(self):
        with tempfile.TemporaryDirectory(prefix="dotfiles-dms-") as temp:
            root = Path(temp)
            home = root / "home with spaces"
            home.mkdir()
            env = {"HOME": str(home), "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8",
                   "XDG_CONFIG_HOME": str(home / ".config"), "XDG_CACHE_HOME": str(root / "cache"),
                   "XDG_DATA_HOME": str(root / "data"), "XDG_STATE_HOME": str(root / "state")}
            for platform in ("linux", "darwin", "windows"):
                for profile in (None, "niri-dms", "hyprland-noctalia", "hyprland-dms", "niri-noctalia"):
                    for managed in (False, True):
                        with self.subTest(platform=platform, profile=profile, managed=managed):
                            data = {"chezmoi": {"os": platform}, "onePasswordSsh": False,
                                    "ManagedByNimbus": managed}
                            if profile:
                                data["profiles"] = ["common", profile]
                            result = subprocess.run(
                                [CHEZMOI, "--source", str(REPO), "--destination", str(home),
                                 "--config", str(root / "chezmoi.toml"), "--cache", str(root / "cache"),
                                 "--persistent-state", str(root / "state.boltdb"), "--skip-secrets",
                                 "--override-data", json.dumps(data), "dump", "--format=json", str(home / ".config")],
                                cwd=root, env=env, text=True, capture_output=True, timeout=20, check=False)
                            self.assertEqual(result.returncode, 0, result.stderr)
                            entries = json.loads(result.stdout)
                            targets = {name for name, entry in entries.items()
                                       if name.startswith(".config/DankMaterialShell/")
                                       and entry["type"] == "file"}
                            enabled = platform == "linux" and profile == "niri-dms"
                            self.assertEqual(targets, {".config/DankMaterialShell/settings.json"}
                                             if enabled else set())
                            if enabled:
                                self.assertEqual(json.loads(entries[
                                    ".config/DankMaterialShell/settings.json"]["contents"]), self.settings)


if __name__ == "__main__":
    unittest.main(verbosity=2)
