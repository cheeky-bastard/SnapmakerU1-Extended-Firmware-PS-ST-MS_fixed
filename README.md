# Snapmaker U1: phase stepping, single-tool calibration and mixed nozzles

**Package: 0.1.0-dev3 | Firmware base: 2.0.0.205 | Updated: 2026-11-19**

Personal experimental firmware maintained by [cheeky-bastard](https://github.com/cheeky-bastard).
This package combines [Justin's phase-stepping work](https://github.com/justinh-rahb/SnapmakerU1-Extended-Firmware/tree/feat/u1-phase-stepping)
with our maintained independent tool calibration and mixed-nozzle print-start fix, on Paxx's 2.0 source line.

## Instructions and downloads

- [Justin's phase-stepping instructions](docs/phase_stepping.md) are retained with the bundled-config setup steps updated: hardware requirements, enablement, calibration, known issues and rollback.
- [Single-tool calibration work instructions](docs/single_tool_calibration.md) cover the macro buttons, cleaning, validation, manual confirmations and Mainsail grouping.
- [Combined installation and testing](docs/combined_package.md) explains this image, what remains off by default, acceptance and rollback.
- [Experimental builds and checksums](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/releases).
- [Build checks](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/actions/workflows/combined-firmware.yaml).

## Choose a build

Every variant includes **single-tool calibration and the mixed-nozzle fix**. The feature split mirrors Justin's four builds:

| File | Contents |
| --- | --- |
| `U1_extended-STC-MS_2.0_upgrade.bin` | Extended + our fixes; **no phase stepping** |
| `U1_extended-PhaseStep-STC-MS_2.0_upgrade.bin` | Extended + our fixes + phase stepping |
| `U1_extended-multiACE-PhaseStep-STC-MS_2.0_upgrade.bin` | Extended + our fixes + multiACE + phase stepping |
| `U1_extended-AFC-PhaseStep-STC-MS_2.0_upgrade.bin` | Extended + our fixes + AFC + phase stepping |

Phase variants require an **AT32 mainboard** and remain off until configured. The first variant retains stock MCU binaries. Remove existing phase-only configuration before switching to the non-phase image. multiACE and AFC retain their [upstream setup instructions](docs/combined_package.md#optional-filament-systems); selecting a variant does not configure external hardware automatically.

Each release includes four image/checksum pairs, a shared `SHA256SUMS`, `release-index.json`, both instruction sets and one verification ZIP per variant. All four must pass CI before publication. [Four-variant downloads](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/releases/tag/ST-MS-2.0-four-2-1).

Boot-screen and Firmware Config profile labels use the same descriptive feature names: `STC` means single-tool calibration and `MS` means the mixed-size nozzle fix. The build/version labels contain no username.

## Bundled phase configuration

The three phase-capable images include `extended/klipper/71_phase.cfg` and the **PHASE_CALIBRATE_XY** macro button. Do not hand-create `phase.cfg` or duplicate its sections. Both `auto_enable` settings remain `False`; continue with [Justin's motion checks and manual enablement](docs/phase_stepping.md#enable-phase-stepping). The non-phase image excludes this CFG. See [upgrade and existing-config behavior](docs/combined_package.md#bundled-phase-config-and-upgrades).

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

## Verified four-variant release

All four variants passed the [four-build CI run](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/actions/runs/44652785752): **64 calibration regressions, eight nozzle checks and six packed native/config checks per variant**, original-container round trips, phase host/MCU/recovery checks for the three phase builds, and stock-MCU preservation/phase-absence checks for the non-phase build. The AFC normal-persistence tests and multiACE configuration sanitizer also passed. Public image checksums, source identities and all per-variant verification bundles are verified.

[Download the four-variant experimental release](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/releases/tag/ST-MS-2.0-four-2-1). Build source: `b000441fa09d9bc90eb647a01dbcb44440869cfa`. Each image still requires its own hardware acceptance; no printer was changed by this work.

## Earlier single-variant build

The [first combined build](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/actions/runs/44648222176) passed **64 calibration regressions, eight nozzle checks, six packed native/config checks, original-container round trips, target-image phase helper loading and phase MCU/host/recovery pairing checks**.

[Download the experimental 2.0 package](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/releases/tag/phase-ST-MS-2.0-test-1-1), built from `c9674669031cd2392bbaeccdcac6d9d1d153d42c`. The release includes the image, checksum, both instruction sets, source pins and payload records. Combined-image **hardware acceptance remains pending**; AT32 mainboard only, with phase stepping off until explicitly configured.

## Version and maintenance policy

This repository stays on **2.0**. Paxx's current `develop` is on 2.1 and is **not** merged automatically. The latest known Paxx 2.0 source is included, plus Justin's pinned phase branch and our existing 2.0 mods. See [source pins](combined-source-lock.json), [change record](docs/combined_changes.md), and [maintenance instructions](docs/combined_maintenance.md). The separate 2.1 project remains separate until proven stable.

Every variant requires its own hardware acceptance. Prior results from Justin's phase builds and our calibration builds are evidence for those images only. A successful CI build is not a printer test. Back up and verify configuration, calibration data and relevant native files before installing; never use debug or factory mode.

## Attribution and license

Based on [Paxx Extended Firmware](https://github.com/paxx12-snapmaker-u1/SnapmakerU1-Extended-Firmware), [Justin's firmware fork](https://github.com/justinh-rahb/SnapmakerU1-Extended-Firmware), [Justin's U1 Klipper phase port](https://github.com/justinh-rahb/u1-klipper), Snapmaker U1 Klipper and the Kalico phase-stepping work credited in Justin's guide.
The original [upstream README](README.upstream.md), Justin's credited documentation, source history, copyright notices and [GPL-3.0 license](LICENSE) are retained. See [modification notice](NOTICE.combined.md) and [calibration notices](overlays/mods/cheeky_b52/NOTICE.md). Independent maintenance does not imply endorsement by upstream authors. No upstream PR is being submitted.

AFC normal persistence: the pinned upstream installer normally writes a debug flag. This fork replaces only that function with a guarded no-op and uses Paxx's Klipper startup-hook mechanism to restore AFC module links while its saved config include is active. Debug mode remains disabled. The installer adaptation and link restore are checked separately from the native calibration code.
