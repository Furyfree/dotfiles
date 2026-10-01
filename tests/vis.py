"""Drive the real Vis with this configuration in a pseudo-terminal and disposable home."""

import fcntl
import os
import pty
import re
import select
import shutil
import struct
import subprocess
import tempfile
import termios
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VIS = shutil.which("vis")
ESCAPES = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07]*\x07|\x1b[()][0-9A-B]|\x1b[=>]")
ERRORS = re.compile(r"attempt to|stack traceback|module '[^']+' not found|\.lua:\d+:")


class Terminal:
    def __init__(self, argv, env, cwd):
        # Popen, not pty.fork: forking a threaded pytest worker can deadlock.
        self.fd, child = pty.openpty()
        fcntl.ioctl(child, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 120, 0, 0))
        self.process = subprocess.Popen(argv, env=env, cwd=cwd, stdin=child, stdout=child,
                                        stderr=child, start_new_session=True)
        os.close(child)
        self.output = b""

    def read(self, seconds):
        deadline = time.monotonic() + seconds
        while (left := deadline - time.monotonic()) > 0:
            if select.select([self.fd], [], [], min(left, 0.05))[0]:
                try:
                    self.output += os.read(self.fd, 65536)
                except OSError:
                    return

    def screen(self, start=0):
        return ESCAPES.sub(" ", self.output[start:].decode(errors="replace"))

    def wait(self, text, start=0, seconds=5):
        deadline = time.monotonic() + seconds
        while text not in self.screen(start) and time.monotonic() < deadline:
            self.read(0.05)
        return text in self.screen(start)

    def send(self, keys, expect=None):
        start = len(self.output)
        os.write(self.fd, keys.encode())
        if expect is None:
            self.read(0.3)
        elif not self.wait(expect, start):
            raise AssertionError(f"{expect!r} not shown after {keys!r}:\n{self.screen(start)[-800:]}")
        return self.screen(start)

    def close(self):
        try:
            os.write(self.fd, b"\x1b:qa!\r")
            self.read(0.5)
        except OSError:
            pass
        self.process.kill()
        self.process.wait()
        os.close(self.fd)


@unittest.skipUnless(VIS, "vis is not installed")
class Vis(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="dotfiles-vis-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        shutil.copytree(REPO / "home/dot_config/vis", self.root / "config/vis")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        # Records copies instead of touching the desktop clipboard.
        clipboard = self.bin / "vis-clipboard"
        clipboard.write_text('#!/bin/sh\ncase "$1" in --copy) cat > "$CLIPBOARD_FILE" ;;'
                             ' --paste) cat "$CLIPBOARD_FILE" 2>/dev/null ;; esac\n')
        clipboard.chmod(0o755)
        self.project = self.root / "project with space"
        (self.project / "sub").mkdir(parents=True)
        (self.project / "sub/inner.txt").write_text("inner\n")
        (self.project / ".hidden").write_text("hidden\n")
        (self.project / "notes.txt").write_text(
            "alpha\nneedle one\nbeta\nneedle two\ngamma\nneedle three\ndelta\n")
        self.env = {
            "HOME": str(self.root), "TERM": "xterm-256color", "LANG": "C.UTF-8",
            "PATH": f"{self.bin}{os.pathsep}{os.environ.get('PATH', os.defpath)}",
            "XDG_CONFIG_HOME": str(self.root / "config"), "XDG_CACHE_HOME": str(self.root / "cache"),
            "CLIPBOARD_FILE": str(self.root / "clipboard"),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
        }

    def start(self, *argv):
        terminal = Terminal(list(argv), self.env, self.project)
        self.addCleanup(terminal.close)
        self.assertTrue(terminal.wait("NORMAL"), terminal.screen())
        return terminal

    def assertNoErrors(self, terminal):
        self.assertIsNone(ERRORS.search(terminal.screen()), terminal.screen()[-800:])

    def test_vim_search_direction(self):
        vis = self.start(VIS, "notes.txt")
        # Three matches, so wrapping cannot hide a wrong direction.
        vis.send("G?needle\r", " 6:1 ")
        vis.send("n", " 4:1 ")
        vis.send("N", " 6:1 ")
        self.assertNoErrors(vis)

    def test_yank_reaches_clipboard(self):
        vis = self.start(VIS, "notes.txt")
        vis.send("jwyiw", "Copied")
        self.assertEqual((self.root / "clipboard").read_text(), "one")
        self.assertNoErrors(vis)

    def test_explore_lists_opens_and_goes_up(self):
        vis = self.start(VIS, f'+Explore "{self.project}/sub/.."')
        screen = vis.screen()
        # The cursor's highlight splits "../" on screen; the title names the directory.
        for entry in (f"{self.project}/ ", "sub/", ".hidden", "notes.txt"):
            self.assertIn(entry, screen)
        vis.send("/sub\r\r", "inner.txt")
        vis.send("-", " 2:1 ")  # back on sub/
        vis.send("/notes\r\r", "needle one")
        # The listing never counts as an unsaved change, so :q just quits.
        vis.send(":q\r")
        self.assertEqual(vis.process.wait(timeout=5), 0)
        self.assertNoErrors(vis)

    @unittest.skipUnless(shutil.which("zsh"), "zsh is not installed")
    def test_shell_function_opens_directory(self):
        functions = REPO / "home/dot_config/zsh/conf.d/functions.zsh"
        vis = self.start("zsh", "-fc", f'source "{functions}"; vis "$1"', "zsh", str(self.project))
        self.assertIn("sub/", vis.screen())
        self.assertNoErrors(vis)

    @unittest.skipUnless(shutil.which("git"), "git is not installed")
    def test_git_hunks_include_unsaved_edits(self):
        for args in (("init", "-q"), ("add", "notes.txt"),
                     ("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                      "commit", "-qm", "fixture")):
            subprocess.run(["git", *args], cwd=self.project, env=self.env, check=True)
        vis = self.start(VIS, "notes.txt")
        # Escape needs a pause, or Vis reads Escape+g as Alt-g.
        vis.send("3Gccchanged\x1b", " 3:8 ")
        vis.send("5Gccchanged\x1b", " 5:8 ")
        vis.send("gg]h", " 3:1 ")
        vis.send("]h", " 5:1 ")
        vis.send("]h", " 3:1 ")
        vis.send("[h", " 5:1 ")
        vis.send(" ghp", "+changed")
        self.assertNoErrors(vis)
