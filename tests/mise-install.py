#!/usr/bin/env python3
"""Exercise the apply lifecycle in a tiny temporary source with a fake Mise."""

import json
import os
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
        for command in ("tee", "stat", "date"):
            (self.path_bin / command).symlink_to(shutil.which(command))
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
if "exec" in sys.argv:
    if (home / "missing-replacement").exists():
        print("fake Mise: missing replacement", file=sys.stderr)
        sys.exit(1)
    print(home / "fake-installed-tool")
    sys.exit(0)
if "prune" in sys.argv:
    print("fake Mise: targeted cleanup", flush=True)
    sys.exit(0)
print("fake Mise: native output", flush=True)
if (home / "fail").exists():
    print("fake Mise: install failed", file=sys.stderr)
    sys.exit(23)
(home / "fake-installed-tool").write_text("installed")
(home / "fake-installed-tool").chmod(0o755)
''')
        path.chmod(0o755)

    def chezmoi(self, *args, platform="linux", input=None, stored=False):
        command = [
            CHEZMOI, "--source", str(self.source), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
            "--cache", str(self.root / "cache/chezmoi")]
        if not stored:
            command += ["--override-data", json.dumps({"chezmoi": {"os": platform},
                                                       "ManagedByNimbus": False})]
        return subprocess.run(command + list(args),
            env=self.env | {"FAKE_EXPECT_CARGO": str(platform == "linux").lower()},
            cwd=self.root, input=input,
            capture_output=True, text=True, timeout=20)

    def calls(self, all_commands=False):
        log = self.home / "calls.jsonl"
        calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
        return calls if all_commands else [call for call in calls if call["argv"][-1] == "install"]

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(sys.platform == "linux", "Nimbus handoff targets Linux")
    def test_real_handoff_prompts_refresh_and_apply(self):
        op = self.path_bin / "op"
        op.write_text("#!/bin/sh\nexit 0\n")
        op.chmod(0o755)
        shutil.copyfile(REPO / "home/.chezmoi.toml.tmpl",
                        self.source / ".chezmoi.toml.tmpl")
        initial = ["--promptString", "Machine=vm", "--promptBool",
                   "ManagedByNimbus=true", "--promptBool",
                   "Enable 1Password SSH integration=false", "--promptMultichoice",
                   "Profiles=common/development/future-profile"]
        self.assert_success(self.chezmoi("init", "--no-tty", *initial, stored=True, input=""))
        data = self.chezmoi("data", "--format=json", stored=True)
        self.assert_success(data)
        selection = json.loads(data.stdout)
        self.assertEqual(selection["Machine"], "vm")
        self.assertTrue(selection["ManagedByNimbus"])
        self.assertFalse(selection["onePasswordSsh"])
        self.assertEqual(selection["Profiles"], ["common", "development", "future-profile"])
        self.assertEqual(self.calls(), [])
        result = self.chezmoi("apply", stored=True)
        self.assert_success(result)
        self.assertIn('Setup note: 1Password: open the desktop app', result.stdout)
        self.assertIn('1Password SSH is not enabled', result.stdout)
        self.assertLess(result.stdout.index('Setup note:'),
                        result.stdout.index('fake Mise: native output'))

        # Model the user's opt-in, then Nimbus's complete refresh command.
        enabled = [arg.replace("integration=false", "integration=true") for arg in initial]
        self.assert_success(self.chezmoi(
            "init", "--prompt", "--no-tty", *enabled, stored=True))
        self.assert_success(self.chezmoi(
            "init", "--prompt", "--no-tty", "--promptString", "Machine=laptop",
            "--promptBool", "ManagedByNimbus=true", "--promptMultichoice",
            "Profiles=common/gaming", "--promptBool",
            "Enable 1Password SSH integration=true", stored=True))
        data = self.chezmoi("data", "--format=json", stored=True)
        self.assert_success(data)
        selection = json.loads(data.stdout)
        self.assertEqual(selection["Machine"], "laptop")
        self.assertTrue(selection["ManagedByNimbus"])
        self.assertTrue(selection["onePasswordSsh"])
        self.assertEqual(selection["Profiles"], ["common", "gaming"])
        self.assertEqual(selection["profiles"], ["common", "unix", "linux", "gaming"])
        self.assertEqual(len(self.calls()), 1)
        (self.home / "fake-installed-tool").unlink()
        (self.home / "fail").touch()
        result = self.chezmoi("apply", stored=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Setup note: 1Password SSH: enable the SSH agent', result.stdout)
        self.assertIn('fake Mise: install failed', result.stderr)
        self.assertNotIn('1Password SSH is not enabled', result.stdout)
        (self.home / "fail").unlink()
        self.assert_success(self.chezmoi("apply", stored=True))
        self.assertTrue((self.home / "fake-installed-tool").exists())
        self.assertEqual(len(self.calls()), 3)

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
if "exec" in sys.argv:
    print(sys.argv[0])
    sys.exit(0)
if "prune" in sys.argv:
    sys.exit(0)
assert sys.argv[1:] == ["-C", os.environ["HOME"], "install"]
with open(os.path.join(os.environ["HOME"], "discovered.json"), "w") as output:
    result = subprocess.run([os.environ["MISE_PROBE_BINARY"], "-C", os.environ["HOME"],
                             "config", "ls", "--json"], check=False, stdout=output)
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
                        configs = json.loads((self.home / "discovered.json").read_text())
                        self.assertEqual({entry["path"] for entry in configs}, {
                            str(self.home / ".config/mise/config.toml"),
                            str(self.home / ".config/mise/conf.d/cargo.toml"),
                        })
                        self.assertEqual({tool for entry in configs for tool in entry["tools"]},
                                         {"node", "cargo:demo"})
                        path.unlink()
        self.assertFalse((self.root / "data/mise/installs").exists())

    def test_cleanup_waits_for_successful_install_and_all_replacements(self):
        (self.home / "fail").touch()
        self.assertNotEqual(self.chezmoi("apply").returncode, 0)
        self.assertFalse(any("prune" in call["argv"] for call in self.calls(True)))
        (self.home / "fail").unlink()
        (self.home / "missing-replacement").touch()
        self.assertNotEqual(self.chezmoi("apply").returncode, 0)
        self.assertFalse(any("prune" in call["argv"] for call in self.calls(True)))
        (self.home / "missing-replacement").unlink()
        self.assert_success(self.chezmoi("apply"))
        calls = self.calls(True)
        self.assertEqual(calls[-1]["argv"][3:], ["prune", "--tools", "--yes",
            "cargo:caligula", "cargo:https://github.com/Myriad-Dreamin/tinymist",
            "cargo:cargo-update", "cargo:sheldon", "cargo:resvg", "cargo:vm-curator"])
        self.assertEqual([call["argv"][-2] for call in calls[-6:-1]],
                         ["tinymist", "sheldon", "resvg", "caligula", "vm-curator"])

    @unittest.skipUnless(os.getuid() == 1000, "private-log fixture uses uid 1000")
    def test_private_tool_log_preserves_output_failure_and_retry(self):
        log_dir = self.root / "install-log"
        log_dir.mkdir(mode=0o700)
        self.env["NIMBUS_INSTALL_LOG_DIR"] = str(log_dir)
        self.env["UNRELATED_SECRET"] = "never-log-this-test-secret"
        (self.home / "fail").touch()
        result = self.chezmoi("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fake Mise: install failed", result.stdout + result.stderr)
        log = log_dir / "mise.log"
        self.assertEqual(log.stat().st_mode & 0o777, 0o600)
        self.assertIn("fake Mise: install failed", log.read_text())
        self.assertIn("exit=23 duration=", log.read_text())
        self.assertNotIn("never-log-this-test-secret", log.read_text())
        (self.home / "fail").unlink()
        self.assert_success(self.chezmoi("apply"))
        self.assertIn("fake Mise: targeted cleanup", log.read_text())
        self.assertIn("exit=23 duration=", log.read_text())
        self.assertIn("exit=0 duration=", log.read_text())

    @unittest.skipUnless(os.getuid() == 1000, "private-log fixture uses uid 1000")
    def test_log_rejects_unsafe_targets_and_write_failure(self):
        log_dir = self.root / "install-log"
        log_dir.mkdir(mode=0o755)
        self.env["NIMBUS_INSTALL_LOG_DIR"] = str(log_dir)
        self.assertNotEqual(self.chezmoi("apply").returncode, 0)
        self.assertEqual(self.calls(), [])
        log_dir.chmod(0o700)
        target = self.root / "unrelated"
        target.write_text("preserve")
        log = log_dir / "mise.log"
        log.symlink_to(target)
        self.assertNotEqual(self.chezmoi("apply").returncode, 0)
        self.assertEqual(target.read_text(), "preserve")
        self.assertEqual(self.calls(), [])
        log.unlink()
        target.chmod(0o600)
        os.link(target, log)
        self.assertNotEqual(self.chezmoi("apply").returncode, 0)
        self.assertEqual(target.read_text(), "preserve")
        self.assertEqual(self.calls(), [])
        log.unlink()
        tee = self.path_bin / "tee"
        tee.unlink()
        tee.write_text("#!/bin/sh\nexit 7\n")
        tee.chmod(0o755)
        result = self.chezmoi("apply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot write the Mise installation log", result.stderr)
        self.assertFalse(any("prune" in call["argv"] for call in self.calls(True)))

    @unittest.skipUnless(MISE, "mise is required for native migration validation")
    def test_native_cleanup_preserves_other_tools_and_tracked_projects(self):
        native = self.root / "native"
        config = native / "config"
        config.mkdir(parents=True)
        (config / "config.toml").write_text('[tools]\nsheldon = "1.0.0"\n')
        project = native / "project"
        project.mkdir()
        (project / "mise.toml").write_text('[tools]\n"cargo:sheldon" = "1.0.0"\n')
        installs = native / "data/installs"
        providers = {
            "sheldon": ("sheldon", "aqua:rossmacarthur/sheldon"),
            "cargo-sheldon": ("cargo:sheldon", "cargo:sheldon"),
            "cargo-cargo-update": ("cargo:cargo-update", "cargo:cargo-update"),
            "cargo-keep-me": ("cargo:keep-me", "cargo:keep-me"),
            "cargo-https-github-com-myriad-dreamin-tinymist": (
                "cargo:https://github.com/Myriad-Dreamin/tinymist",
                "cargo:https://github.com/Myriad-Dreamin/tinymist"),
        }
        for directory, (short, full) in providers.items():
            install = installs / directory
            (install / "1.0.0/bin").mkdir(parents=True)
            (install / ".mise.backend.toml").write_text(
                f'short = "{short}"\nfull = "{full}"\n')
            (install / "1.0.0/bin/tool").write_text("fixture")
        env = {"PATH": "/usr/bin:/bin", "HOME": str(self.home), "LANG": "C.UTF-8",
               "MISE_CONFIG_DIR": str(config), "MISE_SYSTEM_CONFIG_DIR": str(native / "system"),
               "MISE_DATA_DIR": str(native / "data"), "MISE_STATE_DIR": str(native / "state"),
               "MISE_CACHE_DIR": str(native / "cache"), "MISE_CEILING_PATHS": str(native),
               "MISE_OFFLINE": "true", "MISE_AUTO_UPDATE": "false",
               "MISE_TRUSTED_CONFIG_PATHS": str(project)}
        self.assert_success(subprocess.run([MISE, "-C", str(project), "ls", "--json"],
            env=env, cwd=project, text=True, capture_output=True, timeout=30))
        self.assert_success(self.chezmoi("apply"))
        cleanup = self.calls(True)[-1]["argv"][3:]
        self.assert_success(subprocess.run([MISE, "-C", str(native), *cleanup],
            env=env, cwd=native, text=True, capture_output=True, timeout=30))
        for directory in ("sheldon", "cargo-sheldon", "cargo-keep-me"):
            self.assertTrue((installs / directory / "1.0.0").is_dir())
        for directory in ("cargo-cargo-update", "cargo-https-github-com-myriad-dreamin-tinymist"):
            self.assertFalse((installs / directory / "1.0.0").exists())

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
                    self.assertTrue(result.stdout.startswith("#!/bin/bash\n"))
                    syntax = subprocess.run(["/bin/bash", "-n"], input=result.stdout,
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
