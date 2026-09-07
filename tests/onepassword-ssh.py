#!/usr/bin/env python3
"""Check prepared SSH references without accessing 1Password or live SSH state."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest


REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "home"
CHEZMOI = shutil.which("chezmoi")


class OnePasswordSsh(unittest.TestCase):
    def test_document_reference(self):
        # Inspect the expression; evaluating it would retrieve private contents.
        template = SOURCE / "private_dot_ssh/private_config.tmpl"
        self.assertEqual(template.read_text().strip(),
                         '{{ onepasswordDocument "3223bqk2tzqdut7gdhiqjyqj34" }}')

    def test_agent_selects_only_the_two_intended_keys(self):
        config = tomllib.loads((SOURCE / ".chezmoitemplates/configs/1password/ssh/agent.toml").read_text())
        self.assertEqual(config, {"ssh-keys": [
            {"item": "n6imsp5vfs5nmlt5rmxgs6zdci"},
            {"item": "3ppqekfxnmjtg2iapnr5d7gewi"},
        ]})
        for path in ("dot_config/1Password/ssh/agent.toml.tmpl",
                     "AppData/Local/1Password/config/ssh/agent.toml.tmpl"):
            self.assertEqual((SOURCE / path).read_text().strip(),
                             '{{- template "configs/1password/ssh/agent.toml" . -}}')

    @unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
    def test_placeholder_targets_remain_ignored(self):
        with tempfile.TemporaryDirectory(prefix="dotfiles-ssh-") as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            # No op binary, credentials, or real user configuration are available.
            env = {"HOME": str(home), "USERPROFILE": str(home), "PATH": "",
                   "XDG_CONFIG_HOME": str(home / ".config"),
                   "XDG_CACHE_HOME": str(root / "cache"),
                   "XDG_DATA_HOME": str(root / "data"),
                   "XDG_STATE_HOME": str(root / "state")}
            for platform in ("linux", "darwin", "windows"):
                for enabled in (False, True):
                    with self.subTest(platform=platform, enabled=enabled):
                        result = subprocess.run([
                            CHEZMOI, "--source", str(REPO), "--destination", str(home),
                            "--config", str(root / "chezmoi.toml"),
                            "--cache", str(root / "cache/chezmoi"),
                            "--persistent-state", str(root / "chezmoi-state.boltdb"),
                            "--override-data", json.dumps({"chezmoi": {"os": platform},
                                "profiles": ["common"], "onePasswordSsh": enabled}),
                            "dump", "--format=json",
                        ], cwd=root, env=env, text=True, capture_output=True, timeout=20)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        paths = json.loads(result.stdout)
                        for target in (".ssh/config", ".config/1Password/ssh/agent.toml",
                                       "AppData/Local/1Password/config/ssh/agent.toml"):
                            self.assertNotIn(target, paths)


if __name__ == "__main__":
    unittest.main(verbosity=2)
