#!/usr/bin/env python3
"""Render proxy selection in disposable homes without starting native services."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
class AgentProxy(unittest.TestCase):
    def test_platform_selection_and_private_runtime_ownership(self):
        with tempfile.TemporaryDirectory(prefix="proxy-config-") as tmp:
            root = Path(tmp)
            home = root / "home"
            source = root / "source"
            home.mkdir()
            source.mkdir()
            shutil.copytree(REPO / "home/dot_config/private_agent-proxy",
                            source / "dot_config/private_agent-proxy")
            shutil.copy2(REPO / "home/.chezmoiignore", source)
            env = dict(HOME=str(home), PATH=os.defpath,
                       XDG_STATE_HOME=str(root / "private state"),
                       XDG_CONFIG_HOME=str(root / "config"),
                       XDG_DATA_HOME=str(root / "data"),
                       XDG_CACHE_HOME=str(root / "cache"))
            for platform, managed, profiles, selected in (
                ("linux", True, ["hyprland-noctalia"], True),
                ("linux", False, ["hyprland-noctalia"], False),
                ("linux", True, ["common"], False),
                ("darwin", True, ["hyprland-noctalia"], False),
                ("windows", False, ["common"], False),
            ):
                data = dict(chezmoi=dict(os=platform), profiles=profiles,
                            ManagedByNimbus=managed)
                base = [CHEZMOI, "--source", str(source), "--destination",
                        str(home), "--config", str(root / "chezmoi.toml"),
                        "--persistent-state", str(root / "chezmoi.boltdb"),
                        "--skip-secrets", "--override-data", json.dumps(data)]
                result = subprocess.run(base + ["managed"], env=env,
                                        capture_output=True, text=True, check=True)
                self.assertEqual(".config/agent-proxy/config.yaml" in
                                 result.stdout, selected)
                self.assertNotIn("agent-proxy.env", result.stdout)
                self.assertNotIn("agent-proxy.json", result.stdout)
                if selected:
                    target = str(home / ".config/agent-proxy/config.yaml")
                    rendered = subprocess.run(base + ["cat", target], env=env,
                                              capture_output=True, text=True,
                                              check=True).stdout
                    self.assertIn("host: 127.0.0.1", rendered)
                    self.assertIn("admin_token: ${ADMIN_TOKEN}", rendered)
                    self.assertIn("key: ${PROXY_API_KEY}", rendered)
                    self.assertIn("model_mappings: []", rendered)
                    self.assertIn(str(root / "private state"), rendered)
                    self.assertNotIn("/home/pby", rendered)
                    self.assertEqual(rendered.count("enabled: true"), 5)


if __name__ == "__main__":
    unittest.main()
