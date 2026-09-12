#!/usr/bin/env python3
"""Check Zeron launcher selection and native asset updates in a temporary home."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")
ASSETS = {
    ".local/share/applications/zeron.desktop":
        "dot_local/share/applications/symlink_zeron.desktop.tmpl",
    ".local/share/icons/hicolor/512x512/apps/zeron.png":
        "dot_local/share/icons/hicolor/512x512/apps/symlink_zeron.png.tmpl",
}
HOOK = REPO / "home/run_after_refresh-zeron-icon.sh.tmpl"


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
class Zeron(unittest.TestCase):
    def test_profile_selection_and_native_asset_updates(self):
        with tempfile.TemporaryDirectory(prefix="dotfiles-zeron-") as temp:
            root = Path(temp)
            source = root / "source"
            source.mkdir()
            for name in [".chezmoiignore", *ASSETS.values()]:
                target = source / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(REPO / "home" / name, target)
            home = root / "home with spaces"
            home.mkdir()
            env = {"HOME": str(home), "USERPROFILE": str(home), "PATH": "",
                   "XDG_CONFIG_HOME": str(root / "config"),
                   "XDG_DATA_HOME": str(root / "data"),
                   "XDG_CACHE_HOME": str(root / "cache"),
                   "XDG_STATE_HOME": str(root / "state")}

            def run(data, *args):
                result = subprocess.run([
                    CHEZMOI, "--source", str(source), "--destination", str(home),
                    "--config", str(root / "chezmoi.toml"),
                    "--cache", str(root / "cache/chezmoi"),
                    "--persistent-state", str(root / "chezmoi-state.boltdb"),
                    "--skip-secrets", "--override-data", json.dumps(data), *args,
                ], env=env, cwd=root, text=True, capture_output=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout

            for platform in ("linux", "darwin", "windows"):
                for managed in (False, True):
                    for development in (False, True):
                        data = {"chezmoi": {"os": platform}, "ManagedByNimbus": managed,
                                "profiles": ["development"] if development else ["common"]}
                        with self.subTest(data=data):
                            entries = json.loads(run(data, "dump", "--format=json"))
                            for target in ASSETS:
                                self.assertEqual(target in entries,
                                                 platform == "linux" and development)
                            hook = run(data, "execute-template", HOOK.read_text())
                            self.assertEqual(bool(hook.strip()),
                                             platform == "linux" and development)

            # Applying the links before installation is valid. A native install
            # or version switch supplies their targets without another apply.
            data = {"chezmoi": {"os": "linux"}, "ManagedByNimbus": False,
                    "profiles": ["development"]}
            run(data, "apply", "--exclude=scripts")
            hook = run(data, "execute-template", HOOK.read_text())
            cache_tool = root / "bin/gtk-update-icon-cache"
            cache_tool.parent.mkdir()
            log = root / "cache-call.json"
            cache_tool.write_text(f"#!{sys.executable}\n" +
                                  "import json, os, pathlib, sys\n"
                                  "pathlib.Path(os.environ['FAKE_LOG']).write_text("
                                  "json.dumps(sys.argv[1:]))\n"
                                  "sys.exit(int(os.environ.get('FAKE_EXIT', '0')))\n")
            cache_tool.chmod(0o755)
            hook_env = env | {"PATH": str(cache_tool.parent), "FAKE_LOG": str(log)}
            # A link whose vendor target is not installed needs no cache write.
            subprocess.run(["/bin/sh"], input=hook, text=True, env=hook_env, check=True)
            self.assertFalse(log.exists())
            for target in ASSETS:
                self.assertTrue((home / target).is_symlink())
                self.assertFalse((home / target).exists())
            app = home / ".zeron/app"
            for version in ("first", "second"):
                (app / version).mkdir(parents=True)
                for target in ASSETS:
                    (app / version / Path(target).name).write_text(version)
                current = app / "current"
                if current.is_symlink():
                    current.unlink()
                current.symlink_to(version)
                for target in ASSETS:
                    self.assertEqual((home / target).read_text(), version)
            # No cache utility is also a supported no-op on standalone systems.
            subprocess.run(["/bin/sh"], input=hook, text=True, env=env, check=True)
            self.assertFalse(log.exists())
            subprocess.run(["/bin/sh"], input=hook, text=True, env=hook_env, check=True)
            self.assertEqual(json.loads(log.read_text()), [
                "--force", "--ignore-theme-index", "--index-only",
                str(home / ".local/share/icons/hicolor")])
            failed = subprocess.run(["/bin/sh"], input=hook, text=True,
                                    env=hook_env | {"FAKE_EXIT": "23"})
            self.assertEqual(failed.returncode, 23)
            run(data, "verify", *(str(home / p) for p in ASSETS))


if __name__ == "__main__":
    unittest.main(verbosity=2)
