# Combined 2.0 package: installation and acceptance

**Package: 0.1.0-dev3 | Updated: 2026-11-19**

Read [Justin's complete instructions](phase_stepping.md) and [calibration work instructions](single_tool_calibration.md). Justin's guide retains his testing instructions; its manual CFG creation steps now use our bundled default. His original four-way feature split is now also offered here, with our calibration and mixed-nozzle fixes in **every** image. See the [download table](../README.md#choose-a-build).

| Variant | Build profile (internal) |
| --- | --- |
| `extended` | `extended-cheeky_b52` |
| `extended-phase` | `extended-cheeky_b52-phase` |
| `extended-multiace-phase` | `extended-cheeky_b52-multiace-phase` |
| `extended-afc-phase` | `extended-cheeky_b52-afc-phase` |

## Before installing

The three phase variants are for the **AT32 U1 mainboard** described in Justin's guide. Confirm that requirement before flashing. Phase stepping rebuilds the mainboard and toolhead MCU images with a matching USB version and recovery hashes; flashing this combined image updates those MCUs too. The non-phase Extended variant instead keeps the stock MCU binaries and omits the phase host modules. The phase variants install `71_phase.cfg` through the same default-copy mechanism as `70_tool_offsets.cfg`. Both `auto_enable` values remain `False`: commands and the calibration button are registered, without automatic phase motion or driver tuning. Existing phase configuration from an earlier installation can still enable phase stepping; inspect it before flashing.

With the printer idle and no paused or active virtual-SD job, obtain and verify a timestamped local backup of configuration, saved calibration, existing phase settings and relevant native files outside the config root. Preserve originals. Have the previously working 2.0 firmware image available. Use normal operation without debug/factory mode. See the [calibration backup procedure](https://github.com/cheeky-bastard/Snapmaker-U1-Single-Tool-Calibration/blob/a8efd8f02ccc2911a2eb7ca5d3b09b59837d28a8/docs/installation.md#back-up-the-target).

## Bundled phase config and upgrades

Fresh phase installations receive `extended/klipper/71_phase.cfg` automatically alongside `70_tool_offsets.cfg`. This registers the X/Y phase commands and **PHASE_CALIBRATE_XY** button; phase stepping remains off because both `auto_enable` values are `False`. No macro runs or calibration corrections are saved during boot. Add the phase-calibration button to a Mainsail macro group if desired.

Keep T0's accelerometer configuration accurate. The supplied calibration section names `lis2dw e0_lis2dw`; verify that this is the correct physical sensor before using phase calibration. A different sensor requires adapting that setting, not changing tool offsets.

Paxx preserves a customized `71_phase.cfg` and offers the packaged version as `.default`. If another auto-included `extended/klipper/*.cfg` file or `printer.cfg` already defines overlapping phase sections, a newly copied unmodified default is moved to `71_phase.cfg.default`; existing settings remain in use. Review and consolidate those files once, with verified backups. This guard does not follow arbitrary custom include chains outside those locations, so inspect custom includes too. Do not duplicate `[phase_stepping]`, `[phase_calibrate]` or the calibration macro.

Unmodified packaged defaults are refreshed through the stock checksum-cleanup mechanism. That also removes this exact unmodified CFG when switching to the non-phase image. Customized phase files, other filenames and phase sections/corrections in `SAVE_CONFIG` are preserved: remove or disable those explicitly before flashing a firmware without phase support. No custom phase settings or saved corrections are silently erased.

The standalone `71_phase.cfg` release asset is for phase-capable images only; it cannot add phase MCU/host support to the non-phase image.

## Install and test in stages

1. Choose the correct variant and download its `.bin` and its `.sha256` record from the same release; verify SHA-256 locally. Flash through the normal local-update process in Justin's guide.
2. Verify startup, firmware identity, MCU connection and retained tool offsets. Keep phase stepping disabled for the first baseline checks. Compare any persisted custom macro CFG with the packaged CFG 0.1.1; customized files can survive upgrades and receive a `.default` copy.
3. Test the T0 warning and waiting-cycle abort. Run a selected T1/T2/T3 calibration with an unchanged reference. Confirm the selected save, unchanged other tools and persistence after a normal restart. Clean/validate must leave saved calibration unchanged. Follow the work instructions for every manual confirmation.
4. For a phase variant, follow Justin's AT32 checks, manual low-speed phase tests and enable/disable procedure. Skip hand-creating the CFG: it is bundled. His explicit slicer enablement and optional `auto_enable: True` remain choices after the motion tests; neither is enabled by this package.
5. With phase stepping enabled, verify calibration/probing and return-to-phase behavior, all four tool changes, a representative print and mixed-nozzle print-start behavior. Review phase lost ticks/link counters and saved-offset invariants. Use accurate nozzle sizes and suitable materials/temperatures. Individual upstream test results do not prove this combination.

The combined image requires printer acceptance even after all automated checks pass. Never treat an abort as an undo of a completed save or as a guaranteed immediate interrupt of queued probing.

## Optional filament systems

- **multiACE + phase:** use the [Paxx multiACE instructions](multiace.md). The pinned provider is downloaded only when selected in Firmware Config; it is not silently enabled by this image. Existing multiACE settings can persist across updates.
- **AFC + phase:** use the included [AFCProject setup guide](https://afcproject.dev/initial-startup/01-overview.html#snapmaker-u1) and the Firmware Config AFC enable action. This image bundles the pinned AFC source but does not automatically enable or configure the add-on. Enable AFC through this image's Firmware Config action. For normal reboot persistence, this fork replaces the pinned installer's debug-flag function with a source-guarded informational no-op and restores AFC module links through Paxx's existing Klipper startup hooks when the AFC config include is active. No debug flag is written. The hook refuses collisions with protected calibration/nozzle modules. The existing AFC native patch changes only `ExtruderStepper._get_extruder_index` for an invalid extruder name from an exception to a warning; independent-calibration code remains identical. The final AFC native hash is checked separately.

First establish the four physical tools and their offsets before testing any virtual-tool/filament mappings. Our calibration macros address physical T0–T3. External feeders, virtual mappings and phase/calibration interaction require hardware acceptance for the chosen configuration.

## Rollback

Before flashing a firmware without phase support, remove or disable the phase-only configuration exactly as Justin's guide explains; otherwise Klipper may fail at startup. Flash the known-good 2.0 image through the normal updater to restore its MCU payloads. Restore only necessary backed-up files after reviewing their diff. Calibration-only CFGs require their native support; remove unsupported custom macros when reverting to a firmware without it. Do not use a whole saved calibration table from another machine.

## Build locally

Use the Linux/Docker setup in the upstream development guide:

```sh
./dev.sh make tools
./dev.sh make firmware
./dev.sh make test
./dev.sh make build PROFILE=extended-cheeky_b52-phase PROFILE_LABEL=extended-PhaseStep-STC-MS OUTPUT_FILE=firmware/U1_extended-PhaseStep-STC-MS_2.0_upgrade.bin
```

The dedicated GitHub workflow additionally runs the calibration regressions, eight actual nozzle checks during overlay application, six packed native/config checks and phase MCU/host/recovery integrity checks before publishing an experimental prerelease. It does not connect to a printer.

The CI matrix tests every variant independently and publishes only when all four pass. Per-variant verification ZIPs contain build identity, native/config hashes and phase or stock-MCU verification records. The first single-variant release remains historical evidence for its exact image.

## Verified release

All four variants passed the [four-build CI run](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/actions/runs/44652785752): **64 calibration regressions, eight nozzle checks and six packed native/config checks per variant**, original-container round trips, phase host/MCU/recovery checks for the three phase builds, and stock-MCU preservation/phase-absence checks for the non-phase build. The AFC normal-persistence tests and multiACE configuration sanitizer also passed. Public image checksums, source identities and all per-variant verification bundles are verified.

[Download the four-variant experimental release](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/releases/tag/ST-MS-2.0-four-2-1). Build source: `b000441fa09d9bc90eb647a01dbcb44440869cfa`. Each image still requires its own hardware acceptance; no printer was changed by this work.

