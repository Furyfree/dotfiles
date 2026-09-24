"""Render VSCodium configuration without launching it or changing live state."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")
TARGETS = {
    "linux": ".config/VSCodium/User",
    "darwin": "Library/Application Support/VSCodium/User",
    "windows": "AppData/Roaming/VSCodium/User",
}


def strict_json(text):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(text, object_pairs_hook=unique_keys)


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
class VSCodium(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="dotfiles-vscodium-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        self.env = {
            "HOME": str(self.home), "USERPROFILE": str(self.home), "PATH": "",
            "XDG_CONFIG_HOME": str(self.home / ".config"),
            "XDG_DATA_HOME": str(self.root / "data"),
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "XDG_STATE_HOME": str(self.root / "state"),
        }

    def render(self, platform, noctalia=False, legacy=False, entry_type="file"):
        data = {"chezmoi": {"os": platform}, "onePasswordSsh": False}
        if not legacy:
            data["profiles"] = ["common", "hyprland-noctalia"] if noctalia else ["common"]
        roots = {"linux": [".config", ".local"],
                 "darwin": [".config", "Library/Application Support"],
                 "windows": [".config", "AppData/Roaming"]}[platform]
        if entry_type == "script":
            targets, selected = [], ["-i", "scripts"]
        else:
            targets = [str(self.home / root) for root in roots]
            selected = []
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"), "--cache", str(self.root / "cache/chezmoi"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"), "--skip-secrets",
            "--override-data", json.dumps(data), "dump", "--format=json", *selected, *targets,
        ], env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        warning = "chezmoi: warning: config file template has changed, run chezmoi init to regenerate config file\n"
        self.assertEqual(result.stderr.replace(warning, ""), "")
        return {name: entry["contents"] for name, entry in json.loads(result.stdout).items()
                if entry["type"] == entry_type}

    def test_platform_targets_and_theme_ownership(self):
        for platform, target in TARGETS.items():
            for noctalia in (False, True):
                with self.subTest(platform=platform, noctalia=noctalia):
                    files = self.render(platform, noctalia)
                    managed = {name for name in files if "/VSCodium/" in name}
                    self.assertEqual(managed, {f"{target}/settings.json", f"{target}/keybindings.json",
                                               f"{target.removesuffix('/User')}/product.json"})
                    self.assertFalse(any(name.startswith((".vscode-oss/",)) for name in files))
                    settings = strict_json(files[f"{target}/settings.json"])
                    enabled = platform == "linux" and noctalia
                    if enabled:
                        self.assertEqual(settings["workbench.colorTheme"], "NoctaliaTheme")
                        self.assertNotIn("workbench.preferredDarkColorTheme", settings)

    def test_privacy_and_local_runtime_ownership(self):
        expected = {
            "security.workspace.trust.enabled": True,
            "telemetry.telemetryLevel": "off", "redhat.telemetry.enabled": False,
            "gitlens.telemetry.enabled": False,
        }
        for platform, target in TARGETS.items():
            with self.subTest(platform=platform):
                settings = strict_json(self.render(platform)[f"{target}/settings.json"])
                self.assertEqual({key: settings[key] for key in expected}, expected)
                self.assertFalse(any(key.startswith(("terminal.integrated.defaultProfile.",
                    "terminal.integrated.profiles.", "terminal.integrated.env.", "chatgpt.",
                    "claudeCode.", "github.copilot.")) for key in settings))
                for key in ("FSharp.dotnetRoot", "code-runner.executorMap", "chat.model"):
                    self.assertNotIn(key, settings)

    def test_keybindings_have_no_duplicate_key_and_context(self):
        for platform, target in TARGETS.items():
            with self.subTest(platform=platform):
                bindings = strict_json(self.render(platform)[f"{target}/keybindings.json"])
                keys = [(binding["key"], binding.get("when", "")) for binding in bindings]
                self.assertEqual(len(keys), len(set(keys)))

    def test_legacy_data_renders_valid_settings(self):
        strict_json(self.render("linux", legacy=True)[".config/VSCodium/User/settings.json"])

    def test_product_configuration_is_managed(self):
        source = (REPO / "home/.chezmoitemplates/configs/vscodium/product.json").read_text()
        configuration = strict_json(source)
        self.assertEqual(configuration["extensionsGallery"]["serviceUrl"],
                         "https://open-vsx.org/vscode/gallery")
        for platform, target in TARGETS.items():
            with self.subTest(platform=platform):
                files = self.render(platform)
                self.assertEqual(strict_json(files[f"{target.removesuffix('/User')}/product.json"]), configuration)

    def render_installer(self, platform, suffix):
        source = (REPO / f"home/run_after_install-vscodium-extensions.{suffix}.tmpl").read_text()
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
            "--skip-secrets", "--override-data", json.dumps({"chezmoi": {"os": platform}}),
            "execute-template",
        ], input=source, env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_managed_installers_match_platform_and_manifest(self):
        manifest = strict_json((REPO / "VSCODIUM_EXTENSIONS.json").read_text())
        for platform in TARGETS:
            with self.subTest(platform=platform):
                scripts = self.render(platform, entry_type="script")
                for suffix in ("sh", "ps1"):
                    target = f"install-vscodium-extensions.{suffix}"
                    script = self.render_installer(platform, suffix)
                    if (suffix == "ps1") != (platform == "windows"):
                        self.assertEqual(script.strip(), "")
                        self.assertNotIn(target, scripts)
                        continue
                    self.assertEqual(scripts[target], script)
                    for extension in manifest["install"]:
                        self.assertIn(extension, script)
                    for extension in manifest["manual"]:
                        self.assertNotIn(extension, script)
                    if suffix == "sh" and os.name == "posix":
                        result = subprocess.run(["/bin/sh", "-n"], input=script,
                            capture_output=True, text=True, timeout=10, check=False)
                        self.assertEqual(result.returncode, 0, result.stderr)

    def fake_cli(self, installed=(), name="codium"):
        bin_dir = self.root / "bin with spaces"
        bin_dir.mkdir(exist_ok=True)
        for tool in ("grep", "tr"):
            link = bin_dir / tool
            if not link.exists():
                link.symlink_to(shutil.which(tool))
        identity = bin_dir / "id"
        identity.write_text("#!/bin/sh\nprintf '%s\\n' 1000\n")
        identity.chmod(0o700)
        state = self.root / "fake-cli-state.json"
        state.write_text(json.dumps({"installed": list(installed), "calls": []}))
        cli = bin_dir / name
        cli.write_text(f"#!{sys.executable}\n" + '''import json, os, sys
from pathlib import Path
path = Path(os.environ["FAKE_STATE"])
state = json.loads(path.read_text())
args = sys.argv[1:]
state["calls"].append(args)
path.write_text(json.dumps(state))
if args == ["--list-extensions"]:
    if os.environ.get("FAKE_LIST_FAIL"):
        print("fake listing failed", file=sys.stderr)
        sys.exit(1)
    print("\\r\\n".join(item.upper() for item in state["installed"]))
elif len(args) == 2 and args[0] == "--install-extension":
    if os.environ.get("FAKE_INSTALL_FAIL"):
        print("fake install failed", file=sys.stderr)
        sys.exit(1)
    if not os.environ.get("FAKE_NOOP"):
        state["installed"].append(args[1])
        path.write_text(json.dumps(state))
elif len(args) == 2 and args[0] == "--uninstall-extension":
    wanted = args[1].lower()
    state["installed"] = [item for item in state["installed"] if item.lower() != wanted]
    path.write_text(json.dumps(state))
else:
    sys.exit("unexpected CLI arguments")
''')
        cli.chmod(0o700)
        return self.env | {"PATH": str(bin_dir), "FAKE_STATE": str(state)}, state, cli

    def run_installer(self, env):
        return subprocess.run(["/bin/sh"], input=self.render_installer("linux", "sh"),
            env=env, cwd=self.root, capture_output=True, text=True, timeout=30, check=False)

    def run_installer_tty(self, env, replies="\n"):
        path = self.root / "installer.sh"
        path.write_text(self.render_installer("linux", "sh"))
        path.chmod(0o700)
        import pty
        import select
        import time
        # Popen, not pty.fork: forking a threaded test worker can deadlock.
        fd, tty = pty.openpty()
        process = subprocess.Popen(["/bin/sh", str(path)], stdin=tty, stdout=tty, stderr=tty,
                                   cwd=self.root, env=env, start_new_session=True)
        os.close(tty)
        output = b""
        sent = False
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            ready, _, _ = select.select([fd], [], [], 0.2)
            if ready:
                try:
                    chunk = os.read(fd, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                output += chunk
                if not sent and b"[Y/n]" in output:
                    os.write(fd, replies.encode())
                    sent = True
            if process.poll() is not None:
                break
        else:
            process.kill()
            process.wait()
            self.fail("installer tty timed out: " + output.decode(errors="replace"))
        process.wait()
        os.close(fd)
        return subprocess.CompletedProcess(process.args, process.returncode,
                                           output.decode(errors="replace"), "")

    @unittest.skipUnless(os.name == "posix", "POSIX installer execution requires /bin/sh")
    def test_installer_is_repeatable_and_preserves_unrelated_extensions(self):
        desired = strict_json((REPO / "VSCODIUM_EXTENSIONS.json").read_text())["install"]
        env, state, _ = self.fake_cli([desired[0], "unrelated.extension"], name="vscodium")
        result = self.run_installer(env)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = strict_json(state.read_text())
        self.assertEqual(set(data["installed"]), set(desired) | {"unrelated.extension"})
        installs = [args for args in data["calls"] if args[0] == "--install-extension"]
        self.assertEqual(installs, [["--install-extension", item] for item in desired[1:]])
        result = self.run_installer(env)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = strict_json(state.read_text())
        self.assertEqual([args for args in data["calls"] if args[0] == "--install-extension"], installs)
        self.assertEqual(result.stdout, "", "unchanged verification should be quiet")
        self.assertEqual([args for args in data["calls"] if args[0] == "--uninstall-extension"], [])

    @unittest.skipUnless(os.name == "posix", "POSIX installer execution requires /bin/sh")
    def test_installer_prompts_to_remove_leftover_extensions(self):
        desired = strict_json((REPO / "VSCODIUM_EXTENSIONS.json").read_text())["install"]
        env, state, _ = self.fake_cli(desired + ["ms-python.vscode-pylance", "ms-python.isort"])
        result = self.run_installer_tty(env, "y\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("These extensions will be uninstalled:", result.stdout)
        self.assertIn("ms-python.vscode-pylance", result.stdout)
        data = strict_json(state.read_text())
        self.assertEqual(set(data["installed"]), set(desired))
        env, state, _ = self.fake_cli(desired + ["ms-python.vscode-pylance"])
        result = self.run_installer_tty(env, "n\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(set(strict_json(state.read_text())["installed"]),
                         set(desired) | {"ms-python.vscode-pylance"})

    @unittest.skipUnless(os.name == "posix", "POSIX installer execution requires /bin/sh")
    def test_installer_prompt_can_skip_install(self):
        desired = strict_json((REPO / "VSCODIUM_EXTENSIONS.json").read_text())["install"]
        env, state, _ = self.fake_cli([desired[0]])
        result = self.run_installer_tty(env, "n\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("These extensions will be installed:", result.stdout)
        self.assertEqual(strict_json(state.read_text())["installed"], [desired[0]])

    @unittest.skipUnless(os.name == "posix", "POSIX installer execution requires /bin/sh")
    def test_installer_missing_cli_and_listing_failure(self):
        env, state, cli = self.fake_cli()
        result = self.run_installer(env | {"FAKE_LIST_FAIL": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("could not list VSCodium extensions", result.stderr)
        self.assertEqual(strict_json(state.read_text())["calls"], [["--list-extensions"]])
        cli.unlink()
        result = self.run_installer(env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("not installed; skipping", result.stderr)
        (cli.parent / "id").write_text("#!/bin/sh\nprintf '%s\\n' 0\n")
        result = self.run_installer(env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not root", result.stderr)

    @unittest.skipUnless(os.name == "posix", "POSIX installer execution requires /bin/sh")
    def test_installer_tolerates_failures_and_reports_them(self):
        desired = strict_json((REPO / "VSCODIUM_EXTENSIONS.json").read_text())["install"]
        env, state, _ = self.fake_cli(desired[:-1])
        result = self.run_installer(env | {"FAKE_INSTALL_FAIL": "1", "DOTFILES_RETRY_DELAY": "0"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("could not install", result.stderr)
        self.assertIn("extensions incomplete", result.stderr)
        self.assertEqual(set(strict_json(state.read_text())["installed"]), set(desired[:-1]))
        result = self.run_installer(env | {"FAKE_NOOP": "1", "DOTFILES_RETRY_DELAY": "0"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("extensions incomplete", result.stderr)


class Extensions(unittest.TestCase):
    def test_extension_manifest_is_valid(self):
        manifest = strict_json((REPO / "VSCODIUM_EXTENSIONS.json").read_text())
        self.assertEqual(set(manifest), {"install", "manual"})
        ids = manifest["install"] + manifest["manual"]
        self.assertEqual(len(ids), len(set(ids)))
        for extension in ids:
            self.assertRegex(extension, r"^[a-z0-9-]+\.[a-z0-9-]+$")


if __name__ == "__main__":
    unittest.main(verbosity=2)
