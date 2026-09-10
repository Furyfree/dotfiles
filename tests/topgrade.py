#!/usr/bin/env python3
"""Validate Topgrade using an isolated home and fake updater executables."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest


REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "home/.chezmoitemplates/configs/topgrade/topgrade.toml"
TOPGRADE = shutil.which("topgrade")
CHEZMOI = shutil.which("chezmoi")
MISE = shutil.which("mise")


class Topgrade(unittest.TestCase):
    def setUp(self):
        if not CHEZMOI:
            self.skipTest("chezmoi is not installed")
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-topgrade-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.bin = self.root / "bin"
        self.home.mkdir()
        (self.home / ".config").mkdir()
        self.bin.mkdir()
        self.log = self.root / "calls.jsonl"
        self.env = {
            "HOME": str(self.home), "PATH": str(self.bin), "LANG": "C.UTF-8",
            "NO_COLOR": "1", "TERM": "dumb",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_CONFIG_DIRS": str(self.root / "system-config"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
            "TMPDIR": str(self.root), "FAKE_LOG": str(self.log),
        }
        self.rendered = self.render_config()
        self.config = tomllib.loads(self.rendered.read_text())

    def render_config(self, managed=True, platform="linux"):
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--cache", str(self.root / "cache/chezmoi"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
            "--skip-secrets", "--override-data", json.dumps({
                "chezmoi": {"os": platform}, "ManagedByNimbus": managed}),
            "execute-template", CONFIG.read_text()],
            env=self.env, text=True, capture_output=True, check=True)
        config = self.root / (f"topgrade-{platform}-{managed}.toml")
        config.write_text(result.stdout)
        return config

    def test_scope_and_confirmation_policy(self):
        self.assertEqual(set(self.config), {"misc", "mise", "pre_commands", "commands"})
        self.assertEqual(self.config["misc"]["only"],
                         ["mise", "github_cli_extensions", "sheldon", "tldr", "custom_commands"])
        self.assertEqual(self.config["misc"]["first"], ["mise"])
        for setting in ("pre_sudo", "sudo_loop", "assume_yes", "cleanup"):
            self.assertIs(self.config["misc"][setting], False)
        self.assertIs(self.config["misc"]["no_self_update"], True)
        self.assertIs(self.config["misc"]["ask_retry"], True)
        self.assertEqual(self.config["misc"]["notify_end"], "on_failure")
        self.assertEqual(self.config["mise"], {"bump": False})
        self.assertEqual(self.config["pre_commands"],
                         {"Nimbus system updates": "nimbus upgrade --system"})

    def fake_tools(self, copilot=False):
        tools = ["nimbus", "mise", "gh", "sheldon", "tldr"]
        if copilot:
            tools += ["sudo", "github-copilot-installer"]
        for tool in tools:
            path = self.bin / tool
            path.write_text(f"#!{sys.executable}\n" + '''
import json, os, pathlib, sys
with open(os.environ["FAKE_LOG"], "a") as log:
    log.write(json.dumps({"tool": pathlib.Path(sys.argv[0]).name,
        "args": sys.argv[1:], "cwd": os.getcwd()}) + "\\n")
if pathlib.Path(sys.argv[0]).name == "mise" and sys.argv[1:] == ["env", "--json"]:
    print("{}")
if pathlib.Path(sys.argv[0]).name == os.environ.get("FAKE_FAIL_TOOL"):
    sys.exit(int(os.environ.get("FAKE_EXIT_CODE", "23")))
if pathlib.Path(sys.argv[0]).name == "sudo":
    assert sys.argv[1] == "--"
    os.execvp(sys.argv[2], sys.argv[2:])
''')
            path.chmod(0o755)

    def run_topgrade(self, *args, copilot=False):
        # All updater names resolve to fakes. Even native discovery probes must
        # never reach the real tools or the caller's home/authentication/session.
        self.test_scope_and_confirmation_policy()
        self.fake_tools(copilot)
        (self.bin / "sh").symlink_to("/bin/sh")
        self.env["SHELL"] = "/bin/sh"
        return subprocess.run([
            TOPGRADE, "--config", str(self.rendered), "--no-self-update", "--no-tmux",
            "--no-ask-retry", "--allow-root", *args],
            cwd=self.home, env=self.env, stdin=subprocess.DEVNULL,
            text=True, capture_output=True, timeout=30)

    def calls(self):
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    @unittest.skipUnless(TOPGRADE, "topgrade is not installed")
    def test_native_parser_and_dry_run(self):
        result = self.run_topgrade("--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Unknown configuration", result.stderr)
        # Topgrade may run read-only probes in dry-run; never an update command.
        for call in self.calls():
            self.assertEqual((call["tool"], call["args"]),
                             ("gh", ["extensions", "list"]))

    @unittest.skipUnless(TOPGRADE, "topgrade is not installed")
    def test_native_steps_use_only_fake_user_updaters(self):
        result = self.run_topgrade()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls()
        self.assertEqual([(call["tool"], call["args"]) for call in calls], [
            ("nimbus", ["upgrade", "--system"]),
            ("mise", ["plugins", "update"]),
            ("mise", ["self-update"]),
            ("mise", ["upgrade"]),
            ("mise", ["env", "--json"]),
            ("tldr", ["--update"]),
            ("sheldon", ["lock", "--update"]),
            ("gh", ["extensions", "list"]),
            ("gh", ["extension", "upgrade", "--all"]),
        ])
        # Mise must not discover a home-local/caller project configuration.
        for call in calls[1:5]:
            self.assertNotEqual(Path(call["cwd"]), self.home)
            self.assertEqual(Path(call["cwd"]).parent, self.root)

    @unittest.skipUnless(TOPGRADE, "topgrade is not installed")
    def test_explicit_config_ignores_automatic_hook_fragments(self):
        fragments = self.home / ".config/topgrade.d"
        fragments.mkdir()
        (fragments / "unexpected.toml").write_text(
            '[pre_commands]\n"Unexpected fragment" = "exit 97"\n')
        result = self.run_topgrade()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("Unexpected fragment", result.stdout + result.stderr)
        self.assertTrue(any(call["tool"] == "sheldon" for call in self.calls()))

    @unittest.skipUnless(TOPGRADE, "topgrade is not installed")
    def test_failed_update_is_not_reported_as_success(self):
        self.env["FAKE_FAIL_TOOL"] = "sheldon"
        result = self.run_topgrade()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sheldon: FAILED", result.stdout)
        self.assertEqual(self.calls()[-1]["tool"], "gh")

    @unittest.skipUnless(TOPGRADE, "topgrade is not installed")
    def test_nimbus_failure_stops_all_user_updates(self):
        self.env["FAKE_FAIL_TOOL"] = "nimbus"
        result = self.run_topgrade()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([(c["tool"], c["args"]) for c in self.calls()],
                         [("nimbus", ["upgrade", "--system"])])

    @unittest.skipUnless(TOPGRADE, "topgrade is not installed")
    def test_copilot_helper_keeps_native_prompts_and_errors(self):
        self.env["FAKE_FAIL_TOOL"] = "github-copilot-installer"
        result = self.run_topgrade(copilot=True)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([(c["tool"], c["args"]) for c in self.calls()
                          if c["tool"] in ("sudo", "github-copilot-installer")], [
            ("sudo", ["--", "github-copilot-installer", "update"]),
            ("github-copilot-installer", ["update"]),
        ])

    @unittest.skipUnless(TOPGRADE, "topgrade is not installed")
    def test_dry_run_does_not_run_copilot_helper(self):
        result = self.run_topgrade("--dry-run", copilot=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(any(c["tool"] in ("sudo", "github-copilot-installer")
                             for c in self.calls()))

    @unittest.skipUnless(TOPGRADE, "topgrade is not installed")
    def test_cancelled_nimbus_stops_all_user_updates(self):
        self.env["FAKE_FAIL_TOOL"] = "nimbus"
        self.env["FAKE_EXIT_CODE"] = "130"
        result = self.run_topgrade()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual([c["tool"] for c in self.calls()], ["nimbus"])

    def test_standalone_platforms_have_native_system_steps(self):
        for platform, native in (("linux", {"system", "flatpak"}),
                                 ("darwin", {"brew_formula", "brew_cask"})):
            config = tomllib.loads(self.render_config(False, platform).read_text())
            self.assertNotIn("pre_commands", config)
            self.assertEqual(set(config["misc"]["only"]),
                             native | {"mise", "github_cli_extensions", "sheldon", "tldr"})

    @unittest.skipUnless(MISE, "mise is not installed")
    def test_native_mise_global_fragment_discovery(self):
        config = self.home / ".config/mise"
        (config / "conf.d").mkdir(parents=True)
        (config / "config.toml").write_text('[tools]\nnode = "lts"\n')
        (config / "conf.d/linux-tools.toml").write_text(
            '[tools]\n"cargo:demo" = "latest"\n')
        # A native config listing, not an install/update or trust operation.
        for name in ("mise.toml", ".mise.toml", ".tool-versions"):
            (self.home / name).write_text("invalid project config!\n")
        with tempfile.TemporaryDirectory(dir=self.root) as workdir:
            result = subprocess.run([
                MISE, "config", "ls", "--json"], cwd=workdir,
                env=self.env | {"MISE_OFFLINE": "true", "MISE_AUTO_UPDATE": "false",
                                "MISE_SYSTEM_CONFIG_DIR": str(self.root / "system-mise")},
                stdin=subprocess.DEVNULL, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        paths = {Path(entry["path"]) for entry in json.loads(result.stdout)}
        self.assertEqual(paths, {config / "config.toml", config / "conf.d/linux-tools.toml"})

    @unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
    def test_platform_targets(self):
        for platform in ("linux", "darwin", "windows"):
            with self.subTest(platform=platform):
                result = subprocess.run([
                    CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
                    "--config", str(self.root / "chezmoi.toml"),
                    "--cache", str(self.root / "cache/chezmoi"),
                    "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
                    "--skip-secrets", "--override-data", json.dumps({
                        "chezmoi": {"os": platform}, "profiles": ["common"],
                        "onePasswordSsh": False}), "dump", "--format=json"],
                    cwd=self.root, env=self.env, stdin=subprocess.DEVNULL,
                    text=True, capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                files = {name: entry["contents"]
                         for name, entry in json.loads(result.stdout).items()
                         if name.endswith("topgrade.toml") and entry["type"] == "file"}
                expected = {} if platform == "windows" else {
                    ".config/topgrade.toml": self.render_config(managed=False, platform=platform).read_text()}
                self.assertEqual(files, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
