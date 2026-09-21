#!/usr/bin/env python3
"""Check Zed source rendering without opening the editor or changing live state."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


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
        ], env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20)
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
                    self.assertEqual(settings["theme"], {
                        "mode": "system", "light": "Noctalia Light", "dark": "Noctalia Dark"
                    } if enabled else {
                        "mode": "system", "light": "One Light", "dark": "One Dark"})
                    self.assertEqual(".config/noctalia/config.toml" in files, enabled)
                    if platform == "windows":
                        self.assertNotIn("agent_servers", settings)
                    else:
                        agents = settings["agent_servers"]
                        self.assertEqual(set(agents), {"opencode", "grok-build", "claude-acp", "codex-acp"})
                        for name in ("opencode", "claude-acp", "codex-acp"):
                            self.assertEqual(agents[name], {"type": "registry"})
                        self.assertEqual(agents["grok-build"], {
                            "type": "custom",
                            "command": str(self.home / ".local/bin/mise"),
                            "args": ["exec", "npm:@xai-official/grok", "--", "grok", "agent", "stdio"],
                        })

    def test_privacy_and_preferences(self):
        settings = strict_json(self.render("linux")[".config/zed/settings.json"])
        self.assertEqual(settings["base_keymap"], "VSCode")
        self.assertEqual(settings["agent"], {
            "default_profile": "ask", "enable_feedback": False,
            "dock": "left", "sidebar_side": "left",
        })
        self.assertEqual(settings["project_panel"], {"dock": "right"})
        self.assertEqual(settings["git_panel"], {"dock": "right"})
        self.assertEqual(settings["outline_panel"], {"dock": "right"})
        self.assertEqual(settings["jupyter"], {"enabled": True})
        self.assertFalse(settings["session"]["trust_all_worktrees"])
        self.assertTrue(settings["session"]["restore_unsaved_buffers"])
        self.assertEqual(settings["telemetry"], {"diagnostics": False, "metrics": False})
        self.assertTrue(settings["redact_private_values"])
        self.assertEqual(settings["format_on_save"], "off")
        self.assertEqual(settings["autosave"], "off")
        self.assertEqual(settings["terminal"]["shell"], "system")
        self.assertNotIn("theme_overrides", settings)
        self.assertNotIn("language_models", settings)

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

    def test_extension_inventory(self):
        settings = strict_json(self.render("linux")[".config/zed/settings.json"])
        enabled = set("""
            ansible catppuccin csharp csv dart dockerfile dracula elixir everforest
            flexoki-themes fsharp git-firefly github-dark-default github-theme gotmpl
            graphql gruvbox-material-mix html ini java just kanagawa-themes kotlin
            latex log lua macos-classic material-icon-theme nginx nix one-dark-pro
            opencode rainbow-csv rose-pine scala scheme sql svelte swift terraform
            tokyo-night toml typst xml zig
        """.split())
        self.assertEqual(settings["auto_install_extensions"],
                         dict.fromkeys(enabled, True) | {"docker-compose": False})
        updates = set("""
            ansible csharp csv dart dockerfile elixir fsharp git-firefly gotmpl
            graphql html ini java kotlin latex log lua nginx nix opencode rainbow-csv
            scala scheme sql svelte swift terraform toml xml zig
        """.split())
        self.assertEqual(settings["auto_update_extensions"],
                         dict.fromkeys(updates, True) | {"docker-compose": False})

    def test_single_additive_keybind(self):
        for platform in ("linux", "darwin", "windows"):
            with self.subTest(platform=platform):
                target = "AppData/Roaming/Zed" if platform == "windows" else ".config/zed"
                keys = strict_json(self.render(platform)[f"{target}/keymap.json"])
                modifier = "cmd" if platform == "darwin" else "ctrl"
                self.assertEqual(keys, [{"context": "Workspace", "bindings": {
                    f"{modifier}-alt-shift-j": "terminal_panel::Toggle"}}])

    def test_wrappers_and_legacy_data(self):
        for target in ("dot_config/zed", "AppData/Roaming/Zed"):
            for name in ("settings", "keymap"):
                filename = f"{name}.json.tmpl"
                if target == "dot_config/zed" and name == "settings":
                    filename = "private_" + filename
                wrapper = (REPO / "home" / target / filename).read_text()
                self.assertEqual(wrapper.strip(), '{{- template "configs/zed/' + name + '.json" . -}}')
        settings = strict_json(self.render("linux", legacy=True)[".config/zed/settings.json"])
        self.assertEqual(settings["theme"]["dark"], "One Dark")


if __name__ == "__main__":
    unittest.main(verbosity=2)
