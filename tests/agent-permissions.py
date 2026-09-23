"""Patch agent CLI permission keys in an isolated home. Never reads live agent state."""

import json
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")
TARGETS = (
    ".config/opencode/opencode.jsonc",
    ".claude/settings.json",
    ".grok/config.toml",
    ".codex/config.toml",
    ".pi/agent/settings.json",
)
UNMANAGED = (
    ".claude/CLAUDE.md", ".claude/skills", ".claude/auth.json",
    ".codex/AGENTS.md", ".codex/auth.json", ".grok/auth.json",
    ".config/opencode/AGENTS.md", ".agents/skills",
    ".pi/agent/AGENTS.md", ".pi/agent/auth.json", ".pi/agent/extensions",
)


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
class AgentPermissions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-agent-perm-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.env = {
            "HOME": str(self.home), "USERPROFILE": str(self.home), "PATH": "",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_STATE_HOME": str(self.root / "state"),
        }

    def chezmoi(self, platform, *args):
        data = {"chezmoi": {"os": platform}, "profiles": ["common"],
                "onePasswordSsh": False}
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--cache", str(self.root / "cache/chezmoi"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
            "--skip-secrets", "--no-tty", "--override-data", json.dumps(data),
            *args,
        ], env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def dump_files(self, platform):
        dumped = json.loads(self.chezmoi(
            platform, "dump", "--format=json",
            *[str(self.home / path) for path in TARGETS]))
        return {name: entry for name, entry in dumped.items()
                if entry["type"] == "file"}

    def test_unix_targets_and_windows_ignore(self):
        for platform in ("linux", "darwin"):
            with self.subTest(platform=platform):
                managed = set(self.chezmoi(platform, "managed").splitlines())
                self.assertTrue(set(TARGETS) <= managed)
                for path in UNMANAGED:
                    self.assertNotIn(path, managed)
        managed = set(self.chezmoi("windows", "managed").splitlines())
        self.assertFalse(set(TARGETS) & managed)

    def test_fresh_home_renders_valid_private_configs(self):
        files = self.dump_files("linux")
        self.assertEqual(set(files), set(TARGETS))
        for name, entry in files.items():
            parser = tomllib.loads if name.endswith(".toml") else json.loads
            parser(entry["contents"])
        self.assertEqual(files[".codex/config.toml"]["perm"] & 0o777, 0o600)

    def test_preserves_other_keys_and_keeps_bytes_when_set(self):
        samples = {
            ".config/opencode/opencode.jsonc":
                '{\n  "$schema": "https://opencode.ai/config.json",\n'
                '  "plugin": ["ponytail"]\n}\n',
            ".claude/settings.json":
                '{\n  "theme": "dark",\n  "enabledPlugins": {"x": true}\n}\n',
            ".grok/config.toml":
                '[ui]\npermission_mode = "ask"\nyolo = false\n\n'
                '[plugins]\nenabled = ["ponytail"]\n',
            ".codex/config.toml":
                'approval_policy = "never"\nsandbox_mode = "workspace-write"\n'
                'model = "gpt-test"\n\n[projects."/tmp/work"]\n'
                'trust_level = "trusted"\n',
            ".pi/agent/settings.json":
                '{\n  "defaultModel": "test-model",\n  "theme": "dark"\n}\n',
        }
        for rel, text in samples.items():
            path = self.home / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        files = self.dump_files("linux")
        opencode = json.loads(files[".config/opencode/opencode.jsonc"]["contents"])
        self.assertEqual(opencode["plugin"], ["ponytail"])
        claude = json.loads(files[".claude/settings.json"]["contents"])
        self.assertEqual(claude["theme"], "dark")
        grok = tomllib.loads(files[".grok/config.toml"]["contents"])
        self.assertEqual(grok["ui"]["yolo"], False)
        self.assertEqual(grok["plugins"]["enabled"], ["ponytail"])
        codex = tomllib.loads(files[".codex/config.toml"]["contents"])
        self.assertEqual(codex["model"], "gpt-test")
        self.assertEqual(codex["projects"]["/tmp/work"]["trust_level"], "trusted")
        pi = json.loads(files[".pi/agent/settings.json"]["contents"])
        self.assertEqual((pi["defaultModel"], pi["theme"]), ("test-model", "dark"))
        for rel, text in samples.items():
            self.assertEqual((self.home / rel).read_text(), text)

        # Feed rendered output back as input to check repeatability, not policy values.
        already = {rel: "\n" + entry["contents"] for rel, entry in files.items()}
        for rel, text in already.items():
            (self.home / rel).write_text(text)
        files = self.dump_files("linux")
        for rel, text in already.items():
            self.assertEqual(files[rel]["contents"], text)


if __name__ == "__main__":
    unittest.main()
