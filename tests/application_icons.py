#!/usr/bin/env python3
"""Exercise icon discovery in disposable homes without changing the desktop."""

import configparser
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")
CACHE_TOOL = shutil.which("gtk-update-icon-cache")
THEME = ".local/share/icons/hicolor"


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
class ApplicationIcons(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-icons-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.source = self.root / "source"
        self.source.mkdir()
        for name in ("dot_local/share/icons", ".chezmoitemplates/configs/icons"):
            shutil.copytree(REPO / "home" / name, self.source / name)
        shutil.copy2(REPO / "home/.chezmoiignore", self.source)
        self.env = dict(HOME=str(self.home), PATH=os.defpath,
                        XDG_CONFIG_HOME=str(self.root / "config"),
                        XDG_CACHE_HOME=str(self.root / "cache"),
                        XDG_DATA_HOME=str(self.home / ".local/share"),
                        XDG_STATE_HOME=str(self.root / "state"))

    def run_chezmoi(self, *args, platform="linux", managed=True, **extra):
        data = dict(chezmoi=dict(os=platform), profiles=["common"],
                    ManagedByNimbus=managed, **extra)
        result = subprocess.run([
            CHEZMOI, "--source", str(self.source), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--persistent-state", str(self.root / "chezmoi.boltdb"),
            "--skip-secrets", "--override-data", json.dumps(data), *args,
        ], env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def hook(self):
        return self.run_chezmoi("execute-template", (REPO / "home" /
            "run_after_refresh-application-icons.sh.tmpl").read_text())

    def test_extending_vendor_index_preserves_other_sizes_and_is_idempotent(self):
        vendor = ("[Icon Theme]\nName=Vendor\nComment=Fixture\nHidden=true\n"
                  "Directories=16x16/apps,scalable/apps\n"
                  "[16x16/apps]\nSize=16\nType=Fixed\n"
                  "[scalable/apps]\nSize=48\nType=Scalable\nMinSize=1\nMaxSize=512\n")
        for base in ("", vendor):
            rendered = self.run_chezmoi("execute-template",
                '{{ template "configs/icons/hicolor.tmpl" .fixtureIndex }}', fixtureIndex=base)
            config = configparser.ConfigParser(interpolation=None)
            config.read_string(rendered)
            directories = config["Icon Theme"]["Directories"].split(",")
            self.assertEqual(len(directories), len(set(directories)))
            for name in ("512x512/apps", "1024x1024/apps"):
                self.assertIn(name, directories)
            if base:
                self.assertEqual(config["scalable/apps"]["MaxSize"], "512")
                self.assertIn("16x16/apps", directories)
                self.assertEqual(config["Icon Theme"]["Name"], "Vendor")
            again = self.run_chezmoi("execute-template",
                '{{ template "configs/icons/hicolor.tmpl" .fixtureIndex }}', fixtureIndex=rendered)
            self.assertEqual(rendered, again)

    def test_platform_gates_and_package_links(self):
        for platform in ("linux", "darwin", "windows"):
            for managed in (False, True):
                entries = json.loads(self.run_chezmoi("dump", "--format=json",
                                    platform=platform, managed=managed))
                for name in ("index.theme", "1024x1024/apps/t3code.png", "1024x1024/apps/yazi.png"):
                    self.assertEqual(f"{THEME}/{name}" in entries, platform == "linux")
                self.assertEqual(f"{THEME}/512x512/apps/nimbus-webapp-google-maps.png" in entries,
                                 platform == "linux" and managed)
                self.assertNotIn(f"{THEME}/512x512/apps/zeron.png", entries)
        self.run_chezmoi("apply", "--exclude=scripts")
        for name in ("t3code", "yazi"):
            link = self.home / THEME / f"1024x1024/apps/{name}.png"
            self.assertTrue(link.is_symlink())
            self.assertEqual(str(link.readlink()), f"/usr/share/icons/hicolor/1024x1024/apps/{name}.png")

    @unittest.skipUnless(CACHE_TOOL, "gtk-update-icon-cache is not installed")
    def test_native_discovery_without_zeron_and_repeated_apply(self):
        self.run_chezmoi("apply", "--exclude=scripts")
        theme = self.home / THEME
        # Simulate packages not installed yet without touching package-owned files.
        for name in ("t3code", "yazi"):
            link = theme / f"1024x1024/apps/{name}.png"
            link.unlink()
            link.symlink_to(self.root / "absent" / f"{name}.png")
        unrelated = theme / "512x512/apps/unrelated.png"
        shutil.copy2(theme / "512x512/apps/nimbus-webapp-google-maps.png", unrelated)
        original = unrelated.read_bytes()
        subprocess.run(["/bin/sh"], input=self.hook(), text=True, env=self.env, check=True)
        self.assertTrue((theme / "icon-theme.cache").exists())
        probe = subprocess.run(["/usr/bin/python3", "-c", "import gi; gi.require_version('Gtk','3.0')"],
                               env=self.env, capture_output=True)
        if probe.returncode == 0:
            script = """import gi, sys
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
t=Gtk.IconTheme.new()
t.set_search_path([sys.argv[1]])
t.set_custom_theme('hicolor')
for name in ['nimbus-webapp-google-maps','nimbus-webapp-fotmob','unrelated']:
    assert t.lookup_icon(name,48,0) is not None, name
"""
            subprocess.run(["/usr/bin/python3", "-c", script, str(theme.parent)],
                           env=self.env, check=True)
        for name in ("t3code", "yazi"):
            link = theme / f"1024x1024/apps/{name}.png"
            link.unlink()
            link.symlink_to(f"/usr/share/icons/hicolor/1024x1024/apps/{name}.png")
        self.run_chezmoi("apply", "--exclude=scripts")
        subprocess.run(["/bin/sh"], input=self.hook(), text=True, env=self.env, check=True)
        self.assertEqual(unrelated.read_bytes(), original)
        self.assertEqual(self.run_chezmoi("diff"), "")
        self.run_chezmoi("verify", "--exclude=scripts")


if __name__ == "__main__":
    unittest.main(verbosity=2)
