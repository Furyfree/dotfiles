#!/usr/bin/env python3
"""Check profile wiring and previews without reading the live desktop."""

import json
import configparser
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import unittest

REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")
NOCTALIA = shutil.which("noctalia")


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
class Noctalia(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-noctalia-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.env = {"HOME": str(self.home), "PATH": os.defpath,
                    "XDG_CONFIG_HOME": str(self.home / ".config"),
                    "XDG_STATE_HOME": str(self.root / "state"),
                    "XDG_CACHE_HOME": str(self.root / "cache"),
                    "XDG_DATA_HOME": str(self.root / "data")}

    def chezmoi(self, *args, platform="linux", profiles=None, machine="desktop", fastmail_username=""):
        data = {"chezmoi": {"os": platform}, "profiles": ["hyprland-noctalia"] if profiles is None else profiles,
                "onePasswordSsh": False, "ManagedByNimbus": False,
                "fastmailUsername": fastmail_username}
        if machine is not None:
            data["Machine"] = machine
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--cache", str(self.root / "cache/chezmoi"),
            "--persistent-state", str(self.root / "chezmoi.boltdb"),
            "--skip-secrets", "--override-data", json.dumps(data), *args],
            cwd=self.root, env=self.env, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_profile_selection_and_config_ownership(self):
        for platform, profiles, enabled in (
                ("linux", ["hyprland-noctalia"], True),
                ("linux", ["common"], False),
                ("linux", [], False),
                ("linux", ["niri-dms"], False),
                ("darwin", ["hyprland-noctalia"], False),
                ("windows", ["hyprland-noctalia"], False)):
            with self.subTest(platform=platform, profiles=profiles):
                entries = json.loads(self.chezmoi("dump", "--format=json",
                                               platform=platform, profiles=profiles))
                self.assertEqual(".config/noctalia/config.toml" in entries, enabled)
                self.assertEqual(".config/noctalia/vscodium.toml" in entries, enabled)
                self.assertEqual(".config/noctalia/templates/vscodium-output-path.sh" in entries, enabled)
                self.assertEqual(".config/noctalia/assets/profile-picture.jpg" in entries, enabled)
                self.assertEqual(".config/noctalia/assets/profile-picture-circle.svg" in entries, enabled)
                self.assertEqual(".config/zsh/conf.d/noctalia.zsh" in entries, enabled)
                self.assertEqual(".config/bash/conf.d/noctalia.bash" in entries, enabled)
                for target in ("gtk-3.0/settings.ini", "gtk-4.0/settings.ini",
                               "qt5ct/qt5ct.conf", "qt6ct/qt6ct.conf"):
                    self.assertEqual(f".config/{target}" in entries, enabled)
                self.assertFalse(any(name.startswith((".local/state/noctalia", ".claude/", ".codex/"))
                                     for name in entries))
                if enabled:
                    config = tomllib.loads(entries[".config/noctalia/config.toml"]["contents"])
                    templates = config["theme"]["templates"]
                    self.assertNotIn("starship", templates["builtin_ids"])
                    self.assertTrue({"neovim", "fastfetch"}.isdisjoint(templates["community_ids"]))
                    self.assertNotIn("brave-origin", templates["community_ids"])
                    self.assertEqual(tomllib.loads(entries[".config/btop/btop.conf"]["contents"])
                                     ["color_theme"], "noctalia")
                    self.assertIn("include noctaliarc", entries[".config/zathura/zathurarc"]["contents"])
                elif platform == "linux":
                    self.assertEqual(tomllib.loads(entries[".config/btop/btop.conf"]["contents"])
                                     ["color_theme"], "TTY")
                    self.assertNotIn("include noctaliarc", entries[".config/zathura/zathurarc"]["contents"])

    def test_vscodium_target_uses_installed_extension(self):
        helper = REPO / "home/dot_config/noctalia/templates/vscodium-output-path.sh"
        tools = self.root / "bin"
        tools.mkdir()
        editor = tools / "codium"
        editor.write_text("#!/bin/sh\n"
                          "[ \"$1\" = --locate-extension ] || exit 2\n"
                          "[ \"$2\" = noctalia.noctaliatheme ] || exit 2\n"
                          "printf '%s' \"$LOCATED_EXTENSION\"\n")
        editor.chmod(0o755)
        env = dict(self.env, PATH=str(tools))
        for name in ("noctalia.noctaliatheme-0.0.5",
                     "noctalia.noctaliatheme-0.0.6-universal"):
            extension = self.home / ".vscode-oss/extensions" / name
            (extension / "themes").mkdir(parents=True)
            (extension / "package.json").write_text("{}")
            theme = extension / "themes/NoctaliaTheme-color-theme.json"
            theme.write_text("original")
            env["LOCATED_EXTENSION"] = str(extension)
            result = subprocess.run(["/bin/bash", str(helper)], env=env,
                                    text=True, capture_output=True, check=True)
            self.assertEqual(result.stdout, str(theme) + "\n")
            self.assertEqual(theme.read_text(), "original")
        for value, success in (("", True), ("relative/path", False),
                               (str(self.home / "missing"), False),
                               (str(extension) + "\n/another/path", False)):
            env["LOCATED_EXTENSION"] = value
            result = subprocess.run(["/bin/bash", str(helper)], env=env,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode == 0, success)
            self.assertEqual(result.stdout, "")
        editor.unlink()
        result = subprocess.run(["/bin/bash", str(helper)], env=env,
                                text=True, capture_output=True, check=True)
        self.assertEqual(result.stdout, "")

    def test_calendar_metadata_and_display_layout_are_scoped(self):
        for machine, username in (("desktop", "calendar@example.invalid"),
                                  ("laptop", ""), (None, "")):
            with self.subTest(machine=machine):
                entries = json.loads(self.chezmoi("dump", "--format=json", machine=machine,
                                                 fastmail_username=username))
                config = tomllib.loads(entries[".config/noctalia/config.toml"]["contents"])
                self.assertIn("lockscreen_widgets", config)
                if username:
                    account = config["calendar"]["account"]["fastmail"]
                    self.assertEqual(account, {"type": "caldav", "provider": "custom",
                                              "server_url": "https://caldav.fastmail.com/dav/",
                                              "username": username})
                else:
                    self.assertNotIn("account", config.get("calendar", {}))

    def test_lockscreen_layout_and_avatar_follow_selected_outputs(self):
        import base64
        import xml.etree.ElementTree as ET
        for machine, outputs in (("desktop", ["DP-3", "DP-4"]),
                                 ("laptop", ["eDP-1"]), (None, [""])):
            with self.subTest(machine=machine):
                entries = json.loads(self.chezmoi("dump", "--format=json", machine=machine))
                config = tomllib.loads(entries[".config/noctalia/config.toml"]["contents"])
                self.assertEqual(config["lockscreen"]["blur_intensity"], 0.35)
                widgets = config["lockscreen_widgets"]
                self.assertFalse(widgets["grid"]["visible"])
                self.assertEqual(set(widgets["widget_order"]), set(widgets["widget"]))
                self.assertEqual({w["output"] for w in widgets["widget"].values()}, set(outputs))
                for output in outputs:
                    clock = widgets["widget"]["minimal-clock-" + output]
                    date = widgets["widget"]["minimal-date-" + output]
                    avatar = widgets["widget"]["minimal-avatar-" + output]
                    self.assertEqual(avatar["box_width"], 72)
                    self.assertFalse(avatar["settings"]["background"])
                    self.assertEqual(avatar["settings"]["image_path"],
                                     str(self.home / ".config/noctalia/assets/profile-picture-circle.svg"))
                    self.assertLess(date["cy"], clock["cy"])
                    self.assertLess(clock["cy"], avatar["cy"])
                    if output:
                        login = widgets["widget"]["lockscreen-login-box@" + output]
                        self.assertAlmostEqual(login["cy"] / login["placement_height"], 0.69, places=2)
                        self.assertGreater(login["cy"], avatar["cy"] + avatar["box_height"] / 2)
                        self.assertEqual(login["settings"]["layout"], "compact")
                        self.assertFalse(login["settings"]["show_session_buttons"])
                svg = ET.fromstring(entries[".config/noctalia/assets/profile-picture-circle.svg"]["contents"])
                embedded = svg.find("{http://www.w3.org/2000/svg}image").attrib[
                    "{http://www.w3.org/1999/xlink}href"]
                self.assertEqual(base64.b64decode(embedded.split(",", 1)[1]),
                                 (REPO / "home/dot_config/noctalia/assets/profile-picture.jpg").read_bytes())

    def test_logout_requires_and_preserves_the_explicit_session_id(self):
        entries = json.loads(self.chezmoi("dump", "--format=json"))
        config = tomllib.loads(entries[".config/noctalia/config.toml"]["contents"])
        command = next(row["command"] for row in config["shell"]["session"]["actions"]
                       if row["action"] == "logout")
        binaries = self.root / "bin"
        binaries.mkdir()
        fake = binaries / "loginctl"
        fake.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\nexit "${RESULT:-0}"\n')
        fake.chmod(0o755)
        env = dict(self.env, PATH=str(binaries))
        for session in (None, "", "c2", "session with spaces"):
            for status in (0, 7):
                with self.subTest(session=session, status=status):
                    invocation_env = dict(env, RESULT=str(status))
                    if session is not None:
                        invocation_env["XDG_SESSION_ID"] = session
                    result = subprocess.run(["/bin/sh", "-c", command],
                                            env=invocation_env, text=True, capture_output=True)
                    if session:
                        self.assertEqual(result.returncode, status)
                        self.assertEqual(result.stdout.splitlines(), ["terminate-session", session])
                    else:
                        self.assertNotEqual(result.returncode, 0)
                        self.assertEqual(result.stdout, "")

    def test_lid_guard_and_its_shortcut_are_laptop_only(self):
        for machine in (None, "", "desktop", "laptop"):
            with self.subTest(machine=machine):
                entries = json.loads(self.chezmoi("dump", "--format=json", machine=machine))
                config = tomllib.loads(entries[".config/noctalia/config.toml"]["contents"])
                keybinds = entries[".config/hypr/conf.d/keybinds.lua"]["contents"]
                self.assertEqual("8bury/lid-guard" in config["plugins"]["enabled"],
                                 machine == "laptop")
                self.assertEqual("8bury/lid-guard:lid-guard-service" in keybinds,
                                 machine == "laptop")
                for zone in ("start", "center", "end"):
                    for widget in config["bar"]["default"][zone]:
                        kind = config.get("widget", {}).get(widget, {}).get("type", widget)
                        if ":" in kind:
                            self.assertIn(kind.split(":")[0], config["plugins"]["enabled"])

    @unittest.skipUnless(NOCTALIA, "noctalia is not installed")
    def test_native_config(self):
        for machine in ("desktop", "laptop"):
            with self.subTest(machine=machine):
                entries = json.loads(self.chezmoi("dump", "--format=json", machine=machine))
                config = self.root / f"{machine}.toml"
                config.write_text(entries[".config/noctalia/config.toml"]["contents"])
                result = subprocess.run([NOCTALIA, "config", "validate", str(config)],
                                        cwd=self.root, env=self.env, text=True,
                                        capture_output=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_toolkit_selection_leaves_colors_and_mode_to_noctalia(self):
        entries = json.loads(self.chezmoi("dump", "--format=json"))
        for version in (3, 4):
            settings = configparser.ConfigParser()
            settings.read_string(entries[f".config/gtk-{version}.0/settings.ini"]["contents"])
            self.assertNotIn("gtk-application-prefer-dark-theme", settings["Settings"])
            if version == 4:
                self.assertNotIn("gtk-theme-name", settings["Settings"])
            self.assertNotIn(f".config/gtk-{version}.0/noctalia.css", entries)
        for version in (5, 6):
            settings = configparser.ConfigParser()
            settings.read_string(entries[f".config/qt{version}ct/qt{version}ct.conf"]["contents"])
            appearance = settings["Appearance"]
            self.assertTrue(appearance.getboolean("custom_palette"))
            self.assertTrue(appearance["color_scheme_path"].endswith(
                f"/.config/qt{version}ct/colors/noctalia.conf"))
            self.assertNotIn(f".config/qt{version}ct/colors/noctalia.conf", entries)

    def test_files_hook_preserves_user_dirs_across_login_and_reapply(self):
        entries = json.loads(self.chezmoi("dump", "--format=json", machine="laptop"))
        script = self.root / "files.sh"
        script.write_text(self.chezmoi("execute-template",
                                     (REPO / "home/run_after_configure-files.sh.tmpl").read_text(),
                                     machine="laptop"))
        binaries = self.root / "bin"
        binaries.mkdir()
        # Exercise directory creation without changing live GSettings.
        fake = binaries / "gsettings"
        fake.write_text("#!/bin/sh\nexit 0\n")
        fake.chmod(0o755)
        env = dict(self.env, PATH=str(binaries) + os.pathsep + os.defpath)
        config = self.home / ".config"
        config.mkdir()
        user_dirs = config / "user-dirs.dirs"
        contents = entries[".config/user-dirs.dirs"]["contents"]
        user_dirs.write_text(contents)
        for repeat in range(2):
            result = subprocess.run(["bash", str(script)], cwd=self.root, env=env,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            for line in contents.splitlines():
                if line.startswith("XDG_"):
                    value = line.split("=", 1)[1].strip('"').replace("$HOME", str(self.home))
                    self.assertTrue(Path(value).is_dir(), value)
            marker = self.home / "Documents/existing.txt"
            if repeat == 0:
                marker.write_text("preserve me")
            self.assertEqual(marker.read_text(), "preserve me")
            updater = shutil.which("xdg-user-dirs-update")
            if updater:
                result = subprocess.run([updater], cwd=self.root, env=env,
                                        text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(user_dirs.read_text(), contents)

    def test_previews_and_generated_files_do_not_drift(self):
        # Apply into this disposable home only; no install scripts or live state.
        self.chezmoi("apply", "--exclude=scripts")
        for name in (".config/hypr/noctalia.lua", ".config/btop/themes/noctalia.theme",
                     ".config/ghostty/themes/noctalia", ".config/zathura/noctaliarc",
                     ".config/fzf/themes/noctalia.sh", ".config/zed/themes/noctalia.json",
                     ".config/gtk-3.0/noctalia.css", ".config/gtk-4.0/noctalia.css",
                     ".config/qt5ct/colors/noctalia.conf", ".config/qt6ct/colors/noctalia.conf"):
            target = self.home / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("generated stand-in\n")
        managed = self.chezmoi("managed")
        self.assertNotIn(".config/btop/themes/noctalia.theme", managed)
        self.assertEqual(self.chezmoi("status", "--exclude=scripts"), "")
        self.assertEqual(self.chezmoi("diff", "--exclude=scripts"), "")
        self.chezmoi("verify", "--exclude=scripts")

    def test_fzf_missing_and_present_palette(self):
        for shell in ("bash", "zsh"):
            binary = shutil.which(shell)
            if not binary:
                continue
            source = REPO / f"home/dot_config/{shell}/conf.d/noctalia.{shell}"
            script = '. "$1"; printf "%s" "${FZF_DEFAULT_OPTS-}"'
            result = subprocess.run([binary, "-c", script, "fixture", str(source)],
                                    cwd=self.root, env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            palette = self.home / ".config/fzf/themes/noctalia.sh"
            palette.parent.mkdir(parents=True, exist_ok=True)
            palette.write_text('export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS-} --color=fg:#abcdef"\n')
            result = subprocess.run([binary, "-c", script, "fixture", str(source)],
                                    cwd=self.root, env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("--color=fg:#abcdef", result.stdout)
            palette.unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
