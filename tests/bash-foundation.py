"""Run actual Bash code with temporary state and fake external integrations."""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "home"
BASH = shutil.which("bash")
SHELLCHECK = shutil.which("shellcheck")
FILES = [*SOURCE.glob("dot_bash*"), SOURCE / "dot_blerc",
         *(SOURCE / "dot_config/bash" / name for name in ("bashrc", "profile", "blerc", "logout")),
         *sorted((SOURCE / "dot_config/bash/conf.d").glob("*.bash"))]


@unittest.skipUnless(BASH, "bash is not installed")
class BashFoundation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-bash-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("bin", "config", "cache", "data", "state", "work", "home"):
            (self.root / name).mkdir()
        self.bin = self.root / "bin"
        (self.root / "config/bash").symlink_to(SOURCE / "dot_config/bash")
        # Only these harmless utilities are real; installed integrations stay unreachable.
        for name in ("mkdir", "chmod", "cat", "readlink", "mktemp", "rm"):
            (self.bin / name).symlink_to(shutil.which(name))
        shutil.copy(REPO / "tests/fixtures/bash-tool", self.root / "tool")
        (self.root / "tool").chmod(0o755)
        self.env = {
            "HOME": str(self.root / "home"), "PATH": str(self.bin), "LANG": "C",
            "TMPDIR": str(self.root),
            "XDG_CONFIG_HOME": str(self.root / "config"), "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_DATA_HOME": str(self.root / "data"), "XDG_STATE_HOME": str(self.root / "state"),
            "TEST_CLIPBOARD": str(self.root / "clipboard"), "TEST_YAZI_CWD": str(self.root / "work"),
        }

    def bash(self, code, *options, cwd=None, **env):
        result = subprocess.run([BASH, "--noprofile", "--norc", *options, "-c", code],
                                env=self.env | env, cwd=cwd or self.root, stdin=subprocess.DEVNULL,
                                capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def strict(self, code, **env):
        return self.bash("set -euo pipefail\n" + code, **env)

    def link_tools(self, *names):
        for name in names:
            (self.bin / name).symlink_to(self.root / "tool")

    def test_syntax(self):
        for path in FILES:
            with self.subTest(path=path.name):
                result = subprocess.run([BASH, "-n", str(path)], capture_output=True, text=True,
                                        timeout=15, check=False)
                self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(SHELLCHECK, "shellcheck is not installed")
    def test_shellcheck(self):
        result = subprocess.run([SHELLCHECK, "-s", "bash", "-e", "SC1090,SC1091,SC2034", *map(str, FILES)],
                                capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_env_history_functions_and_aliases(self):
        self.strict('''
            unset EDITOR VISUAL PAGER PROMPT_COMMAND
            source "$XDG_CONFIG_HOME/bash/conf.d/env.bash"
            [[ -z ${EDITOR-} && -z ${PAGER-} ]]
            EDITOR=custom VISUAL=visual PAGER=pager
            source "$XDG_CONFIG_HOME/bash/conf.d/env.bash"
            [[ $EDITOR == custom && $VISUAL == visual && $PAGER == pager ]]

            source "$XDG_CONFIG_HOME/bash/conf.d/history.bash"
            [[ $HISTFILE == "$XDG_STATE_HOME/bash/history" && $HISTSIZE == 20000 && $HISTFILESIZE == 10000 ]]
            [[ $PROMPT_COMMAND == dotfiles_bash_history ]]
            source "$XDG_CONFIG_HOME/bash/conf.d/history.bash"
            [[ $PROMPT_COMMAND == dotfiles_bash_history ]]
            if (exit 7); then :; else
              if dotfiles_bash_history; then exit 1; else [[ $? == 7 ]]; fi
            fi
            PROMPT_COMMAND='printf existing'
            source "$XDG_CONFIG_HOME/bash/conf.d/history.bash"
            [[ $PROMPT_COMMAND == 'dotfiles_bash_history; printf existing' ]]
            PROMPT_COMMAND=('printf one' 'printf two')
            source "$XDG_CONFIG_HOME/bash/conf.d/history.bash"
            [[ ${#PROMPT_COMMAND[@]} == 3 && ${PROMPT_COMMAND[1]} == 'printf one' ]]

            source "$XDG_CONFIG_HOME/bash/conf.d/functions.bash"
            copy </dev/null && exit 1
            clip-paste unexpected && exit 1
            y && exit 1
            source "$XDG_CONFIG_HOME/bash/conf.d/aliases.bash"
            [[ $(alias h) == "alias h='history'" && $(alias mkdir) == "alias mkdir='mkdir -p'" ]]
        ''')

    def test_history_directory_stays_private(self):
        directory = self.root / "state/bash"
        for existing in (False, True):
            with self.subTest(existing=existing):
                if existing:
                    directory.chmod(0o755)
                self.strict('source "$XDG_CONFIG_HOME/bash/conf.d/history.bash"')
                self.assertEqual(directory.stat().st_mode & 0o777, 0o700)

    def test_history_fails_visibly_without_mkdir_or_chmod(self):
        for name in ("mkdir", "chmod"):
            with self.subTest(tool=name):
                real = (self.bin / name).readlink()
                (self.bin / name).unlink()
                (self.bin / name).symlink_to(shutil.which("false"))
                self.strict('''
                    source "$XDG_CONFIG_HOME/bash/conf.d/history.bash" && exit 1
                    [[ -z ${HISTFILE+x} ]]
                ''')
                (self.bin / name).unlink()
                (self.bin / name).symlink_to(real)

    def test_clipboard_yazi_and_failed_generators(self):
        self.link_tools("pbcopy", "pbpaste", "wl-copy", "wl-paste", "xclip", "yazi", "mise", "zoxide", "starship")
        (self.root / "first").write_text("first")
        (self.root / "second").write_text("second")
        (self.root / "link").symlink_to("first")
        self.strict('''
            source "$XDG_CONFIG_HOME/bash/conf.d/functions.bash"
            for platform in linux-gnu darwin; do
              OSTYPE=$platform
              export WAYLAND_DISPLAY=test DISPLAY=:test
              copy "$TMPDIR/first" "$TMPDIR/second"
              [[ $(clip-paste) == firstsecond ]]
              copy "$TMPDIR/first" "$TMPDIR/missing" && exit 1
              [[ $(clip-paste) == firstsecond ]]
              copypath "$TMPDIR/link"
              [[ $(clip-paste) == "$TMPDIR/first" ]]
            done
            OSTYPE=linux-gnu
            unset WAYLAND_DISPLAY
            printf fallback | copy
            [[ $(clip-paste) == fallback ]]
            y
            [[ $PWD == "$TEST_YAZI_CWD" ]]
            export TEST_YAZI_STATUS=9
            if y; then exit 1; else [[ $? == 9 ]]; fi
            for module in mise zoxide prompt; do
              source "$XDG_CONFIG_HOME/bash/conf.d/$module.bash" || true
              [[ -z ${dotfiles_bad_eval-} ]]
            done
        ''')
        self.assertEqual(list(self.root.glob("yazi-cwd.*")), [], "Yazi temporary file leaked")

    def test_croot(self):
        # croot asks the real Git for the repository root.
        self.strict(f'''
            source "$XDG_CONFIG_HOME/bash/conf.d/functions.bash"
            builtin cd -- {str(SOURCE)!r}
            croot
            [[ $PWD == {str(REPO)!r} ]]
            croot unexpected && exit 1
            builtin cd -- "$TMPDIR"
            croot && exit 1
            [[ $PWD == "$TMPDIR" ]]
        ''', PATH=os.environ["PATH"])

    def test_startup_is_repeatable_and_login_only_extends_path(self):
        # No optional installed tools or real history are used by startup checks.
        self.bash('''
            source "$XDG_CONFIG_HOME/bash/bashrc"
            before=${PROMPT_COMMAND[*]}
            source "$XDG_CONFIG_HOME/bash/bashrc"
            [[ ${PROMPT_COMMAND[*]} == "$before" && $dotfiles_bash_loaded == yes ]]
            unset HISTFILE
        ''', "-i")
        self.bash('''
            source "$XDG_CONFIG_HOME/bash/bashrc"
            [[ -z ${dotfiles_bash_loaded-} ]] || exit 1
            source "$XDG_CONFIG_HOME/bash/profile"
            [[ $PATH == "$HOME/.local/bin:"* ]]
        ''')

    def test_preserved_profile_loads_bashrc_before_its_path(self):
        # Test both a missing user-local path and one already supplied by the parent.
        home = self.root / "login-home"
        (home / ".local/bin").mkdir(parents=True)
        (home / ".bash_profile").symlink_to(SOURCE / "dot_bash_profile")
        (home / ".bashrc").symlink_to(SOURCE / "dot_bashrc")
        (home / ".profile").symlink_to(REPO / "tests/fixtures/bash-login-profile")
        (home / ".local/bin/mise").symlink_to(self.root / "tool")
        for local in ("", f"{home}/.local/bin:"):
            with self.subTest(local=local):
                self.bash('''
                    # Do not load installed completions during this isolated startup test.
                    BASH_COMPLETION_VERSINFO=(test)
                    source "$HOME/.bash_profile"
                    set -e
                    [[ $TEST_PROFILE_LOADED == yes && $dotfiles_bash_loaded == yes ]]
                    [[ ${test_mise_activations:-0} == 1 ]]
                    [[ $PATH == "$HOME/.local/bin:$TMPDIR/bin" ]]
                    before=${PROMPT_COMMAND[*]}
                    source "$HOME/.bashrc"
                    [[ ${test_mise_activations:-0} == 1 && ${PROMPT_COMMAND[*]} == "$before" ]]
                    unset HISTFILE
                ''', "-i", HOME=str(home), PATH=local + str(self.bin),
                    TEST_MISE_SUCCESS_PATH=str(home / ".local/bin/mise"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
