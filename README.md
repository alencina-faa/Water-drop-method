# Water Drop Method

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Status](https://img.shields.io/badge/status-active-success)

Desktop app based on Tkinter to implement the Water Drop Method and determine the structural stability of soil aggregates.

## Distribution

The application is currently distributed as a compiled build for Windows 64-bit.

- GitHub Releases: https://github.com/alencina-faa/Water-drop-method/releases
- SourceForge: https://sourceforge.net/projects/water-drop-method/

## Highlights

- GUI workflow with tabs for camera preview, threshold setup, measurement, drop energy, and video processing.
- Runtime state persisted per user on Windows.
- Package-safe import structure for src-layout projects.
- Basic automated test suite with structural and persistence checks.

## Project Structure

- `src/Water_drop_method`: application package
- `tests`: automated tests
- `output`: local build artifacts (ignored by git)

## Requirements

- Python 3.10+
- Dependencies:
  - `pillow`
  - `numpy`
  - `matplotlib`

## Install (Editable)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

## Run

```bash
python -m Water_drop_method
```

## Run Tests

```bash
pytest -q
```

## Tabs Guide

| Tab | What it is used for | Main actions | Screenshot |
| --- | --- | --- | --- |
| Camera | Preview the camera feed and validate framing before measurements. | Select camera device, Start Preview, Stop Preview. | <img src="screenshots/image1.png" alt="Camera tab" width="80%" /> |
| Set Threshold | Compute and confirm the photodiode threshold. | Select DAC device, set number of measures, Set Threshold, Confirm Threshold. | <img src="screenshots/image2.png" alt="Set Threshold tab" width="80%" /> |
| Measurement | Execute the drop measurement workflow. | Select camera and DAC, set drops and previous frames, Save File As, start/stop acquisition. | <img src="screenshots/image3.png" alt="Measurement tab" width="80%" /> |
| Drop Energy | Estimate drop velocity and impact energy from physical parameters. | Configure physical values and run Start Simulation. | <img src="screenshots/image4.png" alt="Drop Energy tab" width="80%" /> |
| Video Processing | Batch-process videos and analyze normalized area over frames. | Load videos folder, define hole area, Process Videos, inspect plots and outputs. | <img src="screenshots/image5.png" alt="Video Processing tab" width="80%" /> |

## Runtime State Files

The app stores runtime state in a per-user writable folder:

- Windows: `%APPDATA%\\WaterDropMethod`
- Fallback: `<home>/WaterDropMethod`

Persisted files:

- `threshold.txt`
- `hole_area.txt`

## Legacy Migration

If legacy `threshold.txt` or `hole_area.txt` files are found in the current working directory, the app performs a one-time best-effort copy to the per-user state folder when those values are requested.

These runtime files are intentionally excluded from version control.
