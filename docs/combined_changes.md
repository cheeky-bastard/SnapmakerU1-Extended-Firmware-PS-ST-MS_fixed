# Combined package change record

## 0.1.0-dev3 — 2026-11-19

- Bundle the supplied `71_phase.cfg` in the three phase-capable images, using a separate `phase/96-bundled-config` overlay; the native phase source and original build mod remain unchanged. Keep both `auto_enable` values False and include PHASE_CALIBRATE_XY without an automatic save.
- Add an init guard that preserves existing active phase sections and custom 71_phase.cfg files. Use the stock hash cleanup to refresh/remove only the exact packaged default, including when returning to the non-phase variant.
- Update the credited guide to skip hand-creating the CFG and macro. Retain Justin's motion tests, source pins, behavior and historical results. Document the T0 accelerometer setting, duplicate-section handling and custom/SAVE_CONFIG rollback steps.
- Include the CFG as a release asset, check its actual packed hash in phase builds and its absence in the non-phase build, and test disabled defaults, macro rendering and existing-config preservation. Native calibration/nozzle payloads, phase algorithms, naming and AFC guards remain unchanged.

The [bundled-config four-build CI run](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/actions/runs/44659719706) passed **64 calibration regressions, eight nozzle checks, six packed native/config checks and eight bundled-CFG/default/upgrade checks per variant**, plus original-container round trips and the applicable phase, stock-MCU, AFC and multiACE checks. The three phase builds contain the exact disabled `71_phase.cfg`; the non-phase build excludes it. Public image checksums, CFG asset and per-variant records are verified.

[Download the four-variant release with bundled 71_phase.cfg](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/releases/tag/ST-MS-2.0-four-3-1). It includes **22 assets**, including the standalone CFG and both instruction sets. Build source: `80992cb1ed2ffd4994af778e0be4fa4124ec5564`. Actual printer acceptance remains pending; no printer was changed by this work.

## 0.1.0-dev2 — 2026-11-19

- Mirror Justin's four feature variants: Extended without phase, Extended + phase, multiACE + phase, and AFC + phase. Our calibration/nozzle fixes are present in every variant.
- Use a four-job CI matrix, preserving calibration and exact native/CFG checks per image. Publish only after all four pass; provide four checksum pairs and per-variant verification ZIPs in one release.
- Preserve stock AT32 images/descriptor and omit phase host support in the non-phase image. Retain phase helper/MCU pairing verification for the other three.
- Permit AFC's existing one-line invalid-extruder-name error-to-warning patch only in the AFC variant, as authorized. Check its exact final `extruder.py` hash and full-file delta while retaining all calibration methods unchanged. Original native/mod source guards remain in force before AFC is applied.
- Pin AFCProject source to `5ea84ea6fab75b9b49db090f309154d1e52272bb` rather than following mutable main. Retain all upstream setup/activation defaults and Justin's phase guide unchanged. The multiACE provider remains pinned by Paxx's package definition.
- Update the README feature table, combined instructions and source lock. 2.0 remains separate from 2.1. Hardware acceptance remains pending for each combination.

AFC normal persistence: the pinned upstream installer normally writes a debug flag. This fork replaces only that function with a guarded no-op and uses Paxx's Klipper startup-hook mechanism to restore AFC module links while its saved config include is active. Debug mode remains disabled. The installer adaptation and link restore are checked separately from the native calibration code.

Visible naming: boot artwork, `/etc/BUILD_PROFILE`, version strings and download filenames use feature-based names (`extended-PhaseStep-STC-MS`, with optional multiACE/AFC). Internal legacy overlay paths remain stable for compatibility. Packed-image checks verify all four displayed identities.

All four variants passed the [four-build CI run](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/actions/runs/44652785752): **64 calibration regressions, eight nozzle checks and six packed native/config checks per variant**, original-container round trips, phase host/MCU/recovery checks for the three phase builds, and stock-MCU preservation/phase-absence checks for the non-phase build. The AFC normal-persistence tests and multiACE configuration sanitizer also passed. Public image checksums, source identities and all per-variant verification bundles are verified.

[Download the four-variant experimental release](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/releases/tag/ST-MS-2.0-four-2-1). Build source: `b000441fa09d9bc90eb647a01dbcb44440869cfa`. Each image still requires its own hardware acceptance; no printer was changed by this work.

## 0.1.0-dev1 — 2026-11-19

- Imported Justin's `feat/u1-phase-stepping` at `e64c63669b8f6802871147561f4a1d9d7c94ab10`, rather than the old 1.5.2 `develop` initially copied by GitHub. His six phase-specific files, including `docs/phase_stepping.md`, are retained unchanged.
- Merged our maintained 2.0 calibration build at `3953fdb6748fa80b278f42ff1456de18abe379c4`, including the six later Paxx 2.0 commits missing from Justin's source base. Stock firmware remains 2.0.0.205.
- Retained all eleven files of `overlays/mods/cheeky_b52/` unchanged: native persistence patch and guards, macro CFG and verification, mixed-nozzle patch/guards/eight validation checks, README and notices.
- Composed `PROFILE=extended-cheeky_b52-phase`: the native/nozzle overlays run before the phase overlay. Phase host changes affect `toolhead.py` and C-helper declarations; calibration/nozzle changes affect different Python files. No native algorithms, source hashes, defaults or phase source pins were loosened.
- Added this fork's README, source lock, combined installation/test/rollback instructions, calibration work instructions reused from the maintained project, maintenance policy and modification notice. Preserved upstream and Justin attribution and license.
- Added a dedicated owner-scoped combined build/release workflow. Restricted upstream rolling-release and Cloudflare workflows to their upstream repository so the personal fork does not publish unrelated builds or attempt upstream deployment.

The [first combined CI run](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/actions/runs/44648222176) passed all 64 calibration regressions, eight nozzle checks, six packed native/config checks, original-container round trips, target-image phase helper loading and packed phase MCU/host/recovery verification. Its [experimental release](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware-PS-ST-MS_fixed/releases/tag/phase-ST-MS-2.0-test-1-1) contains 13 assets, including both instruction sets and source/payload records.

Build source: `c9674669031cd2392bbaeccdcac6d9d1d153d42c`. Image SHA-256: `0ed19c8f00ea369e57fbe6d9be85f107b1f1df243e2c7d580a6071a44ecb0fd2`.

Automated build results belong to that exact source commit and its attached records. Justin's earlier phase tests and our earlier calibration tests are retained as historical evidence; combined-image hardware acceptance is pending. No printer was changed during this integration.
