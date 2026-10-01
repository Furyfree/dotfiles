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
        with (self.root / "config/vis/visrc.lua").open("a") as config:
            config.write("""
vis:command_register('WindowState', function()
  local count = 0
  for _ in vis:windows() do count = count + 1 end
  vis:info(count .. ' windows, ' ..
    (vis.ui.layout == vis.ui.layouts.VERTICAL and 'vertical' or 'horizontal'))
  return true
end)
""")
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

    def test_explorer_returns_to_saved_file_and_browsed_directory(self):
        notes = self.project / "notes.txt"
        vis = self.start(VIS, "notes.txt")
        vis.send("3Gccchanged\x1b", " 3:8 ")
        vis.send(":w\r")
        vis.send("5Gll", " 5:3 ")
        vis.send(" e", "sub/")
        vis.send(":WindowState\r", "1 windows, horizontal")
        vis.send("/sub\rl", "inner.txt")
        vis.send("/inner\r")
        vis.send(" e", " 5:3 ")
        vis.send(":WindowState\r", "1 windows, horizontal")
        self.assertIn("changed\n", notes.read_text())
        vis.send(" e", " 2:1 ")
        vis.send("l", "sub/inner.txt")
        vis.send(":WindowState\r", "1 windows, horizontal")
        self.assertNoErrors(vis)

    def test_explorer_selects_current_file_and_closes_after_opening(self):
        vis = self.start(VIS, "notes.txt")
        vis.send("5G", " 5:1 ")
        vis.send(" e", "sub/")
        vis.send("l", " 5:1 ")
        vis.send(":WindowState\r", "1 windows, horizontal")
        vis.send(" e", "sub/")
        vis.send("/sub\rl", "inner.txt")
        vis.send("h")
        vis.send("l", "inner.txt")
        vis.send("/inner\rl", "inner.txt")
        vis.send(":WindowState\r", "1 windows, horizontal")
        # Folder mappings must disappear when we return to editing text.
        vis.send("l", " 1:2 ")
        self.assertNoErrors(vis)

    def test_explorer_preserves_unsaved_file_when_open_is_refused(self):
        vis = self.start(VIS, "notes.txt")
        vis.send("3Gccchanged\x1b", " 3:8 ")
        vis.send(" e", "sub/")
        vis.send("/sub\rl", "inner.txt")
        vis.send("/inner\rl", "No write since last change")
        vis.send(":WindowState\r", "2 windows, horizontal")
        vis.send(" e", " 3:8 ")
        vis.send(":w\r")
        self.assertIn("changed\n", (self.project / "notes.txt").read_text())
        self.assertEqual((self.project / "sub/inner.txt").read_text(), "inner\n")
        self.assertNoErrors(vis)

    def test_explorer_reuses_listing_and_preserves_unsaved_undo(self):
        notes = self.project / "notes.txt"
        original = notes.read_text()
        vis = self.start(VIS, "notes.txt")
        vis.send("3Gccchanged\x1b", " 3:8 ")
        vis.send(" e", "sub/")
        vis.send(":WindowState\r", "2 windows, horizontal")
        vis.send("\x17k")
        vis.send(" e")
        vis.send(":WindowState\r", "2 windows, horizontal")
        vis.send("l", " 3:8 ")
        vis.send(":WindowState\r", "1 windows, horizontal")
        vis.send("u")
        vis.send(":w\r")
        self.assertEqual(notes.read_text(), original)
        self.assertNoErrors(vis)

    def test_explorer_listing_failure_keeps_editing_window(self):
        listing = self.bin / "ls"
        listing.write_text('#!/bin/sh\nprintf "Cannot list fixture\\n" >&2\nexit 1\n')
        listing.chmod(0o755)
        vis = self.start(VIS, "notes.txt")
        vis.send("5G", " 5:1 ")
        vis.send(" e", "Cannot list fixture")
        vis.send(":WindowState\r", "1 windows, horizontal")
        vis.send("j", " 6:1 ")
        self.assertNoErrors(vis)

    def test_native_shell_keeps_working_directory_and_unsaved_editor(self):
        self.project = self.project.rename(self.root / "shell's project with spaces")
        record = self.root / "shell-directory"
        self.env["SHELL_RECORD"] = str(record)
        self.env["SHELL"] = "/bin/sh"
        original = (self.project / "notes.txt").read_text()
        vis = self.start(VIS, "notes.txt")
        vis.send("3Gccchanged\x1b", " 3:8 ")
        vis.send("  ")
        vis.send('printf "%s" "$PWD" > "$SHELL_RECORD"\n')
        vis.send("exit\n", " 3:8 ")
        vis.send(":WindowState\r", "1 windows, horizontal")
        self.assertEqual(record.read_text(), str(self.project))
        vis.send("u")
        vis.send(":w\r")
        self.assertEqual((self.project / "notes.txt").read_text(), original)
        picker = self.bin / "fzf"
        picker.write_text('#!/bin/sh\ncat >/dev/null\nprintf "sub/inner.txt\\0"\n')
        picker.chmod(0o755)
        vis.send(" ff", "inner.txt")
        self.assertNoErrors(vis)

    def test_native_shell_failure_is_visible(self):
        self.env["SHELL"] = str(self.bin / "missing-shell")
        vis = self.start(VIS, "notes.txt")
        vis.send("  ", "Command failed")
        vis.send("j", " 2:1 ")
        self.assertNoErrors(vis)

    def test_explorer_shell_uses_browsed_folder_without_changing_project_directory(self):
        folder = self.project / "folder's space"
        folder.mkdir()
        record = self.root / "shell-directory"
        self.env.update(SHELL="/bin/sh", SHELL_RECORD=str(record))
        vis = self.start(VIS, "notes.txt")
        vis.send(" e", "sub/")
        vis.send("/folder\rl")
        vis.send("  ")
        vis.send('printf "%s" "$PWD" > "$SHELL_RECORD"\n')
        vis.send("exit\n", " 1:1 ")
        self.assertEqual(record.read_text(), str(folder))
        vis.send("h", "sub/")
        vis.send(" e", "notes.txt")
        vis.send("  ")
        vis.send('printf "%s" "$PWD" > "$SHELL_RECORD"\n')
        vis.send("exit\n", " 1:1 ")
        self.assertEqual(record.read_text(), str(self.project))
        self.assertNoErrors(vis)

    @unittest.skipUnless(shutil.which("zsh"), "zsh is not installed")
    def test_shell_function_opens_directory(self):
        functions = REPO / "home/dot_config/zsh/conf.d/functions.zsh"
        vis = self.start("zsh", "-fc", f'source "{functions}"; vis "$1"', "zsh", str(self.project))
        self.assertIn("sub/", vis.screen())
        vis.send(":WindowState\r", "1 windows, horizontal")
        vis.send(" e", "No editing window to return to")
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
