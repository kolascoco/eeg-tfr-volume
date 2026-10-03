# EEG TFR Volume

Interactive exploration of event-locked EEG power as a dense
channel × time × frequency volume.

[Open the public interactive demo](https://kolascoco.github.io/eeg-tfr-volume/)

The signal-processing pipeline uses MNE-Python. The browser viewer supports:

- dense cubic, linear, and native-voxel rendering;
- rotatable orthogonal slices and threshold volumes;
- time × frequency, time × channel, and channel × frequency views;
- posterior-to-anterior channel ordering;
- event-onset highlighting, scrolling, color thresholds, and time stretching.

## Run locally or in GitHub Codespaces

```bash
python src/eeg_tfr_volume.py serve --host 0.0.0.0 --port 8765
```

Open port 8765, select a FIF recording, choose its annotation event, and build
the volume. In Codespaces, the forwarded port opens in the browser.

## Included EEG recording

`data/NS_MI_TS_raw.fif` is the repository owner's recording and is intentionally
shared for demonstration and reproducibility. It is stored with Git LFS. See
[`data/README.md`](data/README.md) for the measured metadata inventory.

Generate a viewer from event `11/3`, for example:

```bash
python src/eeg_tfr_volume.py build data/NS_MI_TS_raw.fif \
  --event 11/3 \
  --output docs/recording-11-3.html \
  --cache recording-11-3.npz
```

## Generate the public synthetic demo

```bash
python scripts/generate_demo.py
```

This creates a deterministic synthetic FIF under `data/`, processes it with
the same MNE pipeline, and writes `docs/index.html` for GitHub Pages.

## Publish GitHub Pages

1. Push the repository to GitHub.
2. In **Settings → Pages**, select **GitHub Actions** as the source.
3. The included workflow deploys `docs/` after each push to `main`.

## Data policy

The repository owner explicitly authorized publication of the included
recording. Its standard MNE metadata fields were audited before publication;
the audit found no subject name, experimenter, project name, measurement date,
description, device information, or `subject_info`. This does not prove that
EEG is non-identifying. Do not add recordings from other participants without
their release authorization and a fresh metadata audit.

## Tests

```bash
PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-eeg python -m unittest -v tests/test_eeg_tfr_volume.py
```

## Scientific limitation

Interpolation along the channel index is a display operation, not anatomical
interpolation. The viewer orders channels posterior-to-anterior using MNE head
coordinates but does not claim that adjacent rows are equally spaced on the
scalp.
