#!/usr/bin/env bash

GIT_URL=https://github.com/AFCProject/AFC-Klipper-Add-On.git
GIT_REF=5ea84ea6fab75b9b49db090f309154d1e52272bb

if [[ -z "$CREATE_FIRMWARE" ]]; then
  echo "Error: This script should be run within the create_firmware.sh environment."
  exit 1
fi

set -eo pipefail

TARGET_DIR="$CACHE_DIR/AFC-Klipper-Add-On"
LAVA_UID=1000
LAVA_GID=1000
DEST_DIR="$ROOTFS_DIR/home/lava/AFC-Klipper-Add-On"

cache_git.sh "$TARGET_DIR" "$GIT_URL" "$GIT_REF"
# Pinned for reproducible combined builds; never follow main implicitly.
git -C "$TARGET_DIR" checkout -f "$GIT_REF"
test "$(git -C "$TARGET_DIR" rev-parse HEAD)" = "$GIT_REF"

echo ">> Installing AFC-Klipper-Add-On..."
rm -rf "$DEST_DIR"
cp -a "$TARGET_DIR" "$DEST_DIR"
rm -rf "$DEST_DIR/.git"
printf '{"source_commit":"%s"}\n' "$GIT_REF" > "$DEST_DIR/build-source.json"
python3 -B "$ROOT_DIR/tools/adapt_afc_no_debug.py" "$DEST_DIR"
chown -R "$LAVA_UID:$LAVA_GID" "$DEST_DIR"

echo ">> AFC-Klipper-Add-On installation completed successfully."
