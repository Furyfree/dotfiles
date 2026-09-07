#!/usr/bin/env python3
"""Exercise SSH rendering in disposable homes with a strict fake op, never a vault."""

import base64
import json
from pathlib import Path
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import tomllib
import unittest


REPO = Path(__file__).resolve().parents[1]
CHEZMOI = shutil.which("chezmoi")
SSH = shutil.which("ssh")
SSH_KEYGEN = shutil.which("ssh-keygen")
KEYS = {"github": "n6imsp5vfs5nmlt5rmxgs6zdci", "homelab": "3ppqekfxnmjtg2iapnr5d7gewi"}
AGENT = ".config/1Password/ssh/agent.toml"
TARGETS = (".ssh/config", ".ssh/github.pub", ".ssh/homelab.pub", AGENT)
HOSTS = """Host test-lab
    HostName 192.0.2.10
    User root
    IdentityFile ~/.ssh/homelab.pub
    IdentitiesOnly yes
    PreferredAuthentications publickey
"""


def public_key(byte):
    # Synthetic public bytes only; no private key exists or is generated.
    fields = (b"ssh-ed25519", bytes([byte]) * 32)
    blob = b"".join(struct.pack(">I", len(field)) + field for field in fields)
    return "ssh-ed25519 " + base64.b64encode(blob).decode()


@unittest.skipUnless(CHEZMOI, "chezmoi is not installed")
@unittest.skipUnless(sys.platform in ("linux", "darwin"), "SSH integration is deferred on this platform")
class OnePasswordSsh(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="dotfiles-ssh-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.env = {"HOME": str(self.home), "USERPROFILE": str(self.home),
                    "PATH": str(self.bin), "XDG_CONFIG_HOME": str(self.home / ".config"),
                    "XDG_CACHE_HOME": str(self.root / "cache"),
                    "XDG_DATA_HOME": str(self.root / "data"),
                    "XDG_STATE_HOME": str(self.root / "state"),
                    "FAKE_ROOT": str(self.root)}
        self.config = self.home / "chezmoi.toml"
        self.args = [CHEZMOI, "--source", str(REPO), "--destination", str(self.home),
                     "--config", str(self.config), "--cache", str(self.root / "cache/chezmoi"),
                     "--persistent-state", str(self.root / "chezmoi-state.boltdb"), "--no-tty"]
        # Render the real init template without op or the live user's config.
        result = self.run_chezmoi("init", "--dry-run", "--verbose",
                                 "--promptString", "Machine=ssh-test",
                                 "--promptBool", "ManagedByNimbus=false",
                                 "--promptBool", "Enable 1Password SSH integration=true",
                                 "--promptMultichoice", "Profiles=common")
        self.assertEqual(result.returncode, 0, result.stderr)
        content = "\n".join(line[1:] for line in result.stdout.splitlines()
                            if line.startswith("+") and not line.startswith("+++"))
        self.assertEqual(tomllib.loads(content)["secret"]["command"], "op")
        self.assertFalse(tomllib.loads(content)["onepassword"]["prompt"])
        self.config.write_text(content)
        self.payload = {"document": HOSTS, **{item: public_key(i)
                       for i, item in enumerate(KEYS.values(), 1)}}
        self.save_payload()
        fake = self.bin / "op"
        fake.write_text(f"#!{sys.executable}\n" + '''import json, os, pathlib, sys
root = pathlib.Path(os.environ["FAKE_ROOT"])
args = sys.argv[1:]
with (root / "calls").open("a") as log:
    log.write(json.dumps(args) + "\\n")
payload = json.loads((root / "payload.json").read_text())
if args == ["--version"]:
    print("2.32.0")
elif args[:2] == ["document", "get"] and args[2:] == ["3223bqk2tzqdut7gdhiqjyqj34"]:
    if payload.get("failure") == "document":
        sys.exit("fake: vault locked or authentication denied")
    print(payload["document"], end="")
elif (len(args) == 7 and args[:2] == ["item", "get"]
      and args[2] in payload
      and args[3:] == ["--fields", "label=public key", "--format", "json"]):
    if payload.get("failure") == "key":
        sys.exit("fake: item unavailable")
    print(json.dumps({"id": "public_key", "label": "public key", "value": payload[args[2]]}))
else:
    sys.exit("fake: unexpected op arguments: " + repr(args))
''')
        fake.chmod(0o700)

    def save_payload(self):
        (self.root / "payload.json").write_text(json.dumps(self.payload))

    def run_chezmoi(self, *args, platform="linux", enabled=True):
        override = {"chezmoi": {"os": platform}, "profiles": ["common"]}
        if enabled is not None:
            override["onePasswordSsh"] = enabled
        return subprocess.run(self.args + ["--override-data", json.dumps(override), *args],
                              cwd=self.root, env=self.env, text=True, capture_output=True, timeout=20)

    def dump(self, **kwargs):
        result = self.run_chezmoi("dump", "--format=json", **kwargs)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_platform_gating_and_legacy_data_without_op(self):
        (self.bin / "op").unlink()
        for platform, enabled in (("linux", False), ("darwin", False),
                                  ("windows", False), ("windows", True)):
            with self.subTest(platform=platform, enabled=enabled):
                paths = self.dump(platform=platform, enabled=enabled)
                for target in (*TARGETS, ".ssh", "AppData/Local/1Password/config/ssh/agent.toml"):
                    self.assertNotIn(target, paths)
        self.config.write_text("")
        for target in TARGETS:
            self.assertNotIn(target, self.dump(enabled=None))
        self.assertFalse((self.root / "calls").exists())

    def test_platform_rendering_and_key_selection(self):
        sockets = {"linux": "~/.1password/agent.sock",
                   "darwin": '"~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock"'}
        for platform, socket in sockets.items():
            with self.subTest(platform=platform):
                paths = self.dump(platform=platform)
                config = paths[".ssh/config"]["contents"]
                self.assertTrue(config.startswith(HOSTS.rstrip()))
                self.assertIn("Host *\n    IdentityAgent " + socket, config)
                self.assertEqual(tomllib.loads(paths[AGENT]["contents"]),
                                 {"ssh-keys": [{"item": item} for item in KEYS.values()]})
                for role, item in KEYS.items():
                    self.assertEqual(paths[f".ssh/{role}.pub"]["contents"].strip(), self.payload[item])
                self.assertNotIn("AppData/Local/1Password/config/ssh/agent.toml", paths)
        calls = [json.loads(line) for line in (self.root / "calls").read_text().splitlines()]
        for item in KEYS.values():
            self.assertIn(["item", "get", item, "--fields", "label=public key", "--format", "json"], calls)

    @unittest.skipUnless(SSH, "OpenSSH client is not installed")
    def test_native_ssh_config_without_connecting(self):
        for platform in ("linux", "darwin"):
            config = self.root / "ssh-config"
            config.write_text(self.dump(platform=platform)[".ssh/config"]["contents"])
            for host, user, key in (("test-lab", "root", "homelab"), ("github.com", "git", "github")):
                result = subprocess.run([SSH, "-G", "-F", str(config), host], env=self.env,
                                        text=True, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"user {user}\n", result.stdout)
                self.assertIn(f"identityfile ~/.ssh/{key}.pub\n", result.stdout)
                self.assertIn("identitiesonly yes\n", result.stdout)
                socket = ("/.1password/agent.sock" if platform == "linux" else
                          "/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock")
                agent = next(line for line in result.stdout.splitlines() if line.startswith("identityagent "))
                self.assertTrue(agent.endswith(socket), agent)
                self.assertEqual(result.stdout.count("identityfile "), 1)
                if host == "test-lab":
                    self.assertIn("hostname 192.0.2.10\n", result.stdout)
                    self.assertIn("preferredauthentications publickey\n", result.stdout)

    def test_apply_permissions_and_disable_preserves_files(self):
        (self.home / ".ssh").mkdir(mode=0o755)
        unrelated = self.home / ".ssh/keep-existing"
        unrelated.write_text("unmanaged test file\n")
        result = self.run_chezmoi("apply", "--exclude=scripts")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(stat.S_IMODE((self.home / ".ssh").stat().st_mode), 0o700)
        for target in TARGETS[:3]:
            self.assertEqual(stat.S_IMODE((self.home / target).stat().st_mode), 0o600)
        before = {target: (self.home / target).read_bytes() for target in TARGETS}
        result = self.run_chezmoi("apply", "--exclude=scripts", enabled=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        for target, contents in before.items():
            self.assertEqual((self.home / target).read_bytes(), contents)
        self.assertEqual(unrelated.read_text(), "unmanaged test file\n")

    @unittest.skipUnless(SSH_KEYGEN, "ssh-keygen is not installed")
    def test_rendered_public_keys_parse_without_private_keys(self):
        paths = self.dump()
        for role in KEYS:
            path = self.root / f"{role}.pub"
            path.write_text(paths[f".ssh/{role}.pub"]["contents"])
            result = subprocess.run([SSH_KEYGEN, "-l", "-f", str(path)], env=self.env,
                                    text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_failed_retrieval_preserves_existing_target(self):
        (self.home / ".ssh").mkdir(mode=0o700)
        for failure, target in (("document", ".ssh/config"), ("key", ".ssh/homelab.pub")):
            with self.subTest(failure=failure):
                path = self.home / target
                path.write_text("existing test content\n")
                self.payload["failure"] = failure
                self.save_payload()
                result = self.run_chezmoi("apply", "--exclude=scripts", str(path))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("fake:", result.stderr)
                self.assertEqual(path.read_text(), "existing test content\n")

    def test_empty_document_and_invalid_public_key_fail(self):
        for target, field, value in ((".ssh/config", "document", " \n"),
                                     (".ssh/homelab.pub", KEYS["homelab"], ""),
                                     (".ssh/homelab.pub", KEYS["homelab"], "not a public key")):
            with self.subTest(target=target, value=value):
                self.payload[field] = value
                self.save_payload()
                result = self.run_chezmoi("cat", str(self.home / target))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("1Password SSH", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_missing_op_and_skip_secrets(self):
        (self.bin / "op").unlink()
        for target in TARGETS[:3]:
            result = self.run_chezmoi("cat", str(self.home / target))
            self.assertNotEqual(result.returncode, 0)
        result = self.run_chezmoi("--skip-secrets", "dump", "--format=json")
        self.assertEqual(result.returncode, 0, result.stderr)
        paths = json.loads(result.stdout)
        for target in TARGETS[:3]:
            self.assertNotIn(target, paths)


if __name__ == "__main__":
    unittest.main(verbosity=2)
