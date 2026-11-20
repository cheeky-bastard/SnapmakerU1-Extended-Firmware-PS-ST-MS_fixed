# Combined package modification notice

**Maintainer: cheeky-bastard | Package: 0.1.0-dev2 | Date: 2026-11-19**

This independently maintained derivative combines Paxx Extended Firmware, Justin's experimental U1 phase-stepping firmware mod and the maintained independent-calibration/mixed-nozzle usermod. Full source history, GPL-3.0 license and existing copyright notices are preserved. Justin's phase-stepping guide is retained unchanged, with our calibration work instructions alongside it.

Upstream projects:

- [Paxx Extended Firmware](https://github.com/paxx12-snapmaker-u1/SnapmakerU1-Extended-Firmware)
- [Justin's phase firmware branch](https://github.com/justinh-rahb/SnapmakerU1-Extended-Firmware/tree/feat/u1-phase-stepping)
- [Justin's U1 Klipper phase port](https://github.com/justinh-rahb/u1-klipper), including the Kalico origin credited in his documentation
- [Independent calibration project](https://github.com/cheeky-bastard/Snapmaker-U1-Single-Tool-Calibration)
- [Snapmaker U1 Klipper](https://github.com/Snapmaker/u1-klipper) and [Klipper](https://github.com/Klipper3d/klipper)

The composition, source lock, instructions, verification and personal build workflow are the changes made by this fork; see [change record](docs/combined_changes.md). Original author notices and the stable `cheeky_b52` namespace are retained for provenance and compatibility. This is not an official release or an endorsement by the upstream authors. No printer configuration, backups, credentials or calibration tables are distributed. No upstream PR is submitted.

AFC normal persistence: the pinned upstream installer normally writes a debug flag. This fork replaces only that function with a guarded no-op and uses Paxx's Klipper startup-hook mechanism to restore AFC module links while its saved config include is active. Debug mode remains disabled. The installer adaptation and link restore are checked separately from the native calibration code.
