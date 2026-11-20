#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Copyright (c) 2026 cheeky-bastard
"""Check disabled config defaults, macro rendering and safe duplicate handling."""
import configparser
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / 'overlays/mods/phase/96-bundled-config/root'
CFG = OVERLAY / 'usr/local/share/firmware-config/extended/klipper/71_phase.cfg'
INIT = OVERLAY / 'etc/init.d/S49phase-config'


class BundledConfig(unittest.TestCase):
    def setUp(self):
        self.config = configparser.RawConfigParser()
        self.config.read_string(CFG.read_text())
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.default = self.base / 'defaults'
        self.root = self.base / 'config'
        self.active = self.root / 'extended/klipper/71_phase.cfg'
        self.default.mkdir()
        self.active.parent.mkdir(parents=True)
        (self.default / '71_phase.cfg').write_bytes(CFG.read_bytes())
        self.active.write_bytes(CFG.read_bytes())

    def run_guard(self):
        subprocess.run(['sh', str(INIT), 'start'], check=True, capture_output=True,
                       env=dict(os.environ, PHASE_CONFIG_ROOT=str(self.root),
                                PHASE_DEFAULT_DIR=str(self.default)))

    def test_only_expected_sections_and_phase_off(self):
        self.assertEqual(set(self.config.sections()), {'phase_stepping stepper_x',
                         'phase_stepping stepper_y', 'phase_calibrate', 'gcode_macro PHASE_CALIBRATE_XY'})
        for name in ('stepper_x', 'stepper_y'):
            self.assertFalse(self.config.getboolean('phase_stepping ' + name, 'auto_enable'))
        self.assertEqual(self.config.get('phase_calibrate', 'accel_chip'), 'lis2dw e0_lis2dw')

    def render(self, homed):
        env = Environment(undefined=StrictUndefined, variable_start_string='{', variable_end_string='}')
        body = self.config.get('gcode_macro PHASE_CALIBRATE_XY', 'gcode')
        output = env.from_string(body).render(printer=SimpleNamespace(toolhead=SimpleNamespace(homed_axes=homed)))
        return [line.strip() for line in output.splitlines() if line.strip()]

    def test_unhomed_macro_homes_before_tool_and_calibrates_without_saving(self):
        commands = self.render('')
        self.assertEqual(commands[:2], ['G28', 'T0 A0'])
        self.assertEqual(sum(x.startswith('PHASE_STEPPING_CALIBRATE ') for x in commands), 2)
        self.assertTrue(all('GRAPH=0' in x for x in commands if x.startswith('PHASE_STEPPING_CALIBRATE ')))
        self.assertFalse(any(x.split()[0] == 'SAVE_CONFIG' for x in commands))

    def test_homed_macro_does_not_rehome(self):
        self.assertNotIn('G28', self.render('xyz'))

    def test_fresh_install_keeps_default_active(self):
        self.run_guard()
        self.assertEqual(self.active.read_bytes(), CFG.read_bytes())

    def test_legacy_phase_file_is_preserved_and_new_default_is_inactive(self):
        legacy = self.active.with_name('phase.cfg')
        original = '[phase_stepping stepper_x]\nauto_enable: True\n'
        legacy.write_text(original)
        self.run_guard()
        self.assertEqual(legacy.read_text(), original)
        self.assertFalse(self.active.exists())
        self.assertEqual(self.active.with_name('71_phase.cfg.default').read_bytes(), CFG.read_bytes())

    def test_custom_71_is_never_moved_or_overwritten(self):
        custom = CFG.read_bytes() + b'\n# Owner customization\n'
        self.active.write_bytes(custom)
        self.run_guard()
        self.assertEqual(self.active.read_bytes(), custom)

    def test_saved_comment_block_is_not_an_active_duplicate(self):
        (self.root / 'printer.cfg').write_text('#*# [phase_stepping stepper_x]\n#*# correction: 1:0.1:0.2\n')
        self.run_guard()
        self.assertTrue(self.active.exists())

    def test_active_main_config_section_preserved(self):
        path = self.root / 'printer.cfg'
        original = '[phase_calibrate]\naccel_chip: custom sensor\n'
        path.write_text(original)
        self.run_guard()
        self.assertEqual(path.read_text(), original)
        self.assertFalse(self.active.exists())


if __name__ == '__main__':
    unittest.main()
