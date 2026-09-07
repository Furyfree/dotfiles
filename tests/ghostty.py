#!/usr/bin/env python3
"""Read-only Ghostty validation with an isolated home and rendered config."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "home/dot_config/ghostty"
CHEZMOI = shutil.which("chezmoi")
GHOSTTY = shutil.which("ghostty")


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
class Ghostty(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-ghostty-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.config_dir = self.home / ".config/ghostty"
        self.config_dir.mkdir(parents=True)
        self.env = {
            "HOME": str(self.home), "PATH": "/usr/bin:/bin", "LANG": "C.UTF-8",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
        }

    def run_command(self, *args, input=None):
        result = subprocess.run(args, input=input, cwd=self.root, env=self.env,
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotRegex(result.stderr.lower(), r"error|unknown|invalid|not found")
        return result.stdout

    def chezmoi(self, platform, *args, input=None, noctalia=False, managed=False, legacy=False):
        data = {"chezmoi": {"os": platform}, "onePasswordSsh": False}
        if not legacy:
            data.update({"profiles": ["common", "hyprland-noctalia"] if noctalia else ["common"],
                         "ManagedByNimbus": managed})
        return self.run_command(
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.home / "chezmoi.toml"), "--cache", str(self.root / "cache/chezmoi"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"), "--skip-secrets",
            "--override-data", json.dumps(data),
            *args, input=input)

    def render(self, platform, noctalia=False):
        content = self.chezmoi(platform, "execute-template", noctalia=noctalia,
                               input=(SOURCE / "config.tmpl").read_text())
        (self.config_dir / "config").write_text(content)
        shutil.copytree(SOURCE / "themes", self.config_dir / "themes", dirs_exist_ok=True)
        if noctalia:
            # Stand-in for Noctalia's output, never a managed source or live file.
            (self.config_dir / "themes/noctalia").write_text(
                "background = #102030\nforeground = #ddeeff\npalette = 6=#123456\n")
        return content

    def test_platform_targets(self):
        targets = {".config/ghostty/config", ".config/ghostty/themes/charcoal-blue"}
        for platform in ("linux", "darwin", "windows"):
            with self.subTest(platform=platform):
                entries = json.loads(self.chezmoi(platform, "dump", "--format=json"))
                files = {name for name, entry in entries.items()
                         if name.startswith(".config/ghostty/") and entry["type"] == "file"}
                self.assertEqual(files, targets if platform != "windows" else set())

    def test_noctalia_profile_and_ownership(self):
        for platform in ("linux", "darwin", "windows"):
            for noctalia in (False, True):
                for managed in (False, True):
                    with self.subTest(platform=platform, noctalia=noctalia, managed=managed):
                        entries = json.loads(self.chezmoi(platform, "dump", "--format=json",
                                                          noctalia=noctalia, managed=managed))
                        enabled = platform == "linux" and noctalia
                        files = {name for name, entry in entries.items() if entry["type"] == "file"}
                        self.assertFalse(any(name.startswith(".config/noctalia/") for name in files))
                        self.assertNotIn(".config/ghostty/themes/noctalia", files)
                        self.assertNotIn(".config/noctalia/config.toml", files)
                        self.assertNotIn(".config/noctalia/settings.toml", files)
                        if platform != "windows":
                            config = entries[".config/ghostty/config"]["contents"]
                            expected = "noctalia" if enabled else "charcoal-blue"
                            themes = [line for line in config.splitlines() if line.startswith("theme =")]
                            self.assertEqual(themes, [f"theme = {expected}"])

    def test_legacy_data_without_profiles(self):
        entries = json.loads(self.chezmoi("linux", "dump", "--format=json", legacy=True))
        self.assertIn("theme = charcoal-blue", entries[".config/ghostty/config"]["contents"].splitlines())
        self.assertNotIn(".config/noctalia/templates.toml", entries)

    def test_platform_settings_and_no_external_includes(self):
        for platform in ("linux", "darwin"):
            with self.subTest(platform=platform):
                content = self.render(platform)
                self.assertNotIn("config-file", content)
                self.assertNotIn("keybind", content)
                self.assertEqual("gtk-toolbar-style" in content, platform == "linux")
                self.assertEqual("macos-option-as-alt" in content, platform == "darwin")
                theme = next(line.partition("=")[2].strip() for line in content.splitlines()
                             if line.startswith("theme ="))
                self.assertTrue((self.config_dir / "themes" / theme).is_file())

    @unittest.skipUnless(GHOSTTY, "ghostty is not installed")
    def test_native_parser_and_protections(self):
        for platform in ("linux", "darwin"):
            with self.subTest(platform=platform):
                self.render(platform)
                self.run_command(GHOSTTY, "+validate-config", f"--config-file={self.config_dir / 'config'}")
                effective = self.run_command(GHOSTTY, "+show-config", "--changes-only=false")
                # Ensure we inspected the rendered file, not an unnoticed fallback to defaults.
                configured = (self.config_dir / "config").read_text().splitlines()
                theme_line = next(line for line in configured if line.startswith("theme ="))
                self.assertIn(theme_line, effective.splitlines())
                self.assertIn("confirm-close-surface = true", effective)
                self.assertIn("clipboard-paste-protection = true", effective)
                self.assertIn("no-ssh-terminfo", effective)

    @unittest.skipUnless(GHOSTTY, "ghostty is not installed")
    def test_native_keymap_unchanged(self):
        defaults = self.run_command(GHOSTTY, "+list-keybinds", "--default")
        for platform in ("linux", "darwin"):
            with self.subTest(platform=platform):
                self.render(platform)
                actual = self.run_command(GHOSTTY, "+list-keybinds")
                self.assertEqual(actual.splitlines(), defaults.splitlines())

    @unittest.skipUnless(GHOSTTY, "ghostty is not installed")
    def test_native_generated_theme_changes(self):
        content = self.render("linux", noctalia=True)
        defaults = self.run_command(GHOSTTY, "+list-keybinds", "--default")
        self.assertEqual(self.run_command(GHOSTTY, "+list-keybinds").splitlines(), defaults.splitlines())
        for foreground, cyan in (("#ddeeff", "#123456"), ("#112233", "#abcdef")):
            with self.subTest(foreground=foreground):
                (self.config_dir / "themes/noctalia").write_text(
                    f"background = #102030\nforeground = {foreground}\npalette = 6={cyan}\n")
                self.run_command(GHOSTTY, "+validate-config", f"--config-file={self.config_dir / 'config'}")
                effective = self.run_command(GHOSTTY, "+show-config", "--changes-only=false")
                self.assertIn("theme = noctalia", effective.splitlines())
                self.assertIn(f"foreground = {foreground}", effective.splitlines())
                self.assertIn(f"palette = 6={cyan}", effective.splitlines())
                self.assertIn("clipboard-paste-protection = true", effective)
                self.assertEqual((self.config_dir / "config").read_text(), content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
