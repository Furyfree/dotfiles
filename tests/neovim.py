#!/usr/bin/env python3
"""Render Neovim into disposable homes; the default suite never downloads plugins."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")
NVIM = shutil.which("nvim")
CANONICAL = REPO / "home/.chezmoitemplates/configs/nvim"


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
class Neovim(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-neovim-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.config = self.home / ".config/nvim"
        self.config.mkdir(parents=True)
        self.env = {
            "HOME": str(self.home), "PATH": "", "LANG": "C.UTF-8",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
        }

    def render(self, platform="linux"):
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--cache", str(self.root / "cache/chezmoi"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
            "--skip-secrets", "--override-data", json.dumps({
                "chezmoi": {"os": platform}, "profiles": ["common"],
                "onePasswordSsh": False,
            }), "dump", "--format=json",
        ], env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return {name: item["contents"] for name, item in json.loads(result.stdout).items()
                if item["type"] == "file"}

    def prepare(self):
        for name, content in self.render().items():
            if name.startswith(".config/nvim/"):
                target = self.home / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content)

    def nvim(self, case):
        if not NVIM:
            self.skipTest("neovim is not installed")
        self.env["DOTFILES_NVIM_CASE"] = case
        result = subprocess.run([
            NVIM, "--headless", "-u", "NONE", "-i", "NONE", "-l",
            str(REPO / "tests/fixtures/neovim.lua"),
        ], env=self.env, cwd=self.root, capture_output=True, text=True, timeout=180)
        output = re.sub(r"\x1b\[[0-9;]*m", "", result.stdout + result.stderr)
        # Remove Git's per-object progress, retaining task summaries and errors.
        output = "\n".join(line for line in output.splitlines()
                           if not re.search(r"remote: (?:Enumerating objects:|Counting objects:|Compressing objects:|Total )"
                                            r"|Receiving objects:|Resolving deltas:|Updating files:", line))
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("NEOVIM TEST OK", result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_targets_and_wrappers(self):
        for platform in ("linux", "darwin", "windows"):
            with self.subTest(platform=platform):
                files = self.render(platform)
                targets = {name for name in files
                           if name.startswith((".config/nvim/", "AppData/Local/nvim/"))}
                expected = {".config/nvim/" + name for name in (
                    "init.lua", "lazy-lock.json", "lua/config/options.lua", "lua/config/lazy.lua",
                    "lua/plugins/snacks.lua", "lua/plugins/which-key.lua", "lua/plugins/gitsigns.lua",
                    "lua/plugins/surround.lua", "lua/plugins/treesitter.lua",
                )}
                self.assertEqual(targets, set() if platform == "windows" else expected)
                for target in targets:
                    name = str(Path(target).relative_to(".config/nvim"))
                    self.assertEqual(files[target], (CANONICAL / name).read_text())
                    wrapper = REPO / "home/dot_config/nvim" / (name + ".tmpl")
                    self.assertEqual(wrapper.read_text().strip(),
                                     '{{- template "configs/nvim/' + name + '" . -}}')

    def test_plugin_lock(self):
        lock = json.loads((CANONICAL / "lazy-lock.json").read_text())
        self.assertEqual(set(lock), {"lazy.nvim", "snacks.nvim", "which-key.nvim",
                                     "gitsigns.nvim", "nvim-surround", "nvim-treesitter"})
        for entry in lock.values():
            self.assertRegex(entry["commit"], r"^[0-9a-f]{40}$")

    def test_offline_without_git(self):
        self.prepare()
        self.nvim("offline")
        self.assertFalse((self.root / "data/nvim/lazy").exists())

    def test_options_keymaps_and_missing_parsers(self):
        self.prepare()
        self.nvim("config")

    @unittest.skipUnless(shutil.which("git"), "git is not installed")
    def test_existing_manager_is_verified_before_loading(self):
        self.prepare()
        self.env.update({"PATH": os.defpath, "GIT_CONFIG_NOSYSTEM": "1",
                         "GIT_CONFIG_GLOBAL": os.devnull, "GIT_TERMINAL_PROMPT": "0"})
        manager = self.root / "data/nvim/lazy/lazy.nvim"
        module = manager / "lua/lazy/init.lua"
        module.parent.mkdir(parents=True)
        module.write_text("vim.g.fixture_manager_loaded = true\nreturn { setup = function() end }\n")
        for args in (("init",), ("add", "."),
                     ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                      "commit", "-m", "Existing manager fixture")):
            result = subprocess.run([shutil.which("git"), "-C", str(manager), *args],
                                    env=self.env, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
        original_head = (manager / ".git/HEAD").read_text()
        # The real local checkout differs from the canonical locked revision.
        self.nvim("existing_mismatch")
        self.assertEqual((manager / ".git/HEAD").read_text(), original_head)
        revision = subprocess.run([shutil.which("git"), "-C", str(manager), "rev-parse", "HEAD"],
                                  env=self.env, capture_output=True, text=True, timeout=20)
        self.assertEqual(revision.returncode, 0, revision.stderr)
        lockfile = self.config / "lazy-lock.json"
        lock = json.loads(lockfile.read_text())
        lock["lazy.nvim"]["commit"] = revision.stdout.strip()
        lockfile.write_text(json.dumps(lock))
        self.nvim("existing_match")
        self.env["PATH"] = ""
        self.nvim("existing_no_git")
        self.env["PATH"] = os.defpath
        (manager / ".git").rename(manager / "saved-git")
        self.nvim("existing_mismatch")

    def test_undo_permissions_and_persistence(self):
        self.prepare()
        undo = self.root / "state/nvim/undo"
        undo.mkdir(parents=True, mode=0o755)
        self.nvim("write_undo")
        self.assertEqual(undo.stat().st_mode & 0o777, 0o700)
        self.assertTrue(list(undo.iterdir()))
        self.nvim("read_undo")

    def test_undo_failure_keeps_editing_usable(self):
        self.prepare()
        undo = self.root / "state/nvim/undo"
        undo.parent.mkdir(parents=True)
        undo.write_text("not a directory")
        self.nvim("undo_failure")
        self.assertEqual(undo.read_text(), "not a directory")

    def test_failed_bootstrap_keeps_editing_usable(self):
        self.prepare()
        self.nvim("bootstrap_failure")

    def test_failed_checkout_never_activates_partial_bootstrap(self):
        self.prepare()
        self.nvim("checkout_failure")
        self.assertFalse((self.root / "data/nvim/lazy/lazy.nvim").exists())
        self.assertTrue((self.root / "data/nvim/lazy/lazy.nvim.bootstrap").exists())

    def test_invalid_lock_keeps_editing_usable(self):
        self.prepare()
        (self.config / "lazy-lock.json").write_text("{}")
        self.nvim("invalid_lock")

    @unittest.skipUnless(os.environ.get("DOTFILES_NVIM_INTEGRATION") == "1",
                         "opt-in plugin download/startup test")
    def test_real_plugins_in_disposable_home(self):
        self.prepare()
        # No inherited credentials, agent sockets, runtime paths, or Git config.
        self.env["PATH"] = os.defpath
        self.env["GIT_CONFIG_NOSYSTEM"] = "1"
        self.env["GIT_CONFIG_GLOBAL"] = os.devnull
        self.env["GIT_TERMINAL_PROMPT"] = "0"
        project = self.root / "project with spaces"
        project.mkdir()
        (project / "sample.lua").write_text("local message = 'before'\n")
        (project / ".hidden.lua").write_text("return true\n")
        (project / ".gitignore").write_text("ignored.txt\n")
        (project / "ignored.txt").write_text("not a search result\n")
        for args in (("init",), ("add", "."),
                     ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                      "commit", "-m", "Fixture")):
            result = subprocess.run([shutil.which("git"), "-C", str(project), *args],
                                    env=self.env, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.env["DOTFILES_NVIM_PROJECT"] = str(project)
        self.nvim("integration")
        self.nvim("integration")  # Reuse and verify the installed pinned manager.
        actual = json.loads((self.config / "lazy-lock.json").read_text())
        self.assertEqual(actual, json.loads((CANONICAL / "lazy-lock.json").read_text()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
