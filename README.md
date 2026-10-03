# EEG TFR Volume

Interactive exploration of event-locked EEG power as a dense
channel × time × frequency volume.

[Open the public synthetic demo](https://OWNER.github.io/eeg-tfr-volume/)

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

## Generate the public synthetic demo

```bash
python scripts/generate_demo.py
```

This creates a deterministic synthetic FIF under `data/`, processes it with
the same MNE pipeline, and writes `docs/index.html` for GitHub Pages.

## Publish GitHub Pages

1. Replace `OWNER` in the demo link above with the GitHub account or
   organization name.
2. Push the repository to GitHub.
3. In **Settings → Pages**, select **GitHub Actions** as the source.
4. The included workflow deploys `docs/` after each push to `main`.

## Data policy

The repository includes only a generated synthetic demonstration. Do not
commit human EEG unless it is explicitly authorized for public release and
has been checked for identifying metadata. Standard GitHub repositories also
reject individual files over 100 MiB; the project recordings are larger than
that. Use approved external research storage or download them only inside a
private Codespace.

## Tests

```bash
PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-eeg python -m unittest -v tests/test_eeg_tfr_volume.py
```

## Scientific limitation

Interpolation along the channel index is a display operation, not anatomical
interpolation. The viewer orders channels posterior-to-anterior using MNE head
coordinates but does not claim that adjacent rows are equally spaced on the
scalp.
