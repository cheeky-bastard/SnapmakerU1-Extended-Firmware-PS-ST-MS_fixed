#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Copyright (c) 2026 cheeky-bastard
"""Verify the phase MCU/host/recovery pairing from the packed firmware."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def verify(profile):
    packed = Path('tmp/calibration-verification')
    image = packed / 'rk-unpacked/rootfs.img'
    built = Path('tmp/firmware/rootfs')
    expected_source = '8825a2c8b547913e80aed9bce1e9021f9de38594'
    lock = json.loads(Path('combined-source-lock.json').read_bytes())
    assert lock['justin_klipper_commit'] == expected_source
    assert lock['firmware_line'] == '2.0'
    variant = next(v for v in lock['variants'] if v['profile'] == profile)
    assert 'FIRMWARE_VERSION=2.0.0\n' in Path('vars.mk').read_text()
    records = []

    def read(relative):
        data = subprocess.check_output(['unsquashfs', '-cat', str(image), relative])
        assert data == (built / relative).read_bytes(), 'Packed/build mismatch: ' + relative
        records.append(hashlib.sha256(data).hexdigest() + '  ' + relative)
        return data

    share = 'usr/local/share/phase-stepping/'
    assert read('etc/BUILD_PROFILE').decode().strip() == variant['display_name']
    for name in ('etc/FULLVERSION', 'etc/BUILD_VERSION'):
        version_text = read(name).decode()
        assert variant['display_name'] in version_text
        assert 'cheeky' not in version_text.lower()
    if variant['afc']:
        afc_source = json.loads(read('home/lava/AFC-Klipper-Add-On/build-source.json'))
        assert afc_source['source_commit'] == lock['afc_source_commit']
        assert afc_source['installer_modified_sha256'] == lock['afc_installer_modified_sha256']
        installer = read('home/lava/AFC-Klipper-Add-On/include/U1_extended_firmware_install.sh')
        assert hashlib.sha256(installer).hexdigest() == lock['afc_installer_modified_sha256']
        assert b'/oem/.debug' not in installer
        read('usr/local/sbin/afc-restore-modules')
        read('etc/hooks/klipper.d/12-afc.sh')
        read('usr/local/share/firmware-config/functions/26_enable_afc.yaml')
    if variant['id'] == 'extended-multiace-phase':
        definition = read('usr/local/share/extended-pkg/multiace')
        assert b'PKG_VERSION="1.27b"' in definition
        assert b'aedc432f1ca56854ae3da98e28d6a947a9b4adc2bdb88e7feb760be472968556' in definition
        for name in ('usr/local/sbin/multiace-control', 'usr/local/share/multiace/common.sh',
                     'etc/hooks/klipper.d/10-multiace.sh'):
            read(name)
    if not variant['phase']:
        for name in ('at32f403a.bin', 'at32f415.bin', 'MCU_DESC'):
            data = (packed / name).read_bytes()
            assert data == (Path('tools/tmp/test') / name).read_bytes(), name
            records.append(hashlib.sha256(data).hexdigest() + '  updater/' + name)
        for name in ('klippy/toolhead.py', 'klippy/chelper/__init__.py'):
            data = read('home/lava/klipper/' + name)
            assert b'def register_flush_callback(' not in data
            assert b'defs_phasegen' not in data
        listing = subprocess.check_output(['unsquashfs', '-ll', str(image)]).decode()
        assert '/usr/local/share/phase-stepping/' not in listing
        assert '/klippy/extras/phase_stepping.py' not in listing
        assert '/extended/klipper/71_phase.cfg' not in listing
        assert '/etc/init.d/S49phase-config' not in listing
        Path('firmware/phase-build.json').write_text(json.dumps({
            'profile': profile, 'included': False, 'auto_enabled': False,
            'mcu_payloads': 'stock byte-identical',
        }, indent=2) + '\n')
        Path('firmware/phase-payload-sha256.txt').write_text('\n'.join(records) + '\n')
        print('Non-phase variant: stock AT32 MCU payloads and descriptor preserved; phase host/config absent')
        return
    bundled = read('usr/local/share/firmware-config/extended/klipper/71_phase.cfg')
    assert hashlib.sha256(bundled).hexdigest() == lock['bundled_phase_cfg']['sha256']
    read('etc/init.d/S49phase-config')
    import configparser
    cfg = configparser.RawConfigParser()
    cfg.read_string(bundled.decode())
    for axis in ('x', 'y'):
        assert cfg.getboolean('phase_stepping stepper_' + axis, 'auto_enable') is False
    assert cfg.has_section('gcode_macro PHASE_CALIBRATE_XY')
    stock_config = read('home/lava/origin_printer_data/config/printer.cfg').decode()
    assert '[lis2dw e0_lis2dw]' in stock_config
    cleanup = read('usr/local/share/firmware-config/force-cleanup.sha256').decode()
    assert lock['bundled_phase_cfg']['sha256'] + '  klipper/71_phase.cfg' in cleanup.splitlines()
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
    print('Packed phase metadata, paired updater/recovery MCUs, host payload and disabled bundled 71_phase.cfg verified')


if __name__ == '__main__':
    verify(sys.argv[1])
