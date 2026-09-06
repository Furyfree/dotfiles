#!/usr/bin/env python3
"""Render VSCodium configuration without launching it or changing live state."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


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

    def render(self, platform, noctalia=False, legacy=False):
        data = {"chezmoi": {"os": platform}, "onePasswordSsh": False}
        if not legacy:
            data["profiles"] = ["common", "hyprland-noctalia"] if noctalia else ["common"]
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"), "--cache", str(self.root / "cache/chezmoi"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"), "--skip-secrets",
            "--override-data", json.dumps(data), "dump", "--format=json",
        ], env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        warning = "chezmoi: warning: config file template has changed, run chezmoi init to regenerate config file\n"
        self.assertEqual(result.stderr.replace(warning, ""), "")
        return {name: entry["contents"] for name, entry in json.loads(result.stdout).items()
                if entry["type"] == "file"}

    def test_platform_targets_and_theme_ownership(self):
        for platform, target in TARGETS.items():
            for noctalia in (False, True):
                with self.subTest(platform=platform, noctalia=noctalia):
                    files = self.render(platform, noctalia)
                    managed = {name for name in files if "/VSCodium/" in name}
                    self.assertEqual(managed, {f"{target}/settings.json", f"{target}/keybindings.json"})
                    self.assertFalse(any(name.startswith((".config/noctalia/", ".vscode-oss/")) for name in files))
                    settings = strict_json(files[f"{target}/settings.json"])
                    enabled = platform == "linux" and noctalia
                    self.assertEqual(settings["workbench.colorTheme"], "NoctaliaTheme" if enabled else "Atom One Dark")
                    self.assertEqual(settings["window.autoDetectColorScheme"], not enabled)
                    if enabled:
                        self.assertNotIn("workbench.preferredDarkColorTheme", settings)
                    else:
                        self.assertEqual(settings["workbench.preferredLightColorTheme"], "Atom One Light")

    def test_shared_editor_behavior_and_privacy(self):
        expected = {
            "editor.fontSize": 15, "terminal.integrated.fontSize": 15,
            "editor.cursorStyle": "block", "editor.lineNumbers": "on",
            "editor.fontLigatures": False, "terminal.integrated.fontLigatures.enabled": False,
            "editor.formatOnSave": False, "editor.formatOnPaste": False,
            "editor.formatOnType": False, "files.autoSave": "off", "prettier.enable": False,
            "workbench.editor.enablePreview": False, "workbench.editor.enablePreviewFromQuickOpen": False,
            "editor.renderWhitespace": "selection", "editor.inlayHints.enabled": "off",
            "editor.bracketPairColorization.enabled": True, "editor.minimap.enabled": False,
            "errorLens.enabled": True, "errorLens.messageBackgroundMode": "none",
            "workbench.sideBar.location": "left", "workbench.panel.defaultLocation": "bottom",
            "terminal.integrated.cwd": "${workspaceFolder}",
            "tinymist.exportPdf": "onSave", "tinymist.outputPath": "$dir/$name",
            "security.workspace.trust.enabled": True, "chat.tools.global.autoApprove": False,
            "telemetry.telemetryLevel": "off", "redhat.telemetry.enabled": False,
            "gitlens.telemetry.enabled": False, "files.hotExit": "onExitAndWindowClose",
            "window.restoreWindows": "none", "workbench.startupEditor": "newUntitledFile",
        }
        for platform, target in TARGETS.items():
            with self.subTest(platform=platform):
                settings = strict_json(self.render(platform)[f"{target}/settings.json"])
                self.assertEqual({key: settings[key] for key in expected}, expected)
                self.assertEqual(settings["editor.fontFamily"], settings["terminal.integrated.fontFamily"])
                self.assertEqual(settings["[go]"], {
                    "editor.formatOnSave": False,
                    "editor.codeActionsOnSave": {"source.organizeImports": "never"},
                })
                self.assertEqual(settings["[zig]"], {"editor.formatOnSave": False})
                self.assertEqual(settings["[python]"], {"editor.formatOnType": False})
                self.assertFalse(any(key.startswith(("terminal.integrated.defaultProfile.",
                    "terminal.integrated.profiles.", "terminal.integrated.env.", "chatgpt.",
                    "claudeCode.", "github.copilot.")) for key in settings))
                for key in ("workbench.colorCustomizations", "editor.tokenColorCustomizations",
                            "FSharp.dotnetRoot", "code-runner.executorMap", "chat.model"):
                    self.assertNotIn(key, settings)

    def test_shortcut_parity_and_contexts(self):
        for platform, target in TARGETS.items():
            with self.subTest(platform=platform):
                bindings = strict_json(self.render(platform)[f"{target}/keybindings.json"])
                self.assertEqual(len(bindings), 8)
                keys = {binding["key"]: binding for binding in bindings}
                self.assertEqual(len(keys), len(bindings))
                mod = "cmd" if platform == "darwin" else "ctrl"
                self.assertEqual(keys[f"{mod}+alt+shift+j"]["command"], "workbench.action.terminal.toggleTerminal")
                self.assertEqual(keys[f"{mod}+shift+b"]["command"], "outline.focus")
                self.assertEqual(keys[f"{mod}+alt+b"]["command"], "workbench.action.toggleAuxiliaryBar")
                self.assertEqual(keys["alt+shift+f"]["command"], "editor.action.formatDocument")
                self.assertIn("!editorReadonly", keys["alt+shift+f"]["when"])
                self.assertEqual(keys["ctrl+shift+g"]["command"], "workbench.view.scm")
                self.assertEqual(keys[f"{mod}+alt+g"]["command"], "git-graph.view")
                chat = keys["ctrl+cmd+i" if platform == "darwin" else "ctrl+alt+i"]
                self.assertEqual(chat["command"], "workbench.action.chat.open")
                self.assertEqual(chat["args"], {"mode": "ask"})
                self.assertEqual(chat["when"], "chatIsEnabled && !terminalFocus")
                self.assertNotIn(f"{mod}+shift+t", keys)
                self.assertNotIn(f"{mod}+shift+o", keys)
                self.assertNotIn(f"{mod}+shift+f", keys)
                if platform == "darwin":
                    self.assertEqual(keys["cmd+alt+o"]["command"], "workbench.action.openRecent")
                else:
                    self.assertEqual(keys["ctrl+shift+a"]["command"], "editor.action.blockComment")

    def test_wrappers_and_legacy_data(self):
        for target in ("dot_config/VSCodium/User", "Library/Application Support/VSCodium/User",
                       "AppData/Roaming/VSCodium/User"):
            for name in ("settings", "keybindings"):
                wrapper = (REPO / "home" / target / f"{name}.json.tmpl").read_text()
                self.assertEqual(wrapper.strip(), '{{- template "configs/vscodium/' + name + '.json" . -}}')
        settings = strict_json(self.render("linux", legacy=True)[".config/VSCodium/User/settings.json"])
        self.assertEqual(settings["workbench.colorTheme"], "Atom One Dark")

    def test_product_configuration_renders_but_stays_ignored(self):
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
            "--skip-secrets", "execute-template",
        ], input='{{ template "configs/vscodium/product.json" . }}',
            env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        source = (REPO / "home/.chezmoitemplates/configs/vscodium/product.json").read_text()
        configuration = strict_json(source)
        self.assertEqual(strict_json(result.stdout), configuration)
        self.assertEqual(configuration["extensionsGallery"]["serviceUrl"],
                         "https://marketplace.visualstudio.com/_apis/public/gallery")
        for platform in TARGETS:
            files = self.render(platform)
            self.assertFalse(any(name.endswith("/VSCodium/product.json") for name in files))

    def render_installer(self, platform, suffix):
        source = (REPO / f"home/run_after_install-vscodium-extensions.{suffix}.tmpl").read_text()
        result = subprocess.run([
            CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
            "--config", str(self.root / "chezmoi.toml"),
            "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
            "--skip-secrets", "--override-data", json.dumps({"chezmoi": {"os": platform}}),
            "execute-template",
        ], input=source, env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_installers_render_from_manifest_but_are_ignored(self):
        manifest = strict_json((REPO / "VSCODIUM_EXTENSIONS.json").read_text())
        for platform in TARGETS:
            with self.subTest(platform=platform):
                for suffix in ("sh", "ps1"):
                    script = self.render_installer(platform, suffix)
                    if (suffix == "ps1") != (platform == "windows"):
                        self.assertEqual(script.strip(), "")
                        continue
                    for extension in manifest["install"]:
                        self.assertIn(extension, script)
                    for extension in manifest["manual"]:
                        self.assertNotIn(extension, script)
                    if suffix == "sh" and os.name == "posix":
                        result = subprocess.run(["/bin/sh", "-n"], input=script,
                            capture_output=True, text=True, timeout=10)
                        self.assertEqual(result.returncode, 0, result.stderr)
                result = subprocess.run([
                    CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
                    "--config", str(self.root / "chezmoi.toml"),
                    "--persistent-state", str(self.root / "chezmoi-state.boltdb"),
                    "--override-data", json.dumps({"chezmoi": {"os": platform}}), "ignored",
                ], env=self.env, cwd=self.root, capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stderr)
                for suffix in ("sh", "ps1"):
                    self.assertIn(f"install-vscodium-extensions.{suffix}", result.stdout.splitlines())

    def fake_cli(self, installed=(), name="codium"):
        bin_dir = self.root / "bin with spaces"
        bin_dir.mkdir()
        for tool in ("grep", "tr"):
            (bin_dir / tool).symlink_to(shutil.which(tool))
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
else:
    sys.exit("unexpected CLI arguments")
''')
        cli.chmod(0o700)
        return self.env | {"PATH": str(bin_dir), "FAKE_STATE": str(state)}, state, cli

    def run_installer(self, env):
        return subprocess.run(["/bin/sh"], input=self.render_installer("linux", "sh"),
            env=env, cwd=self.root, capture_output=True, text=True, timeout=30)

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

    @unittest.skipUnless(os.name == "posix", "POSIX installer execution requires /bin/sh")
    def test_installer_missing_cli_and_listing_failure(self):
        env, state, cli = self.fake_cli()
        result = self.run_installer(env | {"FAKE_LIST_FAIL": "1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fake listing failed", result.stderr)
        self.assertEqual(strict_json(state.read_text())["calls"], [["--list-extensions"]])
        cli.unlink()
        result = self.run_installer(env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CLI is required", result.stderr)
        (cli.parent / "id").write_text("#!/bin/sh\nprintf '%s\\n' 0\n")
        result = self.run_installer(env)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not root", result.stderr)

    @unittest.skipUnless(os.name == "posix", "POSIX installer execution requires /bin/sh")
    def test_installer_propagates_install_failure_and_verifies_success(self):
        desired = strict_json((REPO / "VSCODIUM_EXTENSIONS.json").read_text())["install"]
        env, _, _ = self.fake_cli(desired[:-1])
        result = self.run_installer(env | {"FAKE_INSTALL_FAIL": "1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fake install failed", result.stderr)
        result = self.run_installer(env | {"FAKE_NOOP": "1"})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("extension missing after installation", result.stderr)


class Extensions(unittest.TestCase):
    def test_inventory(self):
        manifest = strict_json((REPO / "VSCODIUM_EXTENSIONS.json").read_text())
        self.assertEqual(set(manifest), {"install", "manual"})
        self.assertEqual(len(manifest["install"]), 52)
        self.assertEqual(len(manifest["manual"]), 8)
        ids = manifest["install"] + manifest["manual"]
        self.assertEqual(len(ids), len(set(ids)))
        for group in manifest.values():
            self.assertEqual(group, sorted(group))
            for extension in group:
                self.assertRegex(extension, r"^[a-z0-9-]+\.[a-z0-9-]+$")
        self.assertEqual(set(manifest["manual"]), {
            "github.copilot-chat", "ms-dotnettools.csharp", "ms-python.vscode-pylance",
            "ms-vscode-remote.remote-ssh", "ms-vscode-remote.remote-ssh-edit",
            "ms-vscode.remote-explorer", "visualstudioexptteam.intellicode-api-usage-examples",
            "visualstudioexptteam.vscodeintellicode",
        })
        for extension in ("ms-toolsai.jupyter", "grapecity.gc-excelviewer", "cweijan.vscode-office",
                          "pomdtr.excalidraw-editor", "myriad-dreamin.tinymist", "golang.go",
                          "noctalia.noctaliatheme", "akamud.vscode-theme-onedark",
                          "akamud.vscode-theme-onelight", "usernamehw.errorlens"):
            self.assertIn(extension, manifest["install"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
