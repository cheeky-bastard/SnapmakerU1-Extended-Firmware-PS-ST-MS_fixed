# Snapmaker U1 calibration firmware — 2.0

**Maintainer: cheeky-bastard | Restored: 2026-11-14**

Personal Paxx-based firmware with independent T1/T2/T3 calibration and a guarded mixed-nozzle print-start workaround. T0 directs the operator to stock full calibration; clean/validate saves nothing.

Read the [usermod instructions](overlays/mods/cheeky_b52/README.md), [full calibration documentation](https://github.com/cheeky-bastard/Snapmaker-U1-Single-Tool-Calibration), and [Releases](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware/releases).

These are web UI macro buttons. In Mainsail, put the seven primary buttons in a **Tool Calibration** macro group and enable Standby visibility.

Pinned upstream: `2c80e3dc495fdf724bc53c5c35c875010ee1668f`. Reviewed native/CFG payload hashes are unchanged. **Verified build available:** [Download the restored 2.0 image](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware/releases/tag/calibration-2.0-restored-1-1). The [new CI run](https://github.com/cheeky-bastard/SnapmakerU1-Extended-Firmware/actions/runs/43561241022) passed 64 calibration regressions, eight nozzle checks, six packed-payload hashes, container round trips, and header/extra-MCU preservation. Public checksums and source identity are verified. On-printer acceptance of the new image is pending. Obtain verified configuration/native backups before persistent printer changes. Use normal operation without debug or factory mode.

## Attribution

Built from [Paxx's Extended Firmware](https://github.com/paxx12-snapmaker-u1/SnapmakerU1-Extended-Firmware). Upstream source history and notices are preserved. See [upstream README](README.upstream.md), [GPL-3.0](LICENSE), and [modification notice](overlays/mods/cheeky_b52/NOTICE.md).

Restored under `cheeky-bastard` on 2026-11-14. Historical source banners, copyright notices and exact native/CFG payload hashes are retained. Old account URLs in source comments and historical records identify provenance; current project links use the new account. The stable `cheeky_b52` mod namespace is retained for compatibility. No upstream PR is authorized.

## Stable-main sync — 2026-11-18

Paxx stable main `0de1a77da137d8a7af3ed1af36ae7c6fb70c3a5a` is now merged into the repository history. Its tree matches the already-included common ancestor exactly, so this introduces no firmware source or payload changes. The 2.0 line stays on stock 2.0.0.205 and its existing reviewed source set; the current release and verification remain applicable. New 2.1 develop work is maintained in the separate 2.1 repository.
