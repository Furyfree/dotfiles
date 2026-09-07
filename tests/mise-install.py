#!/usr/bin/env python3
"""Exercise the apply lifecycle in a tiny temporary source with a fake Mise."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = "run_after_install-mise-tools.sh.tmpl"
CHEZMOI = shutil.which("chezmoi")
MISE = shutil.which("mise")


@unittest.skipUnless(CHEZMOI, "chezmoi is required")
class MiseInstall(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-mise-install-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.source = self.root / "source"
        self.home.mkdir()
        self.source.mkdir()
        self.path_bin = self.root / "bin"
        self.path_bin.mkdir()
        self.env = {
            "HOME": str(self.home), "PATH": str(self.path_bin), "LANG": "C.UTF-8",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
            "MISE_GLOBAL_CONFIG_FILE": str(self.root / "unrelated-mise.toml"),
            "MISE_CEILING_PATHS": str(self.root / "unrelated-ceiling"),
        }
        self.fake_id("1000")
        shutil.copyfile(REPO / "home" / SCRIPT, self.source / SCRIPT)
        config = self.source / "dot_config/mise"
        (config / "conf.d").mkdir(parents=True)
        (config / "config.toml").write_text('[tools]\nnode = "24"\n')
        (config / "conf.d/cargo.toml").write_text('[tools]\n"cargo:demo" = "latest"\n')
        (self.source / ".chezmoiignore").write_text(
            '{{ if ne .chezmoi.os "linux" }}\n.config/mise/conf.d/**\n{{ end }}\n'
            '{{ if eq .chezmoi.os "windows" }}\n.config/mise/**\n{{ end }}\n')
        self.binary = self.home / ".local/bin/mise"
        self.fake_mise(self.binary)

    def fake_id(self, uid):
        path = self.path_bin / "id"
        path.write_text(f'#!/bin/sh\n[ "$1" = -u ] || exit 1\nprintf "%s\\n" {uid}\n')
        path.chmod(0o755)

    def fake_mise(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"#!{sys.executable}\n" + '''
import json, os, pathlib, sys
home = pathlib.Path(os.environ["HOME"])
config = pathlib.Path(os.environ["MISE_CONFIG_DIR"])
assert "MISE_GLOBAL_CONFIG_FILE" not in os.environ
assert os.environ["MISE_CEILING_PATHS"] == str(home)
assert (config / "config.toml").read_text() == '[tools]\\nnode = "24"\\n'
if os.environ["FAKE_EXPECT_CARGO"] == "true":
    assert (config / "conf.d/cargo.toml").read_text() == '[tools]\\n"cargo:demo" = "latest"\\n'
with (home / "calls.jsonl").open("a") as calls:
    calls.write(json.dumps({"argv": sys.argv, "cwd": os.getcwd(),
        "system_deps": os.environ["MISE_SYSTEM_DEPS"],
        "auto_update": os.environ["MISE_AUTO_UPDATE"]}) + "\\n")
print("fake Mise: native output", flush=True)
if (home / "fail").exists():
    print("fake Mise: install failed", file=sys.stderr)
    sys.exit(23)
(home / "fake-installed-tool").write_text("installed")
''')
        path.chmod(0o755)

    def chezmoi(self, *args, platform="linux", input=None):
        return subprocess.run([
            CHEZMOI, "--source", str(self.source), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
            "--cache", str(self.root / "cache/chezmoi"),
            "--override-data", json.dumps({"chezmoi": {"os": platform},
                                           "ManagedByNimbus": False}),
            *args], env=self.env | {"FAKE_EXPECT_CARGO": str(platform == "linux").lower()},
            cwd=self.root, input=input,
            capture_output=True, text=True, timeout=20)

    def calls(self):
        log = self.home / "calls.jsonl"
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_apply_writes_configs_before_install_and_repairs_missing_tool(self):
        # A PATH installation must not override Nimbus's installed binary.
        self.fake_mise(self.path_bin / "mise")
        for _ in range(2):
            result = self.chezmoi("apply")
            self.assert_success(result)
            self.assertIn("installing configured Mise runtimes and tools", result.stdout)
            self.assertIn("fake Mise: native output", result.stdout)
            tool = self.home / "fake-installed-tool"
            self.assertTrue(tool.exists())
            tool.unlink()
        self.assertEqual(len(self.calls()), 2)
        for call in self.calls():
            self.assertEqual(call, {
                "argv": [str(self.binary), "-C", str(self.home), "install"],
                "cwd": str(self.home), "system_deps": "warn", "auto_update": "false"})

    def test_failure_is_visible_and_next_apply_retries(self):
        (self.home / "fail").touch()
        result = self.chezmoi("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fake Mise: install failed", result.stderr)
        self.assertIn("exit status 23", result.stderr)
        self.assertFalse((self.home / "fake-installed-tool").exists())
        (self.home / "fail").unlink()
        self.assert_success(self.chezmoi("apply"))
        self.assertEqual(len(self.calls()), 2)
        self.assertTrue((self.home / "fake-installed-tool").exists())

    @unittest.skipUnless(MISE, "mise is required for native config discovery")
    def test_native_discovery_excludes_home_and_parent_configs(self):
        # Use the real config loader behind a probe, never the real installer.
        self.binary.write_text(f"#!{sys.executable}\n" + '''
import os, subprocess, sys
assert sys.argv[1:] == ["-C", os.environ["HOME"], "install"]
result = subprocess.run([os.environ["MISE_PROBE_BINARY"], "-C", os.environ["HOME"],
                         "config", "ls", "--json"], check=False)
sys.exit(result.returncode)
''')
        self.env.update({
            "MISE_PROBE_BINARY": MISE, "MISE_OFFLINE": "true",
            "MISE_SYSTEM_CONFIG_DIR": str(self.root / "system-mise"),
        })
        (self.root / "mise.toml").write_text('[tools]\npython = "3.12"\n')
        (self.home / ".tool-versions").write_text("go 1.25\n")
        for name in ("mise.toml", ".mise.toml"):
            for trusted in (False, True):
                for content in ('[tools]\npython = "3.12"\n', 'invalid = [\n'):
                    with self.subTest(name=name, trusted=trusted, content=content):
                        path = self.home / name
                        path.write_text(content)
                        if trusted:
                            self.env["MISE_TRUSTED_CONFIG_PATHS"] = str(self.home)
                        else:
                            self.env.pop("MISE_TRUSTED_CONFIG_PATHS", None)
                        result = self.chezmoi("apply")
                        self.assert_success(result)
                        # The script prints one status line before the probe JSON.
                        configs = json.loads(result.stdout.split("\n", 1)[1])
                        self.assertEqual({entry["path"] for entry in configs}, {
                            str(self.home / ".config/mise/config.toml"),
                            str(self.home / ".config/mise/conf.d/cargo.toml"),
                        })
                        self.assertEqual({tool for entry in configs for tool in entry["tools"]},
                                         {"node", "cargo:demo"})
                        path.unlink()
        self.assertFalse((self.root / "data/mise/installs").exists())

    def test_missing_mise_fails_clearly(self):
        self.binary.unlink()
        result = self.chezmoi("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Mise is required", result.stderr)
        self.assertEqual(self.calls(), [])

    def test_root_is_rejected_without_installing(self):
        self.fake_id("0")
        result = self.chezmoi("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("normal user, not root", result.stderr)
        self.assertEqual(self.calls(), [])

    def test_missing_config_fails_clearly(self):
        (self.source / "dot_config/mise/config.toml").unlink()
        result = self.chezmoi("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing Mise configuration", result.stderr)
        self.assertEqual(self.calls(), [])

    def test_path_fallback_on_macos(self):
        self.binary.unlink()
        self.fake_mise(self.path_bin / "mise")
        self.assert_success(self.chezmoi("apply", platform="darwin"))
        self.assertEqual(self.calls()[0]["argv"][0], str(self.path_bin / "mise"))

    def test_platform_rendering_and_windows_apply(self):
        for platform in ("linux", "darwin", "windows"):
            with self.subTest(platform=platform):
                result = self.chezmoi("execute-template", platform=platform,
                                      input=(self.source / SCRIPT).read_text())
                self.assert_success(result)
                if platform == "windows":
                    self.assertEqual(result.stdout.strip(), "")
                else:
                    self.assertTrue(result.stdout.startswith("#!/bin/sh\n"))
                    syntax = subprocess.run(["/bin/sh", "-n"], input=result.stdout,
                                            text=True, capture_output=True)
                    self.assert_success(syntax)
        self.assert_success(self.chezmoi("apply", platform="windows"))
        self.assertEqual(self.calls(), [])

    def test_preview_is_read_only_and_script_stays_visible(self):
        for command in ("managed", "status", "diff", "verify"):
            with self.subTest(command=command):
                result = self.chezmoi(command)
                # Verify reports unapplied fixture files without installing.
                if command != "verify":
                    self.assert_success(result)
                if command == "diff":
                    self.assertIn("installing configured Mise runtimes and tools", result.stdout)
                self.assertEqual(self.calls(), [])
        self.assert_success(self.chezmoi("apply", "--dry-run"))
        self.assertEqual(self.calls(), [])
        self.assertFalse((self.home / ".config/mise/config.toml").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
