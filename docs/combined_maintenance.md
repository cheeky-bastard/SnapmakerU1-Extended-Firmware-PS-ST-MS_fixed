# Maintaining the combined 2.0 line

**Updated: 2026-11-19**

This repository intentionally stays on stock **2.0.0.205**. Paxx's present `develop` uses **2.1.2**; there is no current separate 2.0 develop branch. Therefore "current with 2.0" means retaining the last reviewed Paxx 2.0 source (`2c80e3d`), reviewing later fixes for compatibility, and explicitly backporting selected fixes. Never blindly merge `paxx/develop`, change `vars.mk` to 2.1, or reuse the 2.1 native/nozzle patches here.

The `combined-source-lock.json` file records exact source inputs. Source tracking branches are snapshots, not promises that upstream has stopped changing. The fork's original `develop` is archived under `archive/initial-fork`.

## Review an update

1. Fetch upstream read-only. Inspect Justin's `feat/u1-phase-stepping` and Paxx commits since the pinned source. Confirm the firmware base remains 2.0. Select only compatible changes; retain their attribution and provenance.
2. Prepare a local integration branch. Review `vars.mk`, MCU presets and updater metadata, overlay order, changed host modules, our exact native/nozzle source guards, config migration and the sample phase configuration. An unexpected source hash requires adapting and reviewing the patch; never relax a guard to make it pass.
3. Preserve Justin's phase guide; when incorporating his updates, take the corresponding guide and source pin together. Keep calibration work instructions alongside it. Record compatibility decisions and source SHAs in the lock and change record.
4. Run the combined workflow and inspect the unpacked image. Phase support intentionally replaces the two AT32 MCU payloads; verify their pairing and recovery hashes. The extra GD32 payload and original container format must remain intact. Check the six calibration/native payloads, actual regression tests and target-image C helper load.
5. Publish only from this owner's repository as an experimental prerelease. Record the binary checksum, exact source commit and build verification records. Printer acceptance is a separate operator-controlled step. Keep raw logs, backups, credentials and calibration tables private.

No upstream write or PR is authorized. No scheduled automatic merge is configured. The independent 2.1 repository is outside this package's update path.
