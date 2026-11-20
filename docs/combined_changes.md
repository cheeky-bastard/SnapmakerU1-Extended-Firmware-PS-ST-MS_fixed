# Combined package change record

## 0.1.0-dev1 — 2026-11-19

- Imported Justin's `feat/u1-phase-stepping` at `e64c63669b8f6802871147561f4a1d9d7c94ab10`, rather than the old 1.5.2 `develop` initially copied by GitHub. His six phase-specific files, including `docs/phase_stepping.md`, are retained unchanged.
- Merged our maintained 2.0 calibration build at `3953fdb6748fa80b278f42ff1456de18abe379c4`, including the six later Paxx 2.0 commits missing from Justin's source base. Stock firmware remains 2.0.0.205.
- Retained all eleven files of `overlays/mods/cheeky_b52/` unchanged: native persistence patch and guards, macro CFG and verification, mixed-nozzle patch/guards/eight validation checks, README and notices.
- Composed `PROFILE=extended-cheeky_b52-phase`: the native/nozzle overlays run before the phase overlay. Phase host changes affect `toolhead.py` and C-helper declarations; calibration/nozzle changes affect different Python files. No native algorithms, source hashes, defaults or phase source pins were loosened.
- Added this fork's README, source lock, combined installation/test/rollback instructions, calibration work instructions reused from the maintained project, maintenance policy and modification notice. Preserved upstream and Justin attribution and license.
- Added a dedicated owner-scoped combined build/release workflow. Restricted upstream rolling-release and Cloudflare workflows to their upstream repository so the personal fork does not publish unrelated builds or attempt upstream deployment.

Automated build results belong to the exact source commit and its attached records. Justin's earlier phase tests and our earlier calibration tests are retained as historical evidence; combined-image hardware acceptance is pending.
