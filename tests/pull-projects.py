"""Run pull-projects against throwaway repositories; real projects and Git config stay untouched."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "home/dot_local/bin/executable_pull-projects"


@unittest.skipUnless(shutil.which("git") and shutil.which("sh"), "git or sh is not installed")
class PullProjects(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-pull-projects-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "home with spaces"
        self.env = {"HOME": str(self.home), "PATH": "/usr/bin:/bin", "LANG": "C",
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
        subprocess.run(["sh", str(REPO / "tests/fixtures/git-projects"), str(self.home)],
                       env=self.env, check=True, capture_output=True, timeout=30)

    def run_script(self, *args):
        return subprocess.run(["sh", str(SCRIPT), *args], env=self.env,
                              capture_output=True, text=True, timeout=30, check=False)

    def head(self, name):
        return subprocess.run(["git", "-C", str(self.home / "Projects" / name), "rev-parse", "HEAD"],
                              env=self.env, check=True, capture_output=True, text=True).stdout

    def test_moves_only_clean_repositories(self):
        before = {name: self.head(name) for name in ("dirty", "diverged", "no-upstream")}
        result = self.run_script()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "behind: updated", "current: up to date", "dirty: skipped: uncommitted changes",
            "diverged: failed: not a fast-forward or fetch error", "no-upstream: skipped: no upstream"])
        self.assertEqual(self.head("behind"), self.head("current"))
        self.assertEqual({name: self.head(name) for name in before}, before)
        self.assertEqual((self.home / "Projects/dirty/untracked").read_text(), "draft\n")

    def test_rejects_arguments(self):
        self.assertEqual(self.run_script("unexpected").returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
