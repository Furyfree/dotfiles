#!/usr/bin/env python3
"""Check Fastfetch rendering, fixed-height fallbacks and read-only age detection."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
TEMPLATES = REPO / 'home/.chezmoitemplates/configs/fastfetch'
LOGO = REPO / 'home/dot_config/fastfetch/fedora-dot-colon.txt'
FASTFETCH = shutil.which('fastfetch')
CHEZMOI = shutil.which('chezmoi')
LUA = FASTFETCH and 'Lua ' in subprocess.check_output([FASTFETCH, '--list-features'], text=True)

class Fastfetch(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='dotfiles-fastfetch-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / 'home with spaces'
        self.home.mkdir()
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.env = {'HOME': str(self.home), 'USERPROFILE': str(self.home),
                    'PATH': str(self.bin), 'LANG': 'C.UTF-8',
                    'XDG_CONFIG_HOME': str(self.home / '.config'),
                    'XDG_CONFIG_DIRS': str(self.root / 'system-config'),
                    'XDG_CACHE_HOME': str(self.root / 'cache'),
                    'XDG_DATA_HOME': str(self.root / 'data'),
                    'XDG_STATE_HOME': str(self.root / 'state')}
        for name, value in [('stat', '100000'), ('date', '272800'), ('id', '1000')]:
            self.stub(name, f'printf "{value}"')
        self.stub('pgrep', 'exit 1')

    def stub(self, name, body):
        p = self.bin / name
        p.write_text('#!/bin/sh\n' + body + '\n')
        p.chmod(0o755)

    def run_command(self, *args, env=None):
        p = subprocess.run(args, env=env or self.env, cwd=self.root,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotRegex(p.stderr.lower(), r'error|unknown|invalid')
        return p.stdout

    def render(self, platform='linux'):
        output = self.run_command(CHEZMOI, '--source', str(REPO),
            '--destination', str(self.home), '--config', str(self.root / 'chezmoi.toml'),
            '--cache', str(self.root / 'cache/chezmoi'),
            '--persistent-state', str(self.root / 'chezmoi-state.boltdb'), '--skip-secrets',
            '--override-data', json.dumps({'chezmoi': {'os': platform},
                'profiles': ['common'], 'onePasswordSsh': False}), 'dump', '--format=json')
        files = {k: v['contents'] for k, v in json.loads(output).items()
                 if k.startswith('.config/fastfetch/') and v['type'] == 'file'}
        for name, contents in files.items():
            target = self.home / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents)
        return files

    def native(self, config, colored=False):
        path = self.root / 'test.jsonc'
        path.write_text(json.dumps(config))
        return self.run_command(FASTFETCH, '-c', str(path), '--pipe', 'false' if colored else 'true')

    @unittest.skipUnless(CHEZMOI, 'chezmoi unavailable')
    def test_platform_targets(self):
        linux = self.render()
        self.assertEqual(set(linux), {'.config/fastfetch/config.jsonc', '.config/fastfetch/fedora-dot-colon.txt'})
        cfg = json.loads(linux['.config/fastfetch/config.jsonc'])
        self.assertEqual(cfg['logo']['source'], str(self.home / '.config/fastfetch/fedora-dot-colon.txt'))
        for platform in ['darwin', 'windows']:
            files = self.render(platform)
            self.assertEqual(files, {'.config/fastfetch/config.jsonc': (TEMPLATES / 'portable.jsonc').read_text()})

    def test_age_unknown_future_and_elapsed(self):
        script = (TEMPLATES / 'os-age.sh').read_text()
        def age(): return self.run_command('/bin/sh', '-c', script)
        self.assertEqual(age(), '~2 days')
        for birth in ['0', '-1', '', 'nonsense', '999999']:
            self.stub('stat', f'printf "%s" "{birth}"')
            self.assertEqual(age(), 'not recorded')
        self.stub('stat', 'printf 272799')
        self.assertEqual(age(), '<1 day (estimate)')
        self.stub('stat', 'exit 1')
        self.assertEqual(age(), 'not recorded')
        self.stub('stat', 'printf 100000')
        self.stub('date', 'exit 1')
        self.assertEqual(age(), 'not recorded')

    def test_noctalia_requires_running_process(self):
        script = (TEMPLATES / 'noctalia.sh').read_text()
        self.assertEqual(self.run_command('/bin/sh', '-c', script), '')
        self.stub('pgrep', 'exit 0')
        self.assertEqual(self.run_command('/bin/sh', '-c', script), 'Noctalia (desktop shell)')

    @unittest.skipUnless(LUA, 'Fastfetch with Lua unavailable')
    def test_aggregation_and_long_values(self):
        setup = (TEMPLATES / 'format.lua').read_text()
        seed = '''ff.gpus = { {name='GeForce RTX 3080 Lite Hash Rate',vendor='NVIDIA'},
          {name='UHD Graphics 770',vendor='Intel'} }; ff.displays = {
          {width=1920,height=1080,refreshRate='144.001'}, {width=1920,height=1080,refreshRate='144.001'} }'''
        cfg = {'logo': {'type': 'none'}, 'modules': [
            {'type': 'custom', 'format': 'lua:' + setup + '\n' + seed},
            {'type': 'custom', 'key': 'GPU', 'format': 'lua:return ff.text(ff.gpuNames())'},
            {'type': 'custom', 'key': 'Display', 'format': 'lua:return ff.text(ff.displayNames())'},
            {'type': 'custom', 'key': 'Long', 'format': "lua:return ff.text(string.rep('ø', 80))"}]}
        output = self.native(cfg)
        self.assertIn('RTX 3080 + Intel UHD 770', output)
        self.assertIn('2 × 1920×1080 @ 144 Hz', output)
        self.assertIn('ø' * 45 + '…', output)
        self.assertEqual(len(output.strip().splitlines()), 3)
        cfg['modules'][0]['format'] = 'lua:' + setup + "\nff.displays = { {width=2880,height=1800,refreshRate='120'} }"
        output = self.native(cfg)
        self.assertIn('not detected', output)
        self.assertIn('2880×1800 @ 120 Hz', output)
        self.assertNotIn('2 ×', output)

    @unittest.skipUnless(CHEZMOI and LUA, 'Chezmoi / Fastfetch Lua unavailable')
    def test_missing_hardware_keeps_palette_at_row_21(self):
        cfg = json.loads(self.render()['.config/fastfetch/config.jsonc'])
        # Remove detection; keep the initializer and fixed display rows.
        cfg['modules'] = [m for m in cfg['modules'] if m == 'break' or m.get('type') == 'custom']
        out = self.native(cfg, colored=True)
        lines = out.splitlines()
        self.assertEqual(len(LOGO.read_text().splitlines()), 21)
        palette_index = next(i for i, line in enumerate(lines) if '\x1b[40m' in line)
        self.assertEqual(palette_index, 20)
        self.assertIn(LOGO.read_text().splitlines()[-1].strip(), lines[20])
        self.assertEqual(sum('not detected' in line for line in lines), 13)
        self.assertIn('not recorded', out)
        self.assertNotIn('Battery', out)
        # Logo remains monochrome; palette color codes occur only on row 21.
        self.assertFalse(any(re.search(r'\x1b\[(?:3[0-8]|4\d|9\d|10\d)m', line) for line in lines[:20]))

    @unittest.skipUnless(CHEZMOI and LUA, 'Chezmoi / Fastfetch Lua unavailable')
    def test_native_plain_output_and_commands(self):
        cfg = json.loads(self.render()['.config/fastfetch/config.jsonc'])
        commands = [m['text'] for m in cfg['modules'] if isinstance(m, dict) and m['type'] == 'command']
        self.assertEqual(commands, [(TEMPLATES / x).read_text() for x in ['os-age.sh', 'noctalia.sh']])
        out = self.native(cfg)
        self.assertNotIn('\x1b', out)
        self.assertIn('~2 days', out)
        for heading in ['SYSTEM', 'DESKTOP', 'HARDWARE']:
            self.assertIn(heading, out)

if __name__ == '__main__':
    unittest.main(verbosity=2)
