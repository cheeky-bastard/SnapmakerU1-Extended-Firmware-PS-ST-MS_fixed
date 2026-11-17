# Experimental U1 phase stepping

Build profile: `extended-phase` (also combinable, e.g. `extended-multiace-phase`),
based on paxx12 `1e702da` and stock 2.0.0.205. The source is pinned to `justinh-rahb/u1-klipper` commit
`ad066edefcbf3c49ba5c2d45d2bfa0495b28488c`; the fork's main branch is unused.

The mod enables the mainboard's 10 kHz backend, with coil writes sent by DMA
on every bus each tick, and installs matching host modules, a rebuilt aarch64 C helper, recovery copies and metadata. It
preserves the stock host and existing paxx patches. The helper must load in
the target image's Python/libc before packaging succeeds.

The stock updater uses one version descriptor for all MCUs. Accordingly both
AT32 images are built from the pinned source with one USB build ID. Toolhead
control remains stock (phase support disabled). The package and recovery
copies/MD5s are updated together. This image targets AT32 U1 mainboards.

Phase stepping stays OFF until the sample at
`/usr/local/share/phase-stepping/sample.cfg` is deliberately included by the
user. No config is installed into auto-included printer directories.

The MCU images need GNU Arm 10.3-2021.10, the stock U1 compiler. Set
`MCU_CROSS_PREFIX` to use one from the build image; otherwise the build fetches
ARM's aarch64 or x86_64 release into the download cache and checks its SHA-256.
Validated on a U1 (homing, motors off, tool changes, emergency stop, prints).
No flashing command is part of this mod.
