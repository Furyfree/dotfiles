#!/usr/bin/env python3
"""Exercise sourced session settings without changing any user manager."""

import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UwsmEnvironment(unittest.TestCase):
    def test_paths_defaults_and_inherited_choices(self):
        for overrides in ({}, {"MISE_DATA_DIR": "/tools with spaces/mise",
                               "EDITOR": "vim", "VISUAL": "code --wait"},
                          {"XDG_DATA_HOME": "/data with spaces", "PATH": "/custom/bin:/usr/bin"}):
            with self.subTest(overrides=overrides):
                env = {"HOME": "/home/example with spaces", "PATH": "", **overrides}
                result = subprocess.run([
                    "/bin/sh", "-c",
                    '. "$1"; . "$1"; . "$2"; exec /usr/bin/python3 -c '
                    "'import os,json; print(json.dumps(dict(os.environ)))'", "sh",
                    str(ROOT / "home/dot_config/uwsm/env"),
                    str(ROOT / "home/dot_config/uwsm/env-hyprland"),
                ], env=env, capture_output=True, text=True, check=True)
                actual = json.loads(result.stdout)
                paths = actual["PATH"].split(":")
                data = overrides.get("MISE_DATA_DIR", overrides.get(
                    "XDG_DATA_HOME", env["HOME"] + "/.local/share") + "/mise")
                self.assertEqual(paths.count(data + "/shims"), 1)
                self.assertEqual(paths.count(env["HOME"] + "/.local/bin"), 1)
                self.assertIn("/usr/bin", paths)
                if overrides.get("PATH"):
                    self.assertIn("/custom/bin", paths)
                self.assertEqual(actual["EDITOR"], overrides.get("EDITOR", "nvim"))
                self.assertEqual(actual["VISUAL"], overrides.get("VISUAL", actual["EDITOR"]))
                self.assertEqual(actual["QT_QPA_PLATFORM"], "wayland;xcb")
                self.assertEqual(actual["GTK_IM_MODULE"], "simple")
                self.assertEqual(actual["XCURSOR_SIZE"], actual["HYPRCURSOR_SIZE"])
                self.assertEqual(actual["LOCAL_NOTEBOOK_DEV"], "1")
                self.assertNotIn("WAYLAND_DISPLAY", actual)
                self.assertNotIn("XDG_SESSION_ID", actual)
                self.assertNotIn("uwsm_directory", actual)


if __name__ == "__main__":
    unittest.main()
