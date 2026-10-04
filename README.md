# EEG TFR Volume

Interactive exploration of event-locked EEG power as a dense
channel × time × frequency volume.

[Open the public interactive demo](https://kolascoco.github.io/eeg-tfr-volume/)

## Dependencies

- Python 3.11
- Git LFS
- MNE-Python 1.6.1
- NumPy 1.24–1.x
- SciPy 1.10–1.14

Install the Python dependencies from `requirements.txt`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Download the example recording tracked with Git LFS:

```bash
git lfs install
git lfs pull
```

`data/NS_MI_TS_raw.fif` is the my eeg example recording shared for demonstration.

## Run locally

Start the MNE processing server:

```bash
python src/eeg_tfr_volume.py serve --host 127.0.0.1 --port 8765
```

Open <http://127.0.0.1:8765>, select a FIF recording, choose an annotation
event, adjust the preprocessing parameters, and build the interactive volume.
