# Experimental U1 phase stepping

Build profile: `extended-multiace-phase`, based on paxx12 `1e702da` and stock
2.0.0.205. The source is pinned to `justinh-rahb/u1-klipper` commit
`fb82097dc158f903774bc80193c2336195b82638`; the fork's main branch is unused.

The mod enables the mainboard's 10 kHz backend, with coil writes sent by DMA on every bus each tick, and installs matching
host modules, a rebuilt aarch64 C helper, recovery copies and metadata. It
preserves the stock host and existing paxx patches. The helper must load in
the target image's Python/libc before packaging succeeds.

The stock updater uses one version descriptor for all MCUs. Accordingly both
AT32 images are built from the pinned source with one USB build ID. Toolhead
control remains stock (phase support disabled). The package and recovery
copies/MD5s are updated together. This image targets AT32 U1 mainboards.

Phase stepping stays OFF until the sample at
`/usr/local/share/phase-stepping/sample.cfg` is deliberately included by the
user. No config is installed into auto-included printer directories.

Build using the local phase Dockerfile, which supplies the exact GNU Arm
10.3-2021.10 compiler. Hardware operation, update timing and coil mapping
still require validation. No flashing command is part of this mod.
