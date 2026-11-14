# Experimental phase-stepping build

This checkout uses firmware builder baseline `1e702da` and stock image
`U1_2.0.0.205_20260914173503_upgrade.bin`.
Profile: `extended-multiace-phase`.
Klipper source: `justinh-rahb/u1-klipper`, pinned to
`572b8f3bc673a96cf4d45efe674b4560a487906e`; the fork's `main` is not used.

The `phase` mod adds a 10 kHz mainboard backend, matching host patches/modules,
and a rebuilt aarch64 C helper. Existing paxx12 and multiace changes remain.
Toolhead firmware is rebuilt with phase support disabled to share the stock
updater's single MCU version descriptor. Recovery images, versions and hashes
are updated consistently. This is an AT32-mainboard build.

The sample config is stored at `/usr/local/share/phase-stepping/sample.cfg`,
not in an auto-included directory. Phase stepping remains off by default.

## Build environment

Build `.github/dev/Dockerfile` as `snapmaker-u1-dev`, then build
`.github/dev-phase/Dockerfile` as `u1-custom-phase-builder:20261114`.
The latter reuses local image `u1-stock-mcu:10.3-2021.10`, containing the
previously verified official aarch64 GNU Arm compiler (archive SHA256
`f605b5f23ca898e9b8b665be208510a54a6e9fdd0fa5bfc9592002f6e7431208`).
Run the build in the container's native filesystem, not a macOS bind mount,
so squashfs root ownership is preserved. Initialize `deps/screen-apps` first.

Inside the prepared container, with this repository at `/workspace`:

```
cd /workspace
export GIT_VERSION=2.0.0-phase10k-572b8f3
make build PROFILE=extended-multiace-phase \
  OUTPUT_FILE=firmware/U1_2.0.0.205_phase10k_572b8f3_upgrade.bin
```

This only builds an artifact. It does not upload or flash a printer.
The packaged helper must successfully load under the target image's own
Python/CFFI/libc during the build. MCU and host build hashes are recorded at
`/usr/local/share/phase-stepping/build.json`.
