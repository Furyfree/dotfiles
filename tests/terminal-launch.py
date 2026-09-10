#!/usr/bin/env python3
"""Check the native terminal launcher without starting a terminal or app."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


XTE = shutil.which("xdg-terminal-exec")


class TerminalLaunch(unittest.TestCase):
    @unittest.skipUnless(XTE, "xdg-terminal-exec is not installed")
    def test_native_launcher_preserves_command_arguments(self):
        with tempfile.TemporaryDirectory(prefix="dotfiles-terminal-") as tmp:
            root = Path(tmp)
            for name in ("home", "bin", "config", "data/applications", "cache", "system"):
                (root / name).mkdir(parents=True, exist_ok=True)
            terminal = root / "bin/fake-terminal"
            log = root / "argv.json"
            terminal.write_text(f"#!{sys.executable}\nimport json,sys\nfrom pathlib import Path\n"
                                f"Path({str(log)!r}).write_text(json.dumps(sys.argv[1:]))\n")
            terminal.chmod(0o755)
            (root / "config/xdg-terminals.list").write_text("fake.desktop\n")
            (root / "data/applications/fake.desktop").write_text(
                "[Desktop Entry]\nType=Application\nName=Fake terminal\n"
                "Exec=fake-terminal\nCategories=TerminalEmulator;\nX-TerminalArgExec=-e\n")
            env = {"HOME": str(root / "home"), "PATH": str(root / "bin") + ":/usr/bin:/bin",
                   "XDG_CONFIG_HOME": str(root / "config"), "XDG_CONFIG_DIRS": str(root / "system"),
                   "XDG_DATA_HOME": str(root / "data"), "XDG_DATA_DIRS": str(root / "system"),
                   "XDG_CACHE_HOME": str(root / "cache"), "XDG_CURRENT_DESKTOP": "Hyprland"}
            args = ["btop", "argument with spaces", "$(touch bad)", "--flag=value"]
            result = subprocess.run([XTE, *args], env=env, cwd=root,
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(log.read_text()), ["-e", *args])
            self.assertFalse((root / "bad").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
