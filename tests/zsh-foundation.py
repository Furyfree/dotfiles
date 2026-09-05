#!/usr/bin/env python3
"""Run actual Zsh code with temporary state and fake external integrations."""

import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "home"
ZSH = shutil.which("zsh")


@unittest.skipUnless(ZSH, "zsh is not installed")
class ZshFoundation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-zsh-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.zdot = self.root / "config/zsh"
        shutil.copytree(SOURCE / "dot_config/zsh", self.zdot)
        for path in self.zdot.glob("dot_*"):
            path.rename(path.with_name("." + path.name.removeprefix("dot_")))
        (self.root / "tmp").mkdir()
        self.env = {
            "HOME": str(self.home), "PATH": str(self.bin), "LANG": "C",
            "TERM": "dumb", "TMPDIR": str(self.root / "tmp"),
            "XDG_CONFIG_HOME": str(self.root / "config"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
            "ZDOTDIR": str(self.zdot), "TEST_SOURCE": str(SOURCE),
            "TEST_CLIPBOARD": str(self.root / "clipboard"),
            "TEST_CALLS": str(self.root / "calls"),
        }
        # Only these harmless utilities are real; installed integrations stay unreachable.
        for name in ("mkdir", "chmod", "cat", "mktemp", "rm", "mv"):
            binary = shutil.which(name)
            if not binary:
                self.skipTest(f"{name} is not installed")
            (self.bin / name).symlink_to(binary)

    def mock(self, name, code="exit 0"):
        path = self.bin / name
        if path.is_symlink():
            path.unlink()  # Never write through a fixture symlink to a real utility.
        path.write_text("#!/bin/sh\n" + code + "\n")
        path.chmod(0o755)

    def shell(self, code, expected=0, terminal=False):
        descriptors = os.openpty() if terminal else ()
        try:
            result = subprocess.run([ZSH, "-d", "-f", "-i", "-c", code], env=self.env,
                                    stdin=descriptors[1] if terminal else subprocess.DEVNULL,
                                    cwd=self.home, capture_output=True, text=True, timeout=15)
        finally:
            for descriptor in descriptors:
                os.close(descriptor)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def functions(self, code, expected=0):
        return self.shell('source "$ZDOTDIR/conf.d/functions.zsh"; ' + code, expected)

    def test_all_zsh_syntax(self):
        paths = [SOURCE / "dot_zshenv", *self.zdot.glob(".z*"), *self.zdot.glob("conf.d/*.zsh")]
        for path in paths:
            with self.subTest(path=path.name):
                result = subprocess.run([ZSH, "-d", "-f", "-n", str(path)], env=self.env,
                                        capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_xdg_defaults_and_overrides(self):
        self.shell('''
            source "$TEST_SOURCE/dot_zshenv"
            [[ $ZDOTDIR == "$XDG_CONFIG_HOME/zsh" ]] || exit 1
            unset XDG_CONFIG_HOME XDG_CACHE_HOME XDG_DATA_HOME XDG_STATE_HOME
            source "$TEST_SOURCE/dot_zshenv"
            [[ $XDG_CONFIG_HOME == "$HOME/.config" && $XDG_CACHE_HOME == "$HOME/.cache"
               && $XDG_DATA_HOME == "$HOME/.local/share" && $XDG_STATE_HOME == "$HOME/.local/state"
               && $ZDOTDIR == "$HOME/.config/zsh" ]]
        ''')

    def test_profile_preserves_spaced_paths_and_deduplicates(self):
        self.shell('''
            path=("$HOME/some bin" "${path[@]}")
            source "$ZDOTDIR/.zprofile"
            source "$ZDOTDIR/.zprofile"
            [[ $path[1] == "$HOME/.local/bin" && $path[2] == "$HOME/some bin" && $#path == 3 ]]
        ''')

    def test_environment_preserves_choices_and_handles_missing_tools(self):
        self.shell('''
            EDITOR='custom editor'; VISUAL='custom visual'; PAGER='custom pager'; MANPAGER='custom man'
            source "$ZDOTDIR/conf.d/env.zsh"
            [[ $EDITOR == 'custom editor' && $VISUAL == 'custom visual'
               && $PAGER == 'custom pager' && $MANPAGER == 'custom man' ]] || exit 1
            unset EDITOR VISUAL PAGER
            source "$ZDOTDIR/conf.d/env.zsh"
            [[ -z ${EDITOR-} && -z ${VISUAL-} && -z ${PAGER-} ]]
        ''')
        self.mock("vi")
        self.shell('source "$ZDOTDIR/conf.d/env.zsh"; [[ $EDITOR == vi && $VISUAL == "$EDITOR" ]]')

    def test_history_creation_and_existing_directory_permissions(self):
        directory = self.root / "state/zsh"
        for existing in (False, True):
            with self.subTest(existing=existing):
                if existing:
                    directory.chmod(0o755)
                self.shell('''
                    previous_umask=$(umask)
                    source "$ZDOTDIR/conf.d/history.zsh" || exit 1
                    [[ $(umask) == $previous_umask && $HISTFILE == "$XDG_STATE_HOME/zsh/history"
                       && $SAVEHIST -gt 0 && $HISTSIZE -ge $SAVEHIST ]]
                ''')
                self.assertEqual(stat.S_IMODE(directory.stat().st_mode), 0o700)

    def test_history_disables_saving_on_mkdir_or_chmod_failure(self):
        for utility in ("mkdir", "chmod"):
            with self.subTest(utility=utility):
                self.mock(utility, "exit 23")
                self.shell('''
                    HISTFILE=old
                    source "$ZDOTDIR/conf.d/history.zsh"
                    result=$?
                    [[ $result != 0 && ! -v HISTFILE ]]
                ''')
                (self.bin / utility).unlink()
                (self.bin / utility).symlink_to(shutil.which(utility))

    def test_startup_without_optional_tools(self):
        result = self.shell('source "$ZDOTDIR/.zshrc" || exit 1; (( $+functions[copy] && $+functions[compdef] ))')
        self.assertEqual(result.stderr, "")
        self.assertTrue((self.root / "cache/zsh/zcompdump").exists())
        self.assertFalse((self.root / "calls").exists())

    def test_failed_generated_shell_code_is_never_evaluated(self):
        for command, module in (("mise", "mise"), ("starship", "prompt"),
                                ("zoxide", "zoxide"), ("sheldon", "plugins")):
            with self.subTest(command=command):
                self.mock(command, "printf '%s\\n' 'typeset -g TEST_UNSAFE=1'\nexit 23")
                result = self.shell(f'source "$ZDOTDIR/conf.d/{module}.zsh"; [[ ! -v TEST_UNSAFE ]]')
                self.assertEqual(result.stderr, "")
                self.mock(command, "printf '%s\\n' 'typeset -g TEST_INTEGRATION=1'")
                self.shell(f'source "$ZDOTDIR/conf.d/{module}.zsh"; [[ $TEST_INTEGRATION == 1 ]]')

    def test_fzf_terminal_gate_and_generated_code_failure(self):
        self.mock("fzf", "printf '%s\\n' 'typeset -g TEST_INTEGRATION=1'")
        code = 'source "$ZDOTDIR/conf.d/fzf.zsh"; '
        self.shell(code + '[[ ! -v TEST_INTEGRATION ]]')
        self.shell(code + '[[ $TEST_INTEGRATION == 1 ]]', terminal=True)
        self.mock("fzf", "printf '%s\\n' 'typeset -g TEST_INTEGRATION=1'\nexit 23")
        self.shell(code + '[[ ! -v TEST_INTEGRATION ]]', terminal=True)

    def test_alias_fallbacks_do_not_replace_existing_native_commands(self):
        for name in ("zed", "zeditor", "hx", "helix", "code", "codium"):
            self.mock(name)
        self.shell('''
            source "$ZDOTDIR/conf.d/aliases.zsh"
            for name in zed hx code cat paste; do
                (( ! $+aliases[$name] )) || exit 1
            done
        ''')

    def clipboard_mocks(self):
        for name in ("pbcopy", "pbpaste", "wl-copy", "wl-paste", "xclip"):
            self.mock(name, '''
                printf '%s\\n' "${0##*/} $*" >> "$TEST_CALLS"
                [ "${TEST_BACKEND_FAILURE:-0}" = 0 ] || exit "$TEST_BACKEND_FAILURE"
                case "${0##*/} $*" in
                    pbpaste*|wl-paste*|*'-out'*) cat "$TEST_CLIPBOARD" ;;
                    *) cat > "$TEST_CLIPBOARD" ;;
                esac
            ''')

    def test_clipboard_platforms_precedence_and_roundtrip(self):
        self.clipboard_mocks()
        for ostype, wayland, display, backend in (
                ("darwin", "", "", "pbcopy"), ("linux", "wayland-1", ":1", "wl-copy"),
                ("linux", "", ":1", "xclip")):
            with self.subTest(ostype=ostype, backend=backend):
                self.env.update(WAYLAND_DISPLAY=wayland, DISPLAY=display)
                result = self.functions(f'OSTYPE={ostype}; print -rn -- "test content" | copy; clip-paste')
                self.assertEqual(result.stdout, "test content")
                calls = (self.root / "calls").read_text().splitlines()
                self.assertTrue(calls[-2].startswith(backend), calls)
        (self.bin / "wl-copy").unlink()
        self.env.update(WAYLAND_DISPLAY="wayland-1", DISPLAY=":1")
        self.functions('OSTYPE=linux; print -rn -- fallback | copy')
        self.assertIn("xclip", (self.root / "calls").read_text().splitlines()[-1])

    def test_copy_file_quoting_preflight_and_backend_errors(self):
        self.clipboard_mocks()
        self.env.update(WAYLAND_DISPLAY="wayland-1", TEST_BACKEND_FAILURE="0")
        for name, content in (("space file", "one"), ("-", "two")):
            (self.home / name).write_text(content)
        self.functions('OSTYPE=linux; copy "space file" -')
        self.assertEqual((self.root / "clipboard").read_text(), "onetwo")
        calls = (self.root / "calls").read_text()
        self.functions('OSTYPE=linux; copy "space file" missing', expected=1)
        self.assertEqual((self.root / "calls").read_text(), calls)
        self.functions('OSTYPE=linux; copy .', expected=1)
        self.env["TEST_BACKEND_FAILURE"] = "23"
        self.functions('OSTYPE=linux; copy "space file"', expected=23)
        self.functions('OSTYPE=linux; clip-paste', expected=23)

    def test_missing_clipboard_and_usage_errors(self):
        self.functions('OSTYPE=linux; copy', expected=1)
        self.functions('OSTYPE=darwin; clip-paste', expected=1)
        for command in ("clip-paste argument", "croot argument", "copypath one two"):
            self.functions(command, expected=2)

    def test_copypath_and_croot_preserve_paths_and_errors(self):
        self.shell('''
            source "$ZDOTDIR/conf.d/functions.zsh"
            copy() { command cat; }
            [[ $(copypath) == $PWD ]] || exit 1
            copy() { return 23; }
            copypath
        ''', expected=23)
        self.mock("git", 'printf "%s\\n" "$HOME"')
        self.functions('builtin cd "$ZDOTDIR"; croot; [[ $PWD == $HOME ]]')
        self.mock("git", "exit 23")
        self.functions('croot; result=$?; [[ $result == 23 && $PWD == $HOME ]]')

    def test_yazi_directory_change_cleanup_and_errors(self):
        self.functions("y", expected=127)
        target = self.home / "directory with\na newline"
        target.mkdir()
        self.env["TEST_YAZI_CWD"] = str(target)
        self.mock("yazi", '''
            for arg do
                case "$arg" in --cwd-file=*) printf '%s' "$TEST_YAZI_CWD" > "${arg#*=}" ;; esac
            done
            exit "${TEST_BACKEND_FAILURE:-0}"
        ''')
        self.functions('y || exit; [[ $PWD == $TEST_YAZI_CWD ]]')
        self.env["TEST_BACKEND_FAILURE"] = "23"
        self.functions('y; result=$?; [[ $result == 23 && $PWD == $HOME ]]')
        self.env.update(TEST_BACKEND_FAILURE="0", TEST_YAZI_CWD="relative/path")
        self.functions('y; result=$?; [[ $result == 1 && $PWD == $HOME ]]')
        self.assertEqual(list((self.root / "tmp").iterdir()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
