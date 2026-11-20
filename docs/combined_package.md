# Combined 2.0 package: installation and acceptance

**Package: 0.1.0-dev1 | Updated: 2026-11-19**

Read [Justin's complete instructions](phase_stepping.md) and [calibration work instructions](single_tool_calibration.md). Justin's guide is unchanged; its filenames describe his original builds. The combined image here is named `U1_phase_ST_MS_2.0.bin`, built with `PROFILE=extended-cheeky_b52-phase`.

## Before installing

This image is for the **AT32 U1 mainboard** described in Justin's guide. Confirm that requirement before flashing. Phase stepping rebuilds the mainboard and toolhead MCU images with a matching USB version and recovery hashes; flashing this combined image updates those MCUs too. This differs from the calibration-only image. No phase configuration is installed into auto-included directories, and this package adds no automatic phase enablement or driver tuning. Existing phase configuration from an earlier installation can still enable phase stepping; inspect it before flashing.

With the printer idle and no paused or active virtual-SD job, obtain and verify a timestamped local backup of configuration, saved calibration, existing phase settings and relevant native files outside the config root. Preserve originals. Have the previously working 2.0 firmware image available. Use normal operation without debug/factory mode. See the [calibration backup procedure](https://github.com/cheeky-bastard/Snapmaker-U1-Single-Tool-Calibration/blob/a8efd8f02ccc2911a2eb7ca5d3b09b59837d28a8/docs/installation.md#back-up-the-target).

## Install and test in stages

1. Download the combined `.bin` and its `.sha256` record from the same release; verify SHA-256 locally. Flash through the normal local-update process in Justin's guide.
2. Verify startup, firmware identity, MCU connection and retained tool offsets. Keep phase stepping disabled for the first baseline checks. Compare any persisted custom macro CFG with the packaged CFG 0.1.1; customized files can survive upgrades and receive a `.default` copy.
3. Test the T0 warning and waiting-cycle abort. Run a selected T1/T2/T3 calibration with an unchanged reference. Confirm the selected save, unchanged other tools and persistence after a normal restart. Clean/validate must leave saved calibration unchanged. Follow the work instructions for every manual confirmation.
4. Follow Justin's AT32 checks, manual low-speed phase tests and enable/disable procedure. His guide documents both explicit slicer enablement and optional `auto_enable`; neither is added by this package.
5. With phase stepping enabled, verify calibration/probing and return-to-phase behavior, all four tool changes, a representative print and mixed-nozzle print-start behavior. Review phase lost ticks/link counters and saved-offset invariants. Use accurate nozzle sizes and suitable materials/temperatures. Individual upstream test results do not prove this combination.

The combined image requires printer acceptance even after all automated checks pass. Never treat an abort as an undo of a completed save or as a guaranteed immediate interrupt of queued probing.

## Rollback

Before flashing a firmware without phase support, remove or disable the phase-only configuration exactly as Justin's guide explains; otherwise Klipper may fail at startup. Flash the known-good 2.0 image through the normal updater to restore its MCU payloads. Restore only necessary backed-up files after reviewing their diff. Calibration-only CFGs require their native support; remove unsupported custom macros when reverting to a firmware without it. Do not use a whole saved calibration table from another machine.

## Build locally

Use the Linux/Docker setup in the upstream development guide:

```sh
./dev.sh make tools
./dev.sh make firmware
./dev.sh make test
./dev.sh make build PROFILE=extended-cheeky_b52-phase OUTPUT_FILE=firmware/U1_phase_ST_MS_2.0.bin
```

The dedicated GitHub workflow additionally runs the calibration regressions, eight actual nozzle checks during overlay application, six packed native/config checks and phase MCU/host/recovery integrity checks before publishing an experimental prerelease. It does not connect to a printer.
