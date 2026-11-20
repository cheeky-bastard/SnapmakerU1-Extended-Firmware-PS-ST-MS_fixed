#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Copyright (c) 2026 cheeky-bastard
"""Exercise normal AFC reboot-link restoration in temporary directories only."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'overlays/mods/afc/03-AFC-Klipper-Add-On/root/usr/local/sbin/afc-restore-modules'


class Persistence(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'AFC-Klipper-Add-On/extras'
        self.target = self.root / 'klipper/klippy/extras'
        self.config = self.root / 'printer_data/config/printer.cfg'
        for path in (self.source, self.target, self.config.parent):
            path.mkdir(parents=True)
        self.config.write_text('[include AFC/*.cfg]\n')
        for name in ('AFC.py', 'AFC_unit.py', 'AFC_lane.py', 'AFC_utils.py', '__init__.py'):
            (self.source / name).write_text('# add-on\n')
        for name in ('AFC.py', 'AFC_unit.py', 'AFC_lane.py'):
            (self.target / name).write_text('# stock lite\n')
        for name in ('extruder_config_bak.py', 'probe_inductance_coil.py', 'print_task_config.py', '__init__.py'):
            (self.target / name).write_text('# protected stock\n')

    def run_restore(self):
        return subprocess.run(['sh', str(SCRIPT)], env=dict(os.environ, AFC_RESTORE_ROOT=str(self.root)),
                              capture_output=True, text=True)

    def test_disabled_is_read_only(self):
        self.config.write_text('# [include AFC/*.cfg]\n')
        self.assertEqual(self.run_restore().returncode, 0)
        self.assertFalse((self.target / 'AFC.py').is_symlink())
        self.assertFalse((self.target / 'AFC.py.lite').exists())

    def test_enabled_restores_links_and_preserves_stock_and_native_modules(self):
        self.assertEqual(self.run_restore().returncode, 0)
        self.assertTrue((self.target / 'AFC.py').is_symlink())
        self.assertEqual((self.target / 'AFC.py.lite').read_text(), '# stock lite\n')
        for name in ('extruder_config_bak.py', 'probe_inductance_coil.py', 'print_task_config.py', '__init__.py'):
            self.assertEqual((self.target / name).read_text(), '# protected stock\n')
        self.assertEqual(self.run_restore().returncode, 0)
        self.assertEqual((self.target / 'AFC.py.lite').read_text(), '# stock lite\n')

    def test_conflict_fails_before_any_module_link_is_changed(self):
        (self.source / 'extruder_config_bak.py').write_text('# unexpected\n')
        self.assertNotEqual(self.run_restore().returncode, 0)
        self.assertFalse((self.target / 'AFC.py').is_symlink())
        self.assertFalse((self.target / 'AFC.py.lite').exists())
        self.assertEqual((self.target / 'extruder_config_bak.py').read_text(), '# protected stock\n')

    def test_missing_provider_fails_when_enabled(self):
        for path in self.source.iterdir():
            path.unlink()
        self.assertNotEqual(self.run_restore().returncode, 0)
        self.assertFalse((self.target / 'AFC.py').is_symlink())


if __name__ == '__main__':
    unittest.main()
