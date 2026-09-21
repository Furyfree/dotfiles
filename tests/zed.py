"""Check Zed source rendering without opening the editor or changing live state."""

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")


def strict_json(text):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique_keys)


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
class Zed(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-zed-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.env = {
            "HOME": str(self.home), "USERPROFILE": str(self.home), "PATH": "",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_STATE_HOME": str(self.root / "state"),
        }

    def render(self, platform, noctalia=False, legacy=False):
        data = {"chezmoi": {"os": platform}, "onePasswordSsh": False}
        if not legacy:
            data["profiles"] = ["common", "hyprland-noctalia"] if noctalia else ["common"]
        roots = {"linux": [".config", ".local"],
                 "darwin": [".config", "Library/Application Support"],
                 "windows": [".config", "AppData/Roaming"]}[platform]
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"), "--cache", str(self.root / "cache/chezmoi"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"), "--skip-secrets",
            "--override-data", json.dumps(data), "dump", "--format=json", *[str(self.home / root) for root in roots],
        ], env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        # Rendering without init may warn about the intentionally absent generated config.
        warning = "chezmoi: warning: config file template has changed, run chezmoi init to regenerate config file\n"
        self.assertEqual(result.stderr.replace(warning, ""), "")
        return {name: entry["contents"] for name, entry in json.loads(result.stdout).items()
                if entry["type"] == "file"}

    def test_platform_targets_and_theme_ownership(self):
        for platform in ("linux", "darwin", "windows"):
            for noctalia in (False, True):
                with self.subTest(platform=platform, noctalia=noctalia):
                    files = self.render(platform, noctalia)
                    target = "AppData/Roaming/Zed" if platform == "windows" else ".config/zed"
                    zed_files = {name for name in files if name.startswith((".config/zed/", "AppData/Roaming/Zed/"))}
                    self.assertEqual(zed_files, {f"{target}/settings.json", f"{target}/keymap.json"})
                    settings = strict_json(files[f"{target}/settings.json"])
                    enabled = platform == "linux" and noctalia
                    if enabled:
                        self.assertEqual(settings["theme"]["light"], "Noctalia Light")
                        self.assertEqual(settings["theme"]["dark"], "Noctalia Dark")
                    self.assertEqual(".config/noctalia/config.toml" in files, enabled)
                    if platform == "windows":
                        self.assertNotIn("agent_servers", settings)

    def test_privacy_and_unsaved_data(self):
        settings = strict_json(self.render("linux")[".config/zed/settings.json"])
        self.assertFalse(settings["agent"]["enable_feedback"])
        self.assertFalse(settings["session"]["trust_all_worktrees"])
        self.assertTrue(settings["session"]["restore_unsaved_buffers"])
        self.assertEqual(settings["telemetry"], {"diagnostics": False, "metrics": False})
        self.assertTrue(settings["redact_private_values"])

    def test_local_model_options_survive_without_changing_managed_settings(self):
        for platform in ("linux", "darwin", "windows"):
            with self.subTest(platform=platform):
                target = "AppData/Roaming/Zed/settings.json" if platform == "windows" else ".config/zed/settings.json"
                path = self.home / target
                path.parent.mkdir(parents=True, exist_ok=True)
                local = {
                    "agent": {
                        "default_model": {"provider": "example", "model": "local-choice"},
                        "commit_message_model": {"provider": "example", "model": "commit-choice"},
                        "enable_feedback": True,
                    },
                    "agent_servers": {
                        name: {"default_config_options": {"fast-mode": False, "model": "chosen"},
                               "command": "/unmanaged/launcher"}
                        for name in ("opencode", "grok-build", "claude-acp", "codex-acp")
                    },
                    "telemetry": {"metrics": True},
                }
                # Zed accepts JSONC. Rendering must not change the live input.
                contents = "// Local model choices\n" + json.dumps(local)[:-1] + ",}\n"
                path.write_text(contents)
                rendered = self.render(platform)[target]
                settings = strict_json(rendered)
                self.assertEqual(path.read_text(), contents)
                for key in ("default_model", "commit_message_model"):
                    self.assertEqual(settings["agent"][key], local["agent"][key])
                self.assertFalse(settings["agent"]["enable_feedback"])
                self.assertFalse(settings["telemetry"]["metrics"])
                if platform != "windows":
                    for name, server in settings["agent_servers"].items():
                        if name not in local["agent_servers"]:
                            continue
                        self.assertEqual(server["default_config_options"],
                                         local["agent_servers"][name]["default_config_options"])
                        self.assertNotEqual(server.get("command"), "/unmanaged/launcher")
                path.write_text(rendered)
                self.assertEqual(self.render(platform)[target], rendered)
                # Changing a choice and removing it both take effect locally.
                settings["agent"]["default_model"] = None
                del settings["agent"]["commit_message_model"]
                if platform != "windows":
                    settings["agent_servers"]["codex-acp"]["default_config_options"] = {"fast-mode": True}
                    del settings["agent_servers"]["claude-acp"]["default_config_options"]
                path.write_text(json.dumps(settings))
                changed = strict_json(self.render(platform)[target])
                self.assertIsNone(changed["agent"]["default_model"])
                self.assertNotIn("commit_message_model", changed["agent"])
                if platform != "windows":
                    self.assertEqual(changed["agent_servers"]["codex-acp"]["default_config_options"],
                                     {"fast-mode": True})
                    self.assertNotIn("default_config_options", changed["agent_servers"]["claude-acp"])
                path.unlink()

    def test_local_only_changes_keep_exact_jsonc_without_diff(self):
        target = ".config/zed/settings.json"
        settings = strict_json(self.render("linux")[target])
        settings["agent"]["default_model"] = {"provider": "example", "model": "chosen"}
        settings["agent_servers"]["codex-acp"]["default_config_options"] = {"fast-mode": True}
        path = self.home / target
        path.parent.mkdir(parents=True)
        contents = "// My local choices\n" + json.dumps(settings, indent=4)[:-1] + ",}\n"
        path.write_text(contents)
        self.assertEqual(self.render("linux")[target], contents)

    def test_invalid_local_json_fails_without_overwriting(self):
        path = self.home / ".config/zed/settings.json"
        path.parent.mkdir(parents=True)
        path.write_text("{invalid")
        with self.assertRaises(AssertionError):
            self.render("linux")
        self.assertEqual(path.read_text(), "{invalid")

    def test_keymap_parses_on_each_platform(self):
        for platform in ("linux", "darwin", "windows"):
            with self.subTest(platform=platform):
                target = "AppData/Roaming/Zed" if platform == "windows" else ".config/zed"
                strict_json(self.render(platform)[f"{target}/keymap.json"])

    def test_legacy_data_renders_valid_settings(self):
        strict_json(self.render("linux", legacy=True)[".config/zed/settings.json"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
