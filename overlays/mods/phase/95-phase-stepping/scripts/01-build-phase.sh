#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
: "${CREATE_FIRMWARE:?Run through create_firmware.sh}"
: "${MCU_CROSS_PREFIX:?Use the phase build Docker image with GNU Arm 10.3-2021.10}"
SOURCE_URL=https://github.com/justinh-rahb/u1-klipper.git
SOURCE_SHA=572b8f3bc673a96cf4d45efe674b4560a487906e
SOURCE_DIR="$CACHE_DIR/u1-phase-$SOURCE_SHA"
HOST_DIR="$ROOTFS_DIR/home/lava/klipper"
SHARE_DIR="$ROOTFS_DIR/usr/local/share/phase-stepping"

mkdir -p "$SOURCE_DIR"
if [[ ! -d "$SOURCE_DIR/.git" ]]; then
  git -C "$SOURCE_DIR" init
  git -C "$SOURCE_DIR" fetch --depth=1 "$SOURCE_URL" "$SOURCE_SHA"
  git -C "$SOURCE_DIR" checkout --detach FETCH_HEAD
fi
[[ "$(git -C "$SOURCE_DIR" rev-parse HEAD)" == "$SOURCE_SHA" ]]
git -C "$SOURCE_DIR" diff --exit-code
"${MCU_CROSS_PREFIX}gcc" --version | grep -F '10.3.1 20210824'
MCU_VERSION=$(python3 - "$SOURCE_DIR" "$SOURCE_SHA" <<'PY'
import datetime,subprocess,sys
stamp=int(subprocess.check_output(['git','-C',sys.argv[1],'show','-s','--format=%ct',sys.argv[2]]))
print(datetime.datetime.fromtimestamp(stamp,datetime.timezone.utc).strftime('%Y%m%d%H%M%S')+'-'+sys.argv[2][:10])
PY
)

# Both MCU images share one descriptor in the stock updater. Toolhead control
# code is unchanged; rebuild it only to give both images the same build ID.
for target in at32f403a at32f415; do
  preset="lava/${target}_config"
  [[ "$target" == at32f403a ]] && preset=lava/at32f403a_phase_config
  cp "$SOURCE_DIR/$preset" "$SOURCE_DIR/.config"
  python3 - "$SOURCE_DIR/.config" "$MCU_VERSION" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);s=p.read_text()
s,n=re.subn(r'^CONFIG_USB_PRODUCT_SUFFIX=.*$', 'CONFIG_USB_PRODUCT_SUFFIX="-'+sys.argv[2]+'"',s,flags=re.M)
assert n==1
p.write_text(s)
PY
  make -C "$SOURCE_DIR" olddefconfig
  make -C "$SOURCE_DIR" -j4 CROSS_PREFIX="$MCU_CROSS_PREFIX" OUT="out_$target/"
  install -m 644 "$SOURCE_DIR/out_$target/klipper.bin" "$BUILD_DIR/$target.bin"
  install -m 644 "$SOURCE_DIR/out_$target/klipper.bin" "$ROOTFS_DIR/home/lava/firmware_MCU/$target.bin"
done
printf '%s\n' "$MCU_VERSION" > "$BUILD_DIR/MCU_DESC"
printf '%s\n' "$MCU_VERSION" > "$ROOTFS_DIR/home/lava/firmware_MCU/VERSION"
# Keep recovery hashes consistent, including any untouched vendor MCU images.
(cd "$ROOTFS_DIR/home/lava/firmware_MCU"; md5sum ./*.bin > md5sum.txt)

# Copy only new modules, preserving the image's existing host and paxx patches.
for module in phase_stepping phase_calibrate phase_limits motor_kinematics motor_harmonics; do
  install -m 644 "$SOURCE_DIR/klippy/extras/$module.py" "$HOST_DIR/klippy/extras/$module.py"
done
install -m 755 "$SOURCE_DIR/scripts/graph_motor_harmonics.py" "$HOST_DIR/scripts/graph_motor_harmonics.py"
make -C "$SOURCE_DIR/klippy/chelper" -j4 CROSS_COMPILE=aarch64-linux-gnu-
install -m 755 "$SOURCE_DIR/klippy/chelper/c_helper.so" "$HOST_DIR/klippy/chelper/c_helper.so"
mkdir -p "$SHARE_DIR"
install -m 644 "$SOURCE_DIR/config/sample-u1-phase-stepping.cfg" "$SHARE_DIR/sample.cfg"
install -m 644 "$SOURCE_DIR/docs/U1_Phase_Stepping.md" "$SHARE_DIR/README.md"
install -m 644 "$SOURCE_DIR/out_at32f403a/klipper.dict" "$SHARE_DIR/mainboard.dict"
install -m 644 "$SOURCE_DIR/out_at32f415/klipper.dict" "$SHARE_DIR/toolhead.dict"
# The sample is deliberately outside auto-included config directories.

# Load the actual helper with the target image's loader, Python and CFFI.
chroot_firmware.sh "$ROOTFS_DIR" /usr/bin/python3 - <<'PY'
import sys
sys.path.insert(0,'/home/lava/klipper/klippy')
import chelper
from extras import phase_stepping,phase_calibrate
ffi,lib=chelper.get_ffi()
for name in dir(lib):
    getattr(lib,name)
p=lib.phasegen_alloc()
assert p!=ffi.NULL
lib.phasegen_free(p)
print('Phase host modules, CFFI exports, helper and target libc verified')
PY
python3 - "$SHARE_DIR/build.json" "$SOURCE_SHA" "$MCU_VERSION" "$BUILD_DIR" "$HOST_DIR" <<'PY'
import hashlib,json,sys
from pathlib import Path
files={n:hashlib.sha256((Path(sys.argv[4])/(n+'.bin')).read_bytes()).hexdigest() for n in ['at32f403a','at32f415']}
files['c_helper.so']=hashlib.sha256((Path(sys.argv[5])/'klippy/chelper/c_helper.so').read_bytes()).hexdigest()
Path(sys.argv[1]).write_text(json.dumps({'source_commit':sys.argv[2],'mcu_usb_version':sys.argv[3],'phase_tick_hz':10000,'auto_enabled':False,'sha256':files},indent=2)+'\n')
PY
chown -R 1000:1000 "$ROOTFS_DIR/home/lava/firmware_MCU" "$HOST_DIR"
echo ">> Phase stepping: both MCU images and matching host installed; feature remains off by default."
