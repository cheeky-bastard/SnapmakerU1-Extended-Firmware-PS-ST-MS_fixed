---
title: Phase Stepping
---

# Phase Stepping (experimental)

> **Warning**: Phase stepping drives the X/Y motor coil currents directly from the mainboard MCU at 10 kHz instead of using step pulses. It is experimental and has been validated on one U1.

The `phase` mod (`PROFILE=extended-phase`, combinable with other mods) builds the mainboard firmware from [`justinh-rahb/u1-klipper`](https://github.com/justinh-rahb/u1-klipper) (pinned in `overlays/mods/phase/95-phase-stepping/scripts/01-build-phase.sh`), a U1 port of [Hannott/kalico](https://github.com/Hannott/kalico)'s phase stepping, and installs the matching Klipper modules. It requires an **AT32 mainboard**: `klippy.log` shows `Main MCU model: stm32f103xe`. On other mainboards do not add the phase config.

The MCU images need GNU Arm 10.3-2021.10. Set `MCU_CROSS_PREFIX` to use one from the build image; otherwise the build fetches ARM's release for the host and checks its SHA-256.

## Install

Same as any Extended release ([install guide](install.md)); use the `U1_extended-phase_*_upgrade.bin` build: copy the `.bin` to the root of a FAT32 USB drive, then on the touchscreen go to `Settings` > `About` > `Firmware Version` > `Local Update`. The update also flashes the mainboard and toolhead MCUs.

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

Alternatively, `auto_enable: True` turns it on automatically after every homing.

### How it behaves

- **Homing:** switches off for homing moves (sensorless homing and precise CoreXY homing work as stock) and comes back on when `G28` finishes.
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
- `SAVE_CONFIG` stores accepted corrections. On the test printer calibration found nothing worth correcting: 2nd/4th harmonics were below noise, and the remaining vibration is a frame resonance around 55–80 Hz, which angle corrections cannot cancel.

## Validation on a U1 (AT32)

- Single-motor tests and combined motion at 10–300 mm/s; ABS prints with travel up to 500 mm/s, accel up to 10000.
- Homing, `M84`, T0↔T1 tool changes, `M112` and touchscreen emergency stop, print cancel.
- MCU update 2–5 µs of each 100 µs tick, 0 lost ticks, 0 MCU serial overruns across full prints.
- Sound: the speed-dependent stepper tones (1–3 kHz) disappear; overall loudness is similar.

## Known issues

- One full print showed two single-message host resends to the mainboard (no CRC/sync errors, recovered immediately) where normal prints show none. Under investigation.
- Snapmaker's touchscreen shows any G-code error (e.g. a rejected sweep) as a "System Anomaly" dialog. Klipper keeps running; dismiss it.
- At rest, the stock X/Y hold current (1.2 A, spreadCycle) buzzes audibly. That is stock U1 behavior, not phase stepping.

## Reverting

Flash a regular Extended release or the stock firmware the same way; it restores the stock mainboard and toolhead MCU firmware. Remove `extended/klipper/phase.cfg` first, or Klipper will fail to start on firmware without phase stepping.
