#!/usr/bin/env python3
"""Read-only config checks. All application state is isolated in a temporary tree."""

import gzip
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import unittest

import yaml


REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "home"
CONFIG = SOURCE / "dot_config"


class ToolingApps(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-apps-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(CONFIG / "mise", self.root / "config/mise")
        # Do not inherit credentials, user app configuration, or agent hooks.
        self.env = {key: os.environ[key] for key in ("PATH", "HOME", "LANG") if key in os.environ}
        self.env.update({
            "HOME": str(self.root / "home"),
            "XDG_CONFIG_HOME": str(self.root / "config"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_STATE_HOME": str(self.root / "state"),
            "MISE_CONFIG_DIR": str(self.root / "config/mise"),
            "MISE_CACHE_DIR": str(self.root / "cache/mise"),
            "MISE_DATA_DIR": str(self.root / "data/mise"),
            "MISE_STATE_DIR": str(self.root / "state/mise"),
            "MISE_SYSTEM_CONFIG_FILE": str(self.root / "no-system-mise.toml"),
            "MISE_CEILING_PATHS": str(self.root),
            "MISE_OFFLINE": "true",
            "MISE_AUTO_UPDATE": "false",
            "MISE_AUTO_INSTALL": "false",
            "MISE_NO_ENV": "true",
            "MISE_NO_HOOKS": "true",
            "GH_CONFIG_DIR": str(self.root / "gh"),
            "GH_NO_UPDATE_NOTIFIER": "1",
            "NIX_CONF_DIR": str(self.root / "nix-system"),
            "NIX_USER_CONF_FILES": str(CONFIG / "nix/nix.conf"),
        })
        Path(self.env["HOME"]).mkdir()

    def run_tool(self, *args, input=None):
        if not shutil.which(args[0]):
            self.skipTest(f"{args[0]} is not installed")
        result = subprocess.run(args, cwd=self.root, env=self.env, input=input,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotRegex(result.stderr.lower(), r"unknown (setting|option)|deprecated")
        return result.stdout

    def test_toml_syntax(self):
        for path in CONFIG.rglob("*.toml"):
            if path.stat().st_size:
                with self.subTest(path=path.relative_to(SOURCE)):
                    tomllib.loads(path.read_text())

    def test_starship_native_config(self):
        self.env["STARSHIP_CONFIG"] = str(CONFIG / "starship.toml")
        self.env["STARSHIP_CACHE"] = str(self.root / "cache/starship")
        self.env["STARSHIP_LOG"] = "error"
        native = tomllib.loads(self.run_tool("starship", "print-config"))
        config = tomllib.loads((CONFIG / "starship.toml").read_text())

        def compare(configured, effective):
            for key, value in configured.items():
                if key == "$schema":
                    continue
                self.assertIn(key, effective)
                if isinstance(value, dict):
                    compare(value, effective[key])
                else:
                    self.assertEqual(value, effective[key])

        compare(config, native)

    def test_sheldon_inline_shell(self):
        config = tomllib.loads((CONFIG / "sheldon/plugins.toml").read_text())
        self.assertEqual(config["shell"], "zsh")
        for name, plugin in config["plugins"].items():
            with self.subTest(plugin=name):
                hooks = plugin.get("hooks", {})
                code = "\n".join((hooks.get("pre", ""), plugin.get("inline", ":"),
                                   hooks.get("post", "")))
                self.run_tool("zsh", "-f", "-n", input=code)
                for module in re.findall(r'\$ZDOTDIR/(conf\.d/[^"\s]+)', code):
                    self.assertTrue((CONFIG / "zsh" / module).is_file(), module)

    def test_mise_native_settings_and_registry(self):
        json.loads(self.run_tool("mise", "settings", "--json"))
        configs = self.run_tool("mise", "config", "ls", "--json")
        json.loads(configs)
        for path in (CONFIG / "mise").rglob("*.toml"):
            self.assertIn(path.name, configs)
        config = tomllib.loads((CONFIG / "mise/config.toml").read_text())
        config["tools"].update(tomllib.loads((CONFIG / "mise/conf.d/linux-tools.toml").read_text())["tools"])
        for tool in config.get("tools", {}):
            if ":" in tool:
                continue  # Explicit backend IDs need not appear in the registry.
            with self.subTest(tool=tool):
                self.assertTrue(self.run_tool("mise", "--no-config", "registry", tool).strip())

    def test_nix(self):
        json.loads(self.run_tool("nix", "--extra-experimental-features", "nix-command",
                                 "config", "show", "--json"))

    def test_udiskie(self):
        config = yaml.safe_load((CONFIG / "udiskie/config.yml").read_text())
        self.assertIsInstance(config, dict)
        self.assertIsInstance(config.get("program_options", {}), dict)
        if not importlib.util.find_spec("udiskie"):
            self.skipTest("udiskie Python module is not installed; YAML assertions passed")
        from udiskie.config import Config
        # This parser does not connect to D-Bus or mount anything.
        native = Config.from_file(str(CONFIG / "udiskie/config.yml"))
        self.assertEqual(native.program_options, config.get("program_options", {}))

    def test_gh(self):
        canonical = SOURCE / ".chezmoitemplates/configs/gh/config.yml"
        content = canonical.read_text()
        config = yaml.safe_load(content)
        self.assertIsInstance(config, dict)
        gh_dir = Path(self.env["GH_CONFIG_DIR"])
        gh_dir.mkdir()
        shutil.copyfile(canonical, gh_dir / "config.yml")
        for key, value in config.items():
            if key != "aliases":
                with self.subTest(key=key):
                    self.assertEqual(self.run_tool("gh", "config", "get", key).strip(), str(value))
        aliases = self.run_tool("gh", "alias", "list")
        for name, command in config.get("aliases", {}).items():
            self.assertIn(f"{name}: {command}", aliases)
        self.assertFalse((gh_dir / "hosts.yml").exists())

    def test_btop(self):
        config = tomllib.loads((REPO / "home/.chezmoitemplates/configs/btop/btop.conf").read_text())
        defaults = tomllib.loads(self.run_tool("btop", "--default-config"))
        for key, value in config.items():
            with self.subTest(key=key):
                self.assertIn(key, defaults)
                self.assertIs(type(value), type(defaults[key]))

    def render_zathura(self):
        override = json.dumps({"chezmoi": {"os": "linux"}, "profiles": ["common"],
                               "onePasswordSsh": False})
        entries = json.loads(self.run_tool(*self.chezmoi_args(override), "dump", "--format=json"))
        return entries[".config/zathura/zathurarc"]["contents"]

    def test_zathura(self):
        settings, mappings = {}, {}
        for line in self.render_zathura().splitlines():
            fields = shlex.split(line, comments=True)
            if not fields:
                continue
            self.assertGreaterEqual(len(fields), 3, line)
            action, name, *values = fields
            self.assertIn(action, ("set", "map"))
            target = settings if action == "set" else mappings
            self.assertNotIn(name, target)
            target[name] = values[0]
        man = Path("/usr/share/man/man5/zathurarc.5.gz")
        if not man.exists():
            self.skipTest("installed zathurarc manual unavailable; static assertions passed")
        manual = gzip.decompress(man.read_bytes()).decode().replace(r"\-", "-")
        for name in settings:
            self.assertIn(r"\fI" + name + r"\fP", manual, name)
        for action in mappings.values():
            self.assertIn(r"\fB" + action + r"\fP", manual, action)

    @unittest.skipUnless(os.environ.get("DOTFILES_GUI_TESTS") == "1",
                         "optional GUI smoke check: set DOTFILES_GUI_TESTS=1")
    def test_zathura_headless_startup(self):
        if not all(shutil.which(tool) for tool in ("ldd", "zathura")):
            self.skipTest("Linux zathura and GTK Broadway are required for headless startup")
        libraries = self.run_tool("ldd", shutil.which("zathura"))
        server = "gtk4-broadwayd" if "libgtk-4" in libraries else "broadwayd"
        if not shutil.which(server):
            self.skipTest(f"{server} is not installed")
        config_dir = self.root / "config/zathura"
        config_dir.mkdir()
        (config_dir / "zathurarc").write_text(self.render_zathura())
        runtime = self.root / "runtime"
        runtime.mkdir(mode=0o700)
        display_id = f":{os.getpid()}"
        env = self.env | {"XDG_RUNTIME_DIR": str(runtime), "GDK_BACKEND": "broadway",
                          "BROADWAY_DISPLAY": display_id, "NO_AT_BRIDGE": "1", "GTK_A11Y": "none"}
        # A private Unix socket: no window in the live desktop, no TCP listener.
        display = subprocess.Popen([server, "--unixsocket", str(runtime / "http.sock"), display_id],
                                   env=env, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        viewer = None
        try:
            for _ in range(100):
                if (runtime / "http.sock").exists() or display.poll() is not None:
                    break
                time.sleep(0.02)
            self.assertIsNone(display.poll(), "Broadway failed to start")
            self.assertTrue((runtime / "http.sock").exists(), "Broadway socket not ready")
            viewer = subprocess.Popen([
                "zathura", "--config-dir", str(config_dir),
                "--data-dir", str(self.root / "zathura-data"),
                "--cache-dir", str(self.root / "zathura-cache"), "--log-level", "debug"],
                env=env, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(1)
            early_exit = viewer.poll()
        finally:
            if viewer is not None:
                if viewer.poll() is None:
                    viewer.terminate()
                _, errors = viewer.communicate(timeout=5)
            if display.poll() is None:
                display.terminate()
            display.communicate(timeout=5)
        self.assertIsNone(early_exit, errors.decode())
        self.assertNotRegex(errors.decode().lower(),
                            r"error:|invalid|unknown (setting|function)|failed to (set|parse)")

    def test_chezmoi_platforms_and_templates(self):
        unix = {".config/mise/config.toml", ".config/nix/nix.conf", ".config/btop/btop.conf",
                ".zshenv", ".config/zsh/.zshrc", ".config/zsh/.zprofile",
                ".config/sheldon/plugins.toml"}
        unix |= {f".config/zsh/conf.d/{path.name}"
                 for path in (CONFIG / "zsh/conf.d").glob("*.zsh")
                 if path.name != "noctalia.zsh"}
        linux = {".config/udiskie/config.yml", ".config/zathura/zathurarc",
                 ".config/mise/conf.d/linux-tools.toml", ".config/voxtype/config.toml",
                 ".config/vm-curator/config.toml"}
        gh_unix = ".config/gh/config.yml"
        gh_windows = "AppData/Roaming/GitHub CLI/config.yml"
        all_targets = unix | linux | {gh_unix, gh_windows}
        for platform, expected in (("linux", unix | linux | {gh_unix}),
                                   ("darwin", unix | {gh_unix}),
                                   ("windows", {gh_windows})):
            with self.subTest(platform=platform):
                override = json.dumps({"chezmoi": {"os": platform}, "profiles": ["common"],
                                       "onePasswordSsh": False})
                args = self.chezmoi_args(override)
                managed = set(self.run_tool(*args, "managed").splitlines())
                self.assertEqual(managed & all_targets, expected)
                self.assertIn(".config/starship.toml", managed)
                if platform != "linux":
                    self.assertNotIn(".config/mise/conf.d", managed)
                self.assertFalse(any(re.search(r"(^|/)(hosts.yml|history|.*\.db|\.keep)$", path)
                                     for path in managed))
                wrapper = SOURCE / ("AppData/Roaming/private_GitHub CLI/private_config.yml.tmpl"
                                    if platform == "windows" else "dot_config/private_gh/private_config.yml.tmpl")
                rendered = self.run_tool(*args, "execute-template", input=wrapper.read_text())
                self.assertEqual(yaml.safe_load(rendered),
                                 yaml.safe_load((SOURCE / ".chezmoitemplates/configs/gh/config.yml").read_text()))
                dumped = json.loads(self.run_tool(*args, "dump", "--format=json"))
                for target, entry in dumped.items():
                    if entry["type"] == "file":
                        self.assertTrue(entry.get("contents", "").strip(),
                                        f"empty scaffold is managed: {target}")
                if platform != "windows":
                    self.assertEqual(dumped[".config/gh"]["perm"] & 0o777, 0o700)
                    self.assertEqual(dumped[gh_unix]["perm"] & 0o777, 0o600)

    def chezmoi_args(self, override):
        return ("chezmoi", "--source", str(REPO), "--config", str(self.root / "home/chezmoi.toml"),
                "--destination", str(self.root / "home"), "--cache", str(self.root / "cache/chezmoi"),
                "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
                "--skip-secrets", "--no-tty", "--override-data", override)

    def test_init_preserves_nimbus_handoff(self):
        # Real init uses the host OS, even with --override-data. Do not claim emulation.
        platforms = {"linux": ["unix", "linux"], "darwin": ["unix", "macos"], "win32": ["windows"]}
        if sys.platform not in platforms:
            self.skipTest("unsupported host platform")
        diff = self.run_tool(*self.chezmoi_args("{}"), "init", "--dry-run", "--verbose",
                             "--promptString", "Machine=test-machine",
                             "--promptBool", "ManagedByNimbus=true",
                             "--promptBool", "Enable 1Password SSH integration=false",
                             "--promptMultichoice", "Profiles=common/future-profile/development")
        content = "\n".join(line[1:] for line in diff.splitlines()
                             if line.startswith("+") and not line.startswith("+++"))
        config = tomllib.loads(content)
        self.assertEqual(config["diff"]["exclude"], ["scripts"])
        self.assertNotIn("exclude", config.get("status", {}))
        self.assertNotIn("exclude", config.get("apply", {}))
        data = config["data"]
        self.assertEqual(data["Machine"], "test-machine")
        self.assertTrue(data["ManagedByNimbus"])
        self.assertFalse(data["onePasswordSsh"])
        machine = ["common", "future-profile", "development"] if sys.platform == "linux" else []
        self.assertEqual(data["Profiles"], machine)
        self.assertEqual(data["profiles"], list(dict.fromkeys(["common"] + platforms[sys.platform] + machine)))
        self.assertFalse((self.root / "home/chezmoi.toml").exists())
        self.assertFalse((self.root / "home/.config").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
