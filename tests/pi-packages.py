"""Exercise the Pi package hook through Chezmoi without installing live tools."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = "run_after_install-pi-packages.sh.tmpl"
CHEZMOI = shutil.which("chezmoi")


@unittest.skipUnless(CHEZMOI, "chezmoi is required")
class PiPackages(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-pi-packages-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.source = self.root / "source"
        self.bin = self.root / "bin"
        for path in (self.home, self.source, self.bin):
            path.mkdir()
        self.env = {
            "HOME": str(self.home), "PATH": str(self.bin), "LANG": "C.UTF-8",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
            "MISE_GLOBAL_CONFIG_FILE": str(self.root / "unrelated.toml"),
            "MISE_CEILING_PATHS": str(self.root / "unrelated-ceiling"),
            "PI_CODING_AGENT_DIR": str(self.root / "unrelated-pi"),
        }
        self.fake_id("1000")
        shutil.copyfile(REPO / "home" / SCRIPT, self.source / SCRIPT)
        settings = self.source / "dot_pi/agent"
        settings.mkdir(parents=True)
        shutil.copyfile(REPO / "home/dot_pi/agent/settings.json.tmpl",
                        settings / "settings.json.tmpl")
        self.binary = self.home / ".local/bin/mise"
        self.fake_mise(self.binary)
        pi = self.bin / "pi"
        pi.write_text(f"#!{sys.executable}\n" + '''
import json, os, pathlib, sys
home = pathlib.Path(os.environ["HOME"])
assert os.environ["PI_CODING_AGENT_DIR"] == str(home / ".pi/agent")
assert sys.argv[1:] == ["install", "npm:pi-terminal-math"]
with (home / "pi-calls.jsonl").open("a") as log:
    log.write(json.dumps(sys.argv[1:]) + "\\n")
if (home / "fail").exists():
    print("fixture Pi: download failed", file=sys.stderr)
    sys.exit(23)
p = home / ".pi/agent/settings.json"
s = json.loads(p.read_text())
source = sys.argv[2]
if source not in s.get("packages", []):
    s.setdefault("packages", []).append(source)
p.write_text(json.dumps(s))
(home / "fixture-package").write_text("installed")
print("fixture Pi: installed", flush=True)
''')
        pi.chmod(0o755)

    def fake_id(self, uid):
        path = self.bin / "id"
        path.write_text(f'#!/bin/sh\n[ "$1" = -u ] || exit 1\nprintf "%s\\n" {uid}\n')
        path.chmod(0o755)

    def fake_mise(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"#!{sys.executable}\n" + '''
import json, os, pathlib, subprocess, sys
home = pathlib.Path(os.environ["HOME"])
args = sys.argv[1:]
assert args == ["-C", str(home), "exec", "--", "pi", "install", "npm:pi-terminal-math"]
assert os.getcwd() == str(home)
assert os.environ["MISE_CONFIG_DIR"] == str(home / ".config/mise")
assert os.environ["MISE_CEILING_PATHS"] == str(home)
assert "MISE_GLOBAL_CONFIG_FILE" not in os.environ
assert os.environ["MISE_AUTO_INSTALL"] == "false"
assert os.environ["MISE_AUTO_UPDATE"] == "false"
with (home / "mise-calls.jsonl").open("a") as log:
    log.write(json.dumps(sys.argv) + "\\n")
if os.environ.get("EXPECT_MISE_FIRST") == "true":
    assert (home / "tools-installed").exists()
sys.exit(subprocess.run(args[4:], check=False).returncode)
''')
        path.chmod(0o755)

    def chezmoi(self, *args, platform="linux", input=None):
        return subprocess.run([
            CHEZMOI, "--source", str(self.source), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--persistent-state", str(self.root / "state.boltdb"),
            "--cache", str(self.root / "cache/chezmoi"),
            "--override-data", json.dumps({"chezmoi": {"os": platform}}), *args,
        ], env=self.env, cwd=self.root, input=input, text=True,
            capture_output=True, timeout=20, check=False)

    def calls(self, name="pi"):
        log = self.home / f"{name}-calls.jsonl"
        return [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_full_apply_installs_after_mise_and_repairs_missing_package(self):
        # Chezmoi executes the existing tool hook before the new package hook.
        shutil.copyfile(REPO / "home/run_after_install-mise-tools.sh.tmpl",
                        self.source / "run_after_install-mise-tools.sh.tmpl")
        config = self.source / "dot_config/mise"
        config.mkdir(parents=True)
        (config / "config.toml").write_text('[tools]\npi = "latest"\n')
        original = self.binary.read_text()
        self.binary.write_text(original.replace(
            'args = sys.argv[1:]',
            'args = sys.argv[1:]\n'
            'if args == ["-C", str(home), "install"]:\n'
            '    assert (home / ".config/mise/config.toml").exists()\n'
            '    (home / "tools-installed").write_text("ready")\n'
            '    sys.exit(0)'))
        self.env["EXPECT_MISE_FIRST"] = "true"
        target = self.home / ".pi/agent/settings.json"
        target.parent.mkdir(parents=True)
        keep = {"source": "npm:unrelated", "extensions": []}
        target.write_text(json.dumps({"defaultModel": "local-choice", "packages": [keep]}))
        for _ in range(2):
            self.assert_success(self.chezmoi("apply"))
            self.assertTrue((self.home / "fixture-package").exists())
            saved = json.loads(target.read_text())
            self.assertEqual(saved["defaultModel"], "local-choice")
            self.assertEqual(saved["packages"], [keep, "npm:pi-terminal-math"])
            (self.home / "fixture-package").unlink()
        self.assertEqual(len(self.calls()), 2)

    def test_failure_warns_and_next_apply_retries_without_resetting_settings(self):
        (self.home / "fail").touch()
        result = self.chezmoi("apply")
        self.assert_success(result)
        self.assertIn("fixture Pi: download failed", result.stderr)
        self.assertIn("Pi packages are incomplete", result.stderr)
        self.assertFalse((self.home / "fixture-package").exists())
        (self.home / "fail").unlink()
        self.assert_success(self.chezmoi("apply"))
        self.assertEqual(len(self.calls()), 2)
        self.assertTrue((self.home / "fixture-package").exists())

    def test_missing_pi_warns_without_installing_mise_tools(self):
        (self.bin / "pi").unlink()
        result = self.chezmoi("apply")
        self.assert_success(result)
        self.assertIn("Pi packages are incomplete", result.stderr)
        self.assertEqual(self.calls(), [])
        self.assertEqual(len(self.calls("mise")), 1)

    def test_missing_mise_and_root_fail_before_running_pi(self):
        self.binary.unlink()
        result = self.chezmoi("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Mise is required", result.stderr)
        self.assertEqual(self.calls(), [])
        self.fake_mise(self.binary)
        self.fake_id("0")
        result = self.chezmoi("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("normal user, not root", result.stderr)
        self.assertEqual(self.calls(), [])

    def test_macos_uses_path_mise_when_the_private_binary_is_absent(self):
        self.binary.unlink()
        self.fake_mise(self.bin / "mise")
        self.assert_success(self.chezmoi("apply", platform="darwin"))
        self.assertEqual(self.calls("mise")[0][0], str(self.bin / "mise"))
        self.assertEqual(len(self.calls()), 1)

    def test_platforms_render_and_windows_installs_nothing(self):
        for platform in ("linux", "darwin", "windows"):
            result = self.chezmoi("execute-template", platform=platform,
                                  input=(self.source / SCRIPT).read_text())
            self.assert_success(result)
            if platform == "windows":
                self.assertEqual(result.stdout.strip(), "")
            else:
                syntax = subprocess.run(["/bin/bash", "-n"], input=result.stdout,
                                        text=True, capture_output=True, check=False)
                self.assert_success(syntax)
        self.assert_success(self.chezmoi("apply", platform="windows"))
        self.assertEqual(self.calls(), [])

    def test_preview_and_dry_run_never_install(self):
        for command in ("managed", "status", "diff", "verify"):
            result = self.chezmoi(command)
            if command != "verify":
                self.assert_success(result)
            self.assertEqual(self.calls(), [])
        self.assert_success(self.chezmoi("apply", "--dry-run"))
        self.assertEqual(self.calls(), [])
        self.assertFalse((self.home / ".pi/agent/settings.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
