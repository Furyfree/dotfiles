#!/usr/bin/env python3
"""Check profile wiring and previews without reading the live desktop."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest

REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
class Noctalia(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-noctalia-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.env = {"HOME": str(self.home), "PATH": os.defpath,
                    "XDG_CONFIG_HOME": str(self.home / ".config"),
                    "XDG_STATE_HOME": str(self.root / "state"),
                    "XDG_CACHE_HOME": str(self.root / "cache"),
                    "XDG_DATA_HOME": str(self.root / "data")}

    def chezmoi(self, *args, platform="linux", profiles=None):
        data = {"chezmoi": {"os": platform}, "profiles": ["hyprland-noctalia"] if profiles is None else profiles,
                "onePasswordSsh": False, "ManagedByNimbus": False}
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--cache", str(self.root / "cache/chezmoi"),
            "--persistent-state", str(self.root / "chezmoi.boltdb"),
            "--skip-secrets", "--override-data", json.dumps(data), *args],
            cwd=self.root, env=self.env, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_profile_selection_and_config_ownership(self):
        for platform, profiles, enabled in (
                ("linux", ["hyprland-noctalia"], True),
                ("linux", ["common"], False),
                ("linux", [], False),
                ("linux", ["niri-dms"], False),
                ("darwin", ["hyprland-noctalia"], False),
                ("windows", ["hyprland-noctalia"], False)):
            with self.subTest(platform=platform, profiles=profiles):
                entries = json.loads(self.chezmoi("dump", "--format=json",
                                               platform=platform, profiles=profiles))
                self.assertEqual(".config/noctalia/config.toml" in entries, enabled)
                self.assertEqual(".config/zsh/conf.d/noctalia.zsh" in entries, enabled)
                self.assertEqual(".config/bash/conf.d/noctalia.bash" in entries, enabled)
                self.assertFalse(any(name.startswith((".local/state/noctalia", ".claude/", ".codex/"))
                                     for name in entries))
                if enabled:
                    config = tomllib.loads(entries[".config/noctalia/config.toml"]["contents"])
                    self.assertEqual(set(config), {"theme", "wallpaper"})
                    templates = config["theme"]["templates"]
                    self.assertNotIn("starship", templates["builtin_ids"])
                    self.assertTrue({"neovim", "fastfetch"}.isdisjoint(templates["community_ids"]))
                    self.assertTrue({"brave-origin", "vscode", "discord"} <= set(templates["community_ids"]))
                    self.assertEqual(tomllib.loads(entries[".config/btop/btop.conf"]["contents"])
                                     ["color_theme"], "noctalia")
                    self.assertIn("include noctaliarc", entries[".config/zathura/zathurarc"]["contents"])
                elif platform == "linux":
                    self.assertEqual(tomllib.loads(entries[".config/btop/btop.conf"]["contents"])
                                     ["color_theme"], "TTY")
                    self.assertNotIn("include noctaliarc", entries[".config/zathura/zathurarc"]["contents"])

    def test_previews_and_generated_files_do_not_drift(self):
        # Apply into this disposable home only; no install scripts or live state.
        self.chezmoi("apply", "--exclude=scripts")
        for name in (".config/hypr/noctalia.lua", ".config/btop/themes/noctalia.theme",
                     ".config/ghostty/themes/noctalia", ".config/zathura/noctaliarc",
                     ".config/fzf/themes/noctalia.sh", ".config/zed/themes/noctalia.json"):
            target = self.home / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("generated stand-in\n")
        managed = self.chezmoi("managed")
        self.assertNotIn(".config/btop/themes/noctalia.theme", managed)
        self.assertEqual(self.chezmoi("status", "--exclude=scripts"), "")
        self.assertEqual(self.chezmoi("diff", "--exclude=scripts"), "")
        self.chezmoi("verify", "--exclude=scripts")

    def test_fzf_missing_and_present_palette(self):
        for shell in ("bash", "zsh"):
            binary = shutil.which(shell)
            if not binary:
                continue
            source = REPO / f"home/dot_config/{shell}/conf.d/noctalia.{shell}"
            script = '. "$1"; printf "%s" "${FZF_DEFAULT_OPTS-}"'
            result = subprocess.run([binary, "-c", script, "fixture", str(source)],
                                    cwd=self.root, env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            palette = self.home / ".config/fzf/themes/noctalia.sh"
            palette.parent.mkdir(parents=True, exist_ok=True)
            palette.write_text('export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS-} --color=fg:#abcdef"\n')
            result = subprocess.run([binary, "-c", script, "fixture", str(source)],
                                    cwd=self.root, env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("--color=fg:#abcdef", result.stdout)
            palette.unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
