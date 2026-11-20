#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileCopyrightText: Copyright (c) 2026 cheeky-bastard
"""Replace only the pinned AFC installer's debug-persistence function."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASELINE = '39c4c793b8ee3e9a6eafcd78e83ce246c64265c3dbb8993ed4b1fa4c54f19d6d'
MODIFIED = 'c6f8a27832638d12cce676da75649975f1523b95bbaee9230193a79888d96d21'
OLD = '# For Snapmaker U1 printers need to add /oem/.debug or changes in klipper folder will\n# be reset on reboot/power cycle\nu1_write_debug_file() {\n    # Use su if passed in\n    if [ $EUID -ne 0 ]; then\n        echo "Writing .debug file to /oem/ directory"\n        su root -c "touch /oem/.debug"\n    elif [ ! -f "/oem/.debug" ]; then\n        echo Adding /oem/.debug file\n        touch /oem/.debug\n    fi\n}\n'
NEW = '# Modified by cheeky-bastard, 2026-11-19: normal Paxx startup hooks\n# restore ephemeral AFC links. Retain this legacy function name for callers.\nu1_write_debug_file() {\n    echo "AFC module persistence is provided by the normal Paxx startup hook."\n}\n'


def adapt(root):
    protected = {'extruder_config_bak.py', 'probe_inductance_coil.py',
                 'print_task_config.py', 'queuefile.py'}
    assert not protected.intersection(p.name for p in (root / 'extras').glob('*.py'))
    path = root / 'include/U1_extended_firmware_install.sh'
    data = path.read_bytes()
    assert hashlib.sha256(data).hexdigest() == BASELINE
    source = data.decode()
    assert source.count(OLD) == 1
    output = source.replace(OLD, NEW)
    assert '/oem/.debug' not in output
    assert hashlib.sha256(output.encode()).hexdigest() == MODIFIED
    path.write_bytes(output.encode())
    subprocess.run(['bash', '-n', str(path)], check=True)
    metadata = json.loads((root / 'build-source.json').read_bytes())
    metadata.update(installer_baseline_sha256=BASELINE,
                    installer_modified_sha256=MODIFIED,
                    persistence='normal Paxx Klipper startup hook; no debug flag')
    (root / 'build-source.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print('Pinned AFC installer adapted to normal startup persistence; exact hashes and shell syntax verified')


if __name__ == '__main__':
    adapt(Path(sys.argv[1]))
