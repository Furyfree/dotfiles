#!/usr/bin/env python3
"""Validate the shared Fastfetch config without loading live app configuration."""

import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "home/dot_config/fastfetch/config.jsonc"
FASTFETCH = shutil.which("fastfetch")
CHEZMOI = shutil.which("chezmoi")


class Fastfetch(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-fastfetch-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.env = {
            "HOME": str(self.home), "USERPROFILE": str(self.home), "PATH": "",
            "LANG": "C.UTF-8", "NO_COLOR": "1",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_CONFIG_DIRS": str(self.root / "system-config"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
        }
        self.config = json.loads(CONFIG.read_text())

    def run_command(self, *args):
        result = subprocess.run(args, cwd=self.root, env=self.env, stdin=subprocess.DEVNULL,
                                text=True, capture_output=True, timeout=30)
        # Do not print detected hardware or filesystem information on failure.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotRegex(result.stderr.lower(), r"error|unknown|invalid")
        return result.stdout

    def test_static_config_safety(self):
        # Keep smoke tests free of command execution, network requests, and image helpers.
        safe_modules = {"custom", "break", "cpu", "gpu", "memory", "disk", "display",
                        "battery", "os", "kernel", "wm", "de", "shell", "terminal",
                        "packages", "uptime", "colors", "separator", "swap"}
        for module in self.config["modules"]:
            name = module if isinstance(module, str) else module["type"]
            self.assertIn(name.lower(), safe_modules)
        self.assertIn(self.config["logo"]["type"], ("small", "builtin", "auto", "none"))
        self.assertNotIn("source", self.config["logo"])

    def test_terminal_theme_inheritance(self):
        self.assertEqual(self.config["logo"]["color"],
                         {str(slot): "default" for slot in range(1, 10)})
        self.assertEqual(self.config["display"]["color"], {"keys": "default"})
        for module in self.config["modules"]:
            if isinstance(module, dict):
                self.assertNotIn("keyColor", module)
                self.assertNotIn("outputColor", module)

    @unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
    def test_platform_targets(self):
        for platform in ("linux", "darwin", "windows"):
            with self.subTest(platform=platform):
                output = self.run_command(
                    CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
                    "--config", str(self.root / "chezmoi.toml"), "--cache", str(self.root / "cache/chezmoi"),
                    "--persistent-state", str(self.root / "chezmoi-state.boltdb"), "--skip-secrets",
                    "--override-data", json.dumps({"chezmoi": {"os": platform},
                                                   "profiles": ["common"], "onePasswordSsh": False}),
                    "dump", "--format=json")
                files = {name: entry["contents"] for name, entry in json.loads(output).items()
                         if name.startswith(".config/fastfetch/") and entry["type"] == "file"}
                self.assertEqual(files, {".config/fastfetch/config.jsonc": CONFIG.read_text()})

    @unittest.skipUnless(FASTFETCH, "fastfetch is not installed")
    def test_native_output(self):
        self.test_static_config_safety()
        output = self.run_command(FASTFETCH, "--config", str(CONFIG), "--format", "json")
        modules = json.loads(output)
        expected = [(module if isinstance(module, str) else module["type"]).lower()
                    for module in self.config["modules"]]
        self.assertEqual([module["type"].lower() for module in modules], expected)
        # Optional hardware/session modules may be unavailable in headless environments.
        self.assertTrue(any("result" in module for module in modules))

    @unittest.skipUnless(FASTFETCH, "fastfetch is not installed")
    def test_colored_logos_use_terminal_foreground(self):
        del self.env["NO_COLOR"]
        for logo in ("mac", "windows", "arch"):
            with self.subTest(logo=logo):
                # A break-only structure renders logos without detecting hardware.
                output = self.run_command(
                    FASTFETCH, "--config", str(CONFIG), "--pipe", "false",
                    "--structure", "break", "--logo-type", self.config["logo"]["type"],
                    "--logo", logo)
                controls = re.findall(r"\x1b\[([0-9;:]*)m", output)
                self.assertTrue(controls, "color output must be enabled for this check")
                codes = {int(code or "0") for control in controls
                         for code in re.split(r"[;:]", control)}
                self.assertIn(39, codes, "the logo must select the terminal foreground")
                self.assertTrue(codes <= {0, 1, 22, 39},
                                f"unexpected styling in {logo} logo: {sorted(codes)}")

    @unittest.skipUnless(FASTFETCH, "fastfetch is not installed")
    def test_plain_output(self):
        self.test_static_config_safety()
        output = self.run_command(FASTFETCH, "--config", str(CONFIG), "--pipe", "true")
        self.assertTrue(output.strip())
        self.assertFalse("\x1b[" in output, "plain output should not contain terminal cursor/color controls")
        for module in self.config["modules"]:
            if isinstance(module, dict) and module["type"] == "custom":
                self.assertIn(module["format"], output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
