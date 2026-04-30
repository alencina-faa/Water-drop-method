# Water Drop Method

Desktop app based on Tkinter to implement the Water Drop Method and determine the structural stability of soil aggregates.

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
