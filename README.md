# Snapmaker U1: phase stepping, single-tool calibration and mixed nozzles

**Package: 0.1.0-dev1 | Firmware base: 2.0.0.205 | Updated: 2026-11-19**

Personal experimental firmware maintained by [cheeky-bastard](https://github.com/cheeky-bastard).
This package combines [Justin's phase-stepping work](https://github.com/justinh-rahb/SnapmakerU1-Extended-Firmware/tree/feat/u1-phase-stepping)
with our maintained independent tool calibration and mixed-nozzle print-start fix, on Paxx's 2.0 source line.

## Instructions and downloads

- [Justin's phase-stepping instructions](docs/phase_stepping.md) are preserved unchanged: hardware requirements, enablement, calibration, known issues and rollback.
- [Single-tool calibration work instructions](docs/single_tool_calibration.md) cover the macro buttons, cleaning, validation, manual confirmations and Mainsail grouping.
- [Combined installation and testing](docs/combined_package.md) explains this image, what remains off by default, acceptance and rollback.
- [Experimental builds and checksums](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/releases).
- [Build checks](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/actions/workflows/combined-firmware.yaml).

## Included features

| Feature | Behavior |
| --- | --- |
| Phase stepping | Justin's pinned 20 kHz AT32 mainboard support and matching host/MCU images; **off until explicitly configured** |
| `CALIBRATE_TOOL_1`, `CALIBRATE_TOOL_2`, `CALIBRATE_TOOL_3` | Clean and measure reference plus selected tool; save only the selected tool |
| `CALIBRATE_TOOL_0` | Informational web UI prompt to use stock four-tool calibration |
| `CLEAN_AND_VALIDATE_OFFSETS` | Clean all four tools and compare all six pairs; save nothing |
| `OFFSET_CONTINUE`, `OFFSET_ABORT` | Confirm manual cleaning/plate removal or exit a waiting custom cycle |
| Mixed-nozzle fix | Remove the faulty print-start diameter comparison; retain volume and material checks |

The calibration commands appear as macro buttons in Mainsail/Fluidd. In Mainsail, put the seven main buttons in a **Tool Calibration** macro group with **Standby** visibility. Actual nozzle sizes must remain correct in both printer and slicer.

## Version and maintenance policy

This repository stays on **2.0**. Paxx's current `develop` is on 2.1 and is **not** merged automatically. The latest known Paxx 2.0 source is included, plus Justin's pinned phase branch and our existing 2.0 mods. See [source pins](combined-source-lock.json), [change record](docs/combined_changes.md), and [maintenance instructions](docs/combined_maintenance.md). The separate 2.1 project remains separate until proven stable.

The first combined build requires its own hardware acceptance. Prior results from Justin's phase builds and our calibration builds are evidence for those images only. A successful CI build is not a printer test. Back up and verify configuration, calibration data and relevant native files before installing; never use debug or factory mode.

## Attribution and license

Based on [Paxx Extended Firmware](https://github.com/paxx12-snapmaker-u1/SnapmakerU1-Extended-Firmware), [Justin's firmware fork](https://github.com/justinh-rahb/SnapmakerU1-Extended-Firmware), [Justin's U1 Klipper phase port](https://github.com/justinh-rahb/u1-klipper), Snapmaker U1 Klipper and the Kalico phase-stepping work credited in Justin's guide.
The original [upstream README](README.upstream.md), Justin's documentation, source history, copyright notices and [GPL-3.0 license](LICENSE) are retained. See [modification notice](NOTICE.combined.md) and [calibration notices](overlays/mods/cheeky_b52/NOTICE.md). Independent maintenance does not imply endorsement by upstream authors. No upstream PR is being submitted.
