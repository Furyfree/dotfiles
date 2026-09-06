#!/usr/bin/env python3
"""Validate Git configuration in temporary homes and local repositories only."""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "home/dot_config/git"
GIT = shutil.which("git")
CHEZMOI = shutil.which("chezmoi")


@unittest.skipUnless(GIT, "git is not installed")
class GitConfig(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-git-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        shutil.copytree(SOURCE, self.home / ".config/git")
        self.env = {
            "HOME": str(self.home), "USERPROFILE": str(self.home),
            "PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
            "GIT_ALLOW_PROTOCOL": "file", "GIT_PAGER": "cat",
        }
        self.repo = self.root / "repository"
        self.run_git("init", str(self.repo))

    def run_command(self, *args, cwd=None, input=None, expected=0):
        result = subprocess.run(args, cwd=cwd or self.root, env=self.env, input=input,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def run_git(self, *args, cwd=None, input=None, expected=0):
        return self.run_command(GIT, *args, cwd=cwd, input=input, expected=expected)

    def commit(self, repo, message):
        self.run_git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                     "commit", "--allow-empty", "-m", message, cwd=repo)
        return self.run_git("rev-parse", "HEAD", cwd=repo).strip()

    def test_native_discovery_and_config_scope(self):
        expected = {
            "user.useconfigonly": "true", "init.defaultbranch": "main",
            "fetch.prune": "true", "pull.ff": "only", "push.autosetupremote": "true",
            "merge.conflictstyle": "zdiff3", "alias.st": "status --short --branch",
            "alias.lg": "log --graph --oneline --decorate --all",
        }
        output = self.run_git("config", "--global", "--null", "--list")
        entries = [entry.partition("\n")[::2] for entry in output.split("\0") if entry]
        self.assertEqual(len(entries), len(expected))
        self.assertEqual(dict(entries), expected)
        # Git also discovers the XDG default when the environment variable is absent.
        del self.env["XDG_CONFIG_HOME"]
        self.assertEqual(self.run_git("config", "--get", "pull.ff").strip(), "only")

    def test_personal_override_and_identity(self):
        personal = self.home / ".gitconfig"
        personal.write_text('[user]\nname = Fixture\nemail = fixture@example.invalid\n'
                            '[pull]\nff = false\n')
        before = personal.read_bytes()
        self.assertEqual(self.run_git("config", "--get", "pull.ff").strip(), "false")
        self.assertEqual(self.run_git("config", "--get", "user.name").strip(), "Fixture")
        self.assertIn("fixture@example.invalid", self.run_git("var", "GIT_AUTHOR_IDENT", cwd=self.repo))
        self.assertEqual(personal.read_bytes(), before)

    def test_missing_identity_is_not_guessed(self):
        result = subprocess.run([GIT, "var", "GIT_AUTHOR_IDENT"], cwd=self.repo,
                                env=self.env, capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("auto-detection is disabled", result.stderr)

    def test_global_ignores_are_narrow(self):
        ignored = [".DS_Store", "sub/Thumbs.db", "Desktop.ini", "desktop.ini"]
        visible = [".env", ".vscode/settings.json", ".zed/settings.json", ".codex/config.toml",
                   "src/app.py", "notes.txt", "build/output", "Cargo.lock"]
        output = self.run_git("check-ignore", "--stdin", cwd=self.repo,
                              input="\n".join(ignored + visible) + "\n")
        self.assertEqual(output.splitlines(), ignored)

    def test_main_branch_and_readonly_aliases(self):
        self.assertEqual(self.run_git("symbolic-ref", "--short", "HEAD", cwd=self.repo).strip(), "main")
        self.commit(self.repo, "fixture")
        before = self.run_git("rev-parse", "HEAD", cwd=self.repo)
        self.assertEqual(self.run_git("st", cwd=self.repo),
                         self.run_git("status", "--short", "--branch", cwd=self.repo))
        self.assertEqual(self.run_git("lg", cwd=self.repo),
                         self.run_git("log", "--graph", "--oneline", "--decorate", "--all", cwd=self.repo))
        self.assertEqual(self.run_git("rev-parse", "HEAD", cwd=self.repo), before)

    def test_conflict_markers_include_the_base(self):
        paths = [self.root / name for name in ("ours", "base", "theirs")]
        for path in paths:
            path.write_text(f"shared\n{path.name}\nshared end\n")
        output = self.run_git("merge-file", "-p", *(str(path) for path in paths), expected=1)
        self.assertIn("|||||||", output)
        self.assertIn("\nbase\n", output)
        self.assertEqual(paths[0].read_text(), "shared\nours\nshared end\n")

    def test_push_prune_and_fast_forward_pull(self):
        remote = self.root / "remote.git"
        peer = self.root / "peer"
        self.run_git("init", "--bare", str(remote))
        self.commit(self.repo, "base")
        self.run_git("remote", "add", "origin", str(remote), cwd=self.repo)
        self.run_git("push", cwd=self.repo)
        self.assertEqual(self.run_git("rev-parse", "--abbrev-ref", "@{upstream}", cwd=self.repo).strip(),
                         "origin/main")
        self.run_git("clone", str(remote), str(peer))
        advanced = self.commit(peer, "remote advance")
        self.run_git("push", cwd=peer)
        self.run_git("pull", cwd=self.repo)
        self.assertEqual(self.run_git("rev-parse", "HEAD", cwd=self.repo).strip(), advanced)
        self.run_git("branch", "stale", cwd=peer)
        self.run_git("push", "origin", "stale", cwd=peer)
        self.run_git("fetch", cwd=self.repo)
        self.run_git("show-ref", "--verify", "refs/remotes/origin/stale", cwd=self.repo)
        self.run_git("branch", "stale", "origin/stale", cwd=self.repo)
        self.run_git("push", "origin", "--delete", "stale", cwd=peer)
        self.run_git("fetch", cwd=self.repo)
        self.run_git("show-ref", "--verify", "--quiet", "refs/remotes/origin/stale", cwd=self.repo, expected=1)
        self.run_git("show-ref", "--verify", "refs/heads/stale", cwd=self.repo)
        local_head = self.commit(self.repo, "local divergence")
        self.commit(peer, "remote divergence")
        self.run_git("push", cwd=peer)
        result = subprocess.run([GIT, "pull"], cwd=self.repo, env=self.env,
                                capture_output=True, text=True, timeout=20)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fast-forward", result.stderr)
        self.assertEqual(self.run_git("rev-parse", "HEAD", cwd=self.repo).strip(), local_head)

    @unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
    def test_platform_targets(self):
        for platform in ("linux", "darwin", "windows"):
            with self.subTest(platform=platform):
                output = self.run_command(
                    CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
                    "--config", str(self.root / "chezmoi.toml"), "--cache", str(self.root / "cache/chezmoi"),
                    "--persistent-state", str(self.root / "chezmoi-state.boltdb"), "--skip-secrets",
                    "--override-data", json.dumps({"chezmoi": {"os": platform},
                                                   "profiles": ["common"], "onePasswordSsh": False}),
                    "dump", "--format=json")
                entries = json.loads(output)
                files = {name: entry["contents"] for name, entry in entries.items()
                         if name.startswith(".config/git/") and entry["type"] == "file"}
                self.assertEqual(files, {f".config/git/{name}": (SOURCE / name).read_text()
                                         for name in ("config", "ignore")})
                self.assertNotIn(".gitconfig", entries)
                self.assertNotIn(".gitignore", entries)


if __name__ == "__main__":
    unittest.main(verbosity=2)
