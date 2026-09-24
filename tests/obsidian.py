"""Check Obsidian vault settings and its Flatpak override without touching live state."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")
VAULT = "Projects/dtu-bachelor/.obsidian"


def strict_json(text):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique_keys)


@unittest.skipUnless(CHEZMOI and shutil.which("sh"), "chezmoi or sh is not installed")
class Obsidian(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-obsidian-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        (self.home / VAULT).mkdir(parents=True)
        # A stub pgrep decides whether Obsidian looks open, independent of the real desktop.
        self.bin = self.root / "bin"
        self.bin.mkdir()
        os.symlink(shutil.which("sh"), self.bin / "sh")
        self.set_obsidian_open(False)

    def set_obsidian_open(self, is_open):
        stub = self.bin / "pgrep"
        stub.write_text(f"#!{shutil.which('sh')}\nexit {0 if is_open else 1}\n")
        stub.chmod(0o755)

    def chezmoi(self, *args, platform="linux"):
        data = {"chezmoi": {"os": platform}, "profiles": ["common", "hyprland-noctalia"], "onePasswordSsh": False}
        env = {"HOME": str(self.home), "PATH": str(self.bin),
               "XDG_CONFIG_HOME": str(self.home / ".config"), "XDG_CACHE_HOME": str(self.root / "cache")}
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"), "--cache", str(self.root / "cache/chezmoi"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"), "--skip-secrets",
            "--override-data", json.dumps(data), *args,
        ], env=env, cwd=self.root, capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def cat(self, target):
        return self.chezmoi("cat", str(self.home / target)).stdout

    def test_settings_are_strict_json_in_obsidian_format(self):
        for name in ("app.json", "appearance.json", "hotkeys.json", "plugins/obsidian-hider/data.json",
                     "plugins/omnisearch/data.json", "plugins/tinymist/data.json"):
            with self.subTest(name=name):
                text = self.cat(f"{VAULT}/{name}")
                strict_json(text)
                if name != "hotkeys.json":
                    # Obsidian rewrites these without a final newline; matching avoids apply prompts.
                    self.assertEqual(text, json.dumps(json.loads(text), indent=2))

    def test_hotkeys_do_not_share_a_key(self):
        hotkeys = strict_json(self.cat(f"{VAULT}/hotkeys.json"))
        seen = {}
        for command, bindings in hotkeys.items():
            for binding in bindings:
                key = (tuple(sorted(binding["modifiers"])), binding["key"])
                self.assertNotIn(key, seen, f"{command} and {seen.get(key)} share {key}")
                seen[key] = command

    def test_workspace_keeps_tabs_and_resets_sidebars(self):
        path = self.home / VAULT / "workspace.json"
        local = {"main": {"id": "local-main", "type": "split", "children": []},
                 "left": {"id": "old", "children": []}, "right": {"id": "old", "children": []},
                 "active": "local-main", "lastOpenFiles": ["notes.md"], "left-ribbon": {"hiddenItems": {}}}
        path.write_text(json.dumps(local))
        workspace = strict_json(self.cat(f"{VAULT}/workspace.json"))
        for key in ("main", "active", "lastOpenFiles", "left-ribbon"):
            self.assertEqual(workspace[key], local[key])
        def leaves(side):
            return [leaf["state"]["type"] for tabs in workspace[side]["children"] for leaf in tabs["children"]]
        self.assertEqual(leaves("left"), ["agent-client-chat-view"])
        self.assertEqual(leaves("right"), ["file-explorer", "search", "outline", "git-view"])
        self.assertEqual(path.read_text(), json.dumps(local))

    def test_workspace_is_created_when_missing(self):
        workspace = strict_json(self.cat(f"{VAULT}/workspace.json"))
        self.assertEqual(set(workspace), {"main", "left", "right", "active", "lastOpenFiles"})

    def test_workspace_is_left_alone_while_obsidian_runs(self):
        path = self.home / VAULT / "workspace.json"
        path.write_text('{"main": {}, "left": {"id": "mine"}}')
        self.set_obsidian_open(True)
        result = self.chezmoi("cat", str(path))
        self.assertEqual(result.stdout, path.read_text())
        self.assertIn("Obsidian is open", result.stderr)

    def test_vault_settings_need_the_vault_and_skip_windows(self):
        self.assertIn(VAULT, self.chezmoi("managed", "--include=files").stdout)
        self.assertNotIn(VAULT, self.chezmoi("managed", "--include=files", platform="windows").stdout)
        shutil.rmtree(self.home / "Projects")
        self.assertNotIn(VAULT, self.chezmoi("managed", "--include=files").stdout)

    def test_flatpak_override_uses_home_mise_and_git(self):
        text = self.cat(".local/share/flatpak/overrides/md.obsidian.Obsidian")
        env = dict(line.split("=", 1) for line in text.splitlines()[1:])
        self.assertEqual(text.splitlines()[0], "[Environment]")
        self.assertTrue(env["PATH"].startswith(f"{self.home}/.local/share/mise/shims:"))
        self.assertEqual(env["GIT_CONFIG_GLOBAL"], f"{self.home}/.config/git/config")
        self.assertEqual(env["GIT_CONFIG_KEY_0"], "gpg.ssh.program")


if __name__ == "__main__":
    unittest.main(verbosity=2)
