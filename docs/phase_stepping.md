---
title: Phase Stepping
---

# Phase Stepping (experimental)

> **Warning**: Phase stepping drives the X/Y motor coil currents directly from the mainboard MCU at 10 kHz instead of using step pulses. It is experimental: tested in depth on one U1 and now running on a second. So far it appears to help (quieter motion, smoother walls) with no drawbacks observed: prints look the same and run at the same speed. That is not yet proven across many printers.

The `phase` mod (`PROFILE=extended-phase`, combinable with other mods) builds the mainboard firmware from [`justinh-rahb/u1-klipper`](https://github.com/justinh-rahb/u1-klipper) (pinned in `overlays/mods/phase/95-phase-stepping/scripts/01-build-phase.sh`), a U1 port of [Hannott/kalico](https://github.com/Hannott/kalico)'s phase stepping, and installs the matching Klipper modules. It requires an **AT32 mainboard**: `klippy.log` shows `Main MCU model: stm32f103xe`. On other mainboards do not add the phase config.

The MCU images need GNU Arm 10.3-2021.10. Set `MCU_CROSS_PREFIX` to use one from the build image; otherwise the build fetches ARM's release for the host and checks its SHA-256.

## Install

Each build is Extended plus the named mods:

| File | Contents |
|---|---|
| `U1_extended_*_upgrade.bin` | Extended, **no** phase stepping |
| `U1_extended-phase_*_upgrade.bin` | Extended + phase stepping |
| `U1_extended-multiace-phase_*_upgrade.bin` | Extended + multiACE + phase stepping |
| `U1_extended-afc-phase_*_upgrade.bin` | Extended + AFC + phase stepping |

Install the same way as any Extended release ([install guide](install.md)): copy the `.bin` to the root of a FAT32 USB drive, then on the touchscreen go to `Settings` > `About` > `Firmware Version` > `Local Update`. The update also flashes the mainboard and toolhead MCUs.

Phase stepping is **off** after installing. Nothing changes until you add the config.

## Enable phase stepping

1. Create `extended/klipper/phase.cfg` in your printer config (auto-included):

   ```ini
   [phase_stepping stepper_x]
   auto_enable: False

   [phase_stepping stepper_y]
   auto_enable: False
   ```

   Restart Klipper (`RESTART`). This only registers the commands; the motors still step normally.

2. Home, move to the middle of the bed with the nozzle raised, and run the short per-motor test (on CoreXY one motor alone moves the head diagonally):

   ```
   PHASE_STEPPING_TEST STEPPER=stepper_x DISTANCE=5 VELOCITY=5 ACCEL=100
   PHASE_STEPPING_TEST STEPPER=stepper_y DISTANCE=5 VELOCITY=5 ACCEL=100
   ```

   Each should report `lost 0`, `Host link: 0 received bytes lost on the MCU`, and `Returned to the start phase`. If not, stop and re-home.

3. Turn it on and off by hand:

   ```
   PHASE_STEPPING_ENABLE STEPPER=stepper_x
   PHASE_STEPPING_ENABLE STEPPER=stepper_y
   PHASE_STEPPING_ENABLE STEPPER=stepper_x ENABLE=0
   PHASE_STEPPING_ENABLE STEPPER=stepper_y ENABLE=0
   ```

### Printing with phase stepping

Recommended: add these two lines as the **last lines of your slicer's machine start G-code** (after `TIMELAPSE_START` in the Snapmaker profile), so Snapmaker's start sequence (wiping, auto-feed, flow calibration, bed mesh) runs in normal stepping:

```
PHASE_STEPPING_ENABLE STEPPER=stepper_x
PHASE_STEPPING_ENABLE STEPPER=stepper_y
```

No end G-code is needed: phase stepping switches off when the motors are released (`M84`, idle timeout, cancel, error, emergency stop).

Alternatively, set `auto_enable: True` for both steppers. Phase stepping then turns on after every homing and comes back after each bed or nozzle probing command, so it is on for the print with no slicer change. Snapmaker's start sequence then also runs with phase stepping on, switching off for each homing or probing command and back on after it. (Before u1-klipper `efef63d`, probing turned it off for the rest of the print; see Known issues.)

### How it behaves

- **Homing and probing:** switches off for homing moves (sensorless homing and precise CoreXY homing work as stock) and comes back on when `G28` finishes. The U1's bed probe moves count as homing moves for the X/Y motors, so probing (bed mesh, bed and nozzle detection) switches it off too; it comes back on once that probing command finishes.
- **Motors off / cancel / error:** switches off cleanly with the motors.
- **Emergency stop:** the MCU drops phase stepping and releases the coils; `FIRMWARE_RESTART` recovers normally.
- **Tool changes:** stays on through docking and pickup.
- **Status:** `phase_stepping stepper_x` / `stepper_y` report `enabled`. While on, `klippy.log` stats lines show `phase_stepping_stepper_x: … lost_ticks=… update_max_us=… rx_overruns=…`.

## Optional: measurement and calibration

The toolhead accelerometer can measure each motor's vibration harmonics and fit angle corrections. Add to `phase.cfg` (T0 must be the toolhead on the carriage):

```ini
[phase_calibrate]
accel_chip: lis2dw e0_lis2dw
speed_min: 30
speed_max: 80
```

```
PHASE_STEPPING_ENABLE STEPPER=stepper_x
PHASE_STEPPING_ENABLE STEPPER=stepper_y
MEASURE_MOTOR_HARMONICS STEPPER=stepper_x SPEED_MIN=20 SPEED_MAX=160 POINT=135,167,10 GRAPH=0
PHASE_STEPPING_CALIBRATE STEPPER=stepper_x POINT=135,167,10
```

- Use `GRAPH=0` on the printer. Plotting runs matplotlib on the U1's small host; copy the CSV from `/tmp` and plot elsewhere.
- Sweeps whose top speed cannot be reached within the travel limit now fail with "a speed ramp needs more travel" (20–180 mm/s plans fine; 20–200 does not).
- To keep calibration one click away, add this macro to `phase.cfg`:

  ```ini
  [gcode_macro PHASE_CALIBRATE_XY]
  description: Calibrate phase stepping angle corrections for X and Y (T0 accelerometer)
  gcode:
    {% if printer.toolhead.homed_axes != "xyz" %}
      G28
    {% endif %}
    T0 A0
    PHASE_STEPPING_ENABLE STEPPER=stepper_x
    PHASE_STEPPING_ENABLE STEPPER=stepper_y
    PHASE_STEPPING_CALIBRATE STEPPER=stepper_x POINT=135,167,10 GRAPH=0
    PHASE_STEPPING_CALIBRATE STEPPER=stepper_y POINT=135,167,10 GRAPH=0
    RESPOND MSG="Phase calibration done. Review the results, then run SAVE_CONFIG to keep the corrections."
  ```

  Each run starts from no correction, so rerunning recalibrates from scratch.
- `SAVE_CONFIG` stores accepted corrections. On the test printer calibration found nothing worth correcting: 2nd/4th harmonics were below noise, and the remaining vibration is a frame resonance around 55–80 Hz, which angle corrections cannot cancel.

## Test printers

Both U1s (AT32 mainboards) run the same non-stock TMC2240 driver tune, `tmc_autotune.cfg` from [Argolein's U1 config](https://github.com/Argolein/SnapmakerU1/blob/main/SnapmakerU1-CustomConfig/01_ArgoConfig.cfg), at the stock 1.2 A run current. While phase stepping is on it uses that tune's spreadCycle chopper settings (`TOFF 5, HSTRT 7, HEND 9, TBL 1, TPFD 2`; Klipper's defaults are `3, 5, 2, 2, 4`), which shape how the drivers regulate coil current. Its StealthChop `PWM_*` settings do nothing while phase stepping is on, because phase stepping turns StealthChop off. With stock driver settings the sound and the results may differ; that setup has not been tested.

- **Printer 1:** `extended-phase`. All the testing below.
- **Printer 2:** `extended-multiace-phase`. Calibration found and saved a small 1st-harmonic correction on X (0.6–0.9 µm down to about 0.2 µm); `SHAPER_CALIBRATE` with phase on matched its earlier phase-off result (X mzv 54.4 Hz, Y mzv 47.2 Hz).

## Validation on printer 1

- Single-motor tests and combined motion at 10–300 mm/s; ABS prints with travel up to 500 mm/s, accel up to 10000.
- Homing, `M84`, T0↔T1 tool changes, `M112` and touchscreen emergency stop, print cancel.
- MCU update 2–5 µs of each 100 µs tick, 0 lost ticks, 0 MCU serial overruns across full prints.
- 20 kHz was tried (u1-klipper `f204caa`) and reverted in `5caf5b1`: the mainboard and host link handled it (motor updates under 5 µs of each 50 µs tick, 0 lost ticks, no host resends with 164,000 TMC register reads), and motor vibration from 20 to 160 mm/s measured the same as at 10 kHz, but the Z motor (normal step pulses) lost about 4 full steps (50 µm) within 30 cycles of combined XY+Z moves with phase stepping on, and a print showed a skipped Z step. No phase-off or 10 kHz control run was made, so the cause is not isolated. Phase stepping runs at 10 kHz.
- Sound: the speed-dependent stepper tones (1–3 kHz) disappear; overall loudness is similar. Motion feels quieter.
- Prints: full ABS cubes with phase on and off came out the same speed; the phase-on cube's walls look smoother.
- Input shaping: `SHAPER_CALIBRATE` with phase on and off gave the same result (X mzv 53.4 Hz, Y mzv 46.6 Hz; resonance peaks at 51 / 45 Hz within run-to-run noise). Existing shaper settings stay valid; no need to recalibrate.
- Probing resume (this release, on printer 1 with `auto_enable: True`): phase stepping was on after `G28` (which includes a Z probe) and came back on for both X and Y after a full `BED_MESH_CALIBRATE`. X reported 0 lost ticks and 0 MCU serial overruns, and no MCU link resends occurred.
- Print on printer 2 with `auto_enable: True` and no slicer lines: phase stepping switched off and on through Snapmaker's start sequence (about 3.5 minutes, longest off stretch about 1:40 during the bed prescan), was on before printing began, and stayed on through the first 5 minutes of printing (where monitoring stopped). 0 lost ticks and 0 MCU serial overruns, no MCU link resends. Before this fix that printer's prints ran with phase stepping off after the bed prescan.
- Host link (u1-klipper `ad066ed`, on printer 1): with phase stepping on, XY moves and 240,000 TMC register reads in 30 minutes caused no host resends. Before the fix the same test produced one every ~94,000 reads.
- multiACE and AFC builds: neither mod touches the MCU firmware or the Klipper files phase stepping patches, so they combine cleanly. multiACE + phase runs on printer 2; AFC + phase has not been tested on a printer.

## Known issues

- **Fixed in u1-klipper `b588bd2`:** with phase stepping on, a Z-only move while X/Y were at rest could hang the Klipper host (100% CPU, no response, Mainsail stuck loading). The host code that skips ahead over long rests walked past the end of the move list. It happened only sometimes, at either tick rate. Restarting Klipper recovered it.
- **Fixed in this release:** in earlier releases (source `0bf75e9`), Snapmaker's bed probing turned phase stepping off and nothing turned it back on, so with `auto_enable: True` alone a print ran with phase stepping off. The slicer start G-code lines were not affected.
- **Fixed in u1-klipper `ad066ed`:** with phase stepping on, the host occasionally had to resend a message to the mainboard (about once an hour of printing; recovered within milliseconds, prints unaffected). A TMC driver command that arrived while a coil write was in flight kept interrupts off for about 11 µs, just over one serial byte, and the mainboard's UART then received one byte twice and dropped the next. Interrupts now stay off for at most about 2 µs there.
- Snapmaker's touchscreen shows any G-code error (e.g. a rejected sweep) as a "System Anomaly" dialog. Klipper keeps running; dismiss it.
- At rest, the stock X/Y hold current (1.2 A, spreadCycle) buzzes audibly. That is stock U1 behavior, not phase stepping.

## Reverting

Flash a regular Extended release or the stock firmware the same way; it restores the stock mainboard and toolhead MCU firmware. Remove `extended/klipper/phase.cfg` first, or Klipper will fail to start on firmware without phase stepping.
