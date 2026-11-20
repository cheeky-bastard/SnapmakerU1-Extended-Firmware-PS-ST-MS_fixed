#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Copyright (c) 2026 cheeky-bastard
"""Combine four verified CI artifacts into one unambiguous testing release."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile


def assemble(source, target):
    lock = json.loads(Path('combined-source-lock.json').read_bytes())
    assert len(lock['variants']) == 4
    assert not target.exists()
    target.mkdir(parents=True)
    common = ('PHASE_STEPPING.md', 'WORK_INSTRUCTIONS.md', 'TESTING.md',
              'NOTICE.md', 'LICENSE', '70_tool_offsets.cfg', 'combined-source-lock.json')
    shared = {}
    index, checksums = [], []
    infos = list(source.glob('*/build-info.txt'))
    assert len(infos) == 4
    used = set()
    for variant in lock['variants']:
        matches = []
        for path in infos:
            info = dict(line.split('=', 1) for line in path.read_text().splitlines())
            if info['profile'] == variant['profile']:
                matches.append((path.parent, info))
        assert len(matches) == 1, variant['id']
        folder, info = matches[0]
        used.add(folder)
        assert info['source_commit'] == __import__('os').environ['GITHUB_SHA']
        assert json.loads((folder / 'combined-source-lock.json').read_bytes()) == lock
        for name in common:
            data = (folder / name).read_bytes()
            if name in shared:
                assert shared[name] == data, name
            else:
                shared[name] = data
                (target / name).write_bytes(data)
        image = folder / variant['image']
        checksum = image.with_name(image.name + '.sha256')
        digest, filename = checksum.read_text().split()
        assert filename == image.name
        assert hashlib.sha256(image.read_bytes()).hexdigest() == digest
        phase = json.loads((folder / 'phase-build.json').read_bytes())
        assert phase['auto_enabled'] is False
        if variant['phase']:
            assert phase['source_commit'] == lock['justin_klipper_commit']
            assert int(phase['phase_tick_hz']) == 20000
        else:
            assert phase['included'] is False
        shutil.copyfile(image, target / image.name)
        shutil.copyfile(checksum, target / checksum.name)
        checksums.append(digest + '  ' + image.name)
        bundle = variant['id'] + '-verification.zip'
        records = ('build-info.txt', 'payload-sha256.txt', 'phase-build.json', 'phase-payload-sha256.txt')
        with zipfile.ZipFile(target / bundle, 'w', zipfile.ZIP_DEFLATED) as archive:
            for name in records:
                archive.write(folder / name, name)
        index.append(dict(variant, version=info['version'], source_commit=info['source_commit'],
                          sha256=digest, bytes=image.stat().st_size, verification=bundle))
    assert len(used) == 4
    (target / 'SHA256SUMS').write_text('\n'.join(checksums) + '\n')
    (target / 'release-index.json').write_text(json.dumps({'variants': index}, indent=2) + '\n')
    assert len(list(target.iterdir())) == 21
    print('Four variants verified and assembled: 4 images, 4 checksums, 4 verification bundles and shared instructions/records')


if __name__ == '__main__':
    assemble(Path(sys.argv[1]), Path(sys.argv[2]))
