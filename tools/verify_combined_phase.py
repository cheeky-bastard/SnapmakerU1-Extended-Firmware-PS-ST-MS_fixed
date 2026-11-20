#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Copyright (c) 2026 cheeky-bastard
"""Verify the phase MCU/host/recovery pairing from the packed firmware."""
import hashlib
import json
from pathlib import Path
import subprocess


def verify():
    packed = Path('tmp/calibration-verification')
    image = packed / 'rk-unpacked/rootfs.img'
    built = Path('tmp/firmware/rootfs')
    expected_source = '8825a2c8b547913e80aed9bce1e9021f9de38594'
    lock = json.loads(Path('combined-source-lock.json').read_bytes())
    assert lock['justin_klipper_commit'] == expected_source
    assert lock['firmware_line'] == '2.0'
    assert lock['profile'] == 'extended-cheeky_b52-phase'
    assert 'FIRMWARE_VERSION=2.0.0\n' in Path('vars.mk').read_text()
    records = []

    def read(relative):
        data = subprocess.check_output(['unsquashfs', '-cat', str(image), relative])
        assert data == (built / relative).read_bytes(), 'Packed/build mismatch: ' + relative
        records.append(hashlib.sha256(data).hexdigest() + '  ' + relative)
        return data

    share = 'usr/local/share/phase-stepping/'
    metadata_bytes = read(share + 'build.json')
    metadata = json.loads(metadata_bytes)
    assert metadata['source_commit'] == expected_source
    assert metadata['auto_enabled'] is False
    assert int(metadata['phase_tick_hz']) == 20000
    version = metadata['mcu_usb_version']
    assert version.endswith('-' + expected_source[:10])
    assert (packed / 'MCU_DESC').read_text().strip() == version
    recovery = 'home/lava/firmware_MCU/'
    assert read(recovery + 'VERSION').decode().strip() == version
    for target in ('at32f403a', 'at32f415'):
        updater = (packed / (target + '.bin')).read_bytes()
        assert hashlib.sha256(updater).hexdigest() == metadata['sha256'][target]
        assert updater == read(recovery + target + '.bin')
        assert updater != (Path('tools/tmp/test') / (target + '.bin')).read_bytes()
        records.append(hashlib.sha256(updater).hexdigest() + '  updater/' + target + '.bin')
    for line in read(recovery + 'md5sum.txt').decode().splitlines():
        digest, filename = line.split(None, 1)
        filename = filename.lstrip('*')
        assert '/' not in filename and filename != '..'
        assert hashlib.md5(read(recovery + filename)).hexdigest() == digest
    helper = read('home/lava/klipper/klippy/chelper/c_helper.so')
    assert hashlib.sha256(helper).hexdigest() == metadata['sha256']['c_helper.so']
    main = json.loads(read(share + 'mainboard.dict'))
    assert int(main['config']['PHASE_STEPPER_TICK_FREQ']) == 20000
    read(share + 'toolhead.dict')
    read(share + 'sample.cfg')
    read(share + 'README.md')
    host = 'home/lava/klipper/klippy/'
    assert b'def register_flush_callback(' in read(host + 'toolhead.py')
    assert b'defs_phasegen' in read(host + 'chelper/__init__.py')
    for module in ('phase_stepping', 'phase_calibrate', 'phase_limits',
                   'motor_kinematics', 'motor_harmonics'):
        name = host + 'extras/' + module + '.py'
        compile(read(name), name, 'exec')
    read('home/lava/klipper/scripts/graph_motor_harmonics.py')
    Path('firmware/phase-build.json').write_bytes(metadata_bytes)
    Path('firmware/phase-payload-sha256.txt').write_text('\n'.join(sorted(set(records))) + '\n')
    print('Packed phase metadata, 20 kHz source pin, paired updater/recovery MCUs, recovery hashes and host payload verified')


if __name__ == '__main__':
    verify()
