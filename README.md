# EEG Volume Viewers

Interactive exploration of event-locked EEG power as a dense
channel × time × frequency volume, plus a second viewer for RIDE-decomposed
single-trial activity as trial × channel × time volumes.

- [Open the EEG time–frequency demo](https://kolascoco.github.io/eeg-tfr-volume/)
- [Open the RIDE single-trial demo](https://kolascoco.github.io/eeg-tfr-volume/ride.html)

## Dependencies

- Python 3.8–3.11 (the published RIDE artifact was generated with 3.8.1)
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

The published RIDE viewer uses `docs/ride-volume-S.i16.gz` and
`docs/ride-volume-R.i16.gz` together with
`docs/ride-volume.json`. This compact dataset contains only the S and R
components needed by the app, all 457 behavioral response times, the full
28-channel order, trial identities, and all 1,751 samples from every trial.
The unused C component and MATLAB-specific fields are omitted. The three
source recordings contribute 149, 137, and 171 trials respectively.

Before compact export, each source recording received an MNE 0.5–20 Hz zero-phase
Butterworth IIR filter with design order 4 (effective order 16 after band-pass
transformation and forward–reverse application), without resampling or
decimation. Values are stored as signed 16-bit microvolt counts at 0.01 µV per
count and gzip-compressed for transport. The maximum quantization error is
0.005 µV. Electrode labels follow the ordered list in the data owner's analysis
notebook; the original MAT files did not embed them. Source filenames, sizes,
and SHA-256 hashes remain recorded in the compact manifest for provenance.

## Run locally

Start the MNE processing server:

```bash
python src/eeg_tfr_volume.py serve --host 127.0.0.1 --port 8765
```

Open <http://127.0.0.1:8765>, select a FIF recording, choose an annotation
event, adjust the preprocessing parameters, and build the interactive volume.

To regenerate and open the static RIDE viewer:

```bash
python scripts/generate_ride_viewer.py
python -m http.server 8766 --directory docs
```

Then open <http://127.0.0.1:8766/ride.html>. The two side-by-side boxes show
the stimulus-locked S component and response-locked R component. Their camera,
time limits, trial limits, channel montage, time stretch, and color limits are
linked. All 457 trials remain loaded and can be ordered globally by response
time or kept in recording-plus-original-trial order. Linked trial-start and
trial-end sliders select an inclusive visible rank window from either side;
the rank labels follow the currently selected trial order.
The X-ray mode can show positive, negative, or both-polarity thresholded
structures with crisp outlines and time-directed threads. The compact HTML
loads the two `docs/ride-volume-{S,R}.i16.gz` assets, which contain every S/R
voxel as gzip-compressed signed 16-bit microvolt data. Each file is about 31 MiB,
below GitHub's 50 MiB warning threshold. With smoothing **Off**,
Canvas rendering samples the native grid for interactive performance and does
not interpolate or smooth across trials, channels, or time. At extremely
permissive thresholds, a visible
2,400-voxel-per-component safety cap keeps the browser responsive and reports
the displayed/eligible counts.

The optional dense-view smoothing slider is off by default. Each level applies a centered
rolling mean over ±10 ms of time and then ±1 displayed trial (up to ±80 ms and
±8 trials), independently for each channel. Trial smoothing follows the chosen
RT-sorted or original trial order. This changes only the browser presentation;
the embedded payload and MNE preprocessing remain unchanged.

The X-ray view uses a separate pipeline and defaults to **Strong** structure smoothing. It
smooths the sampled display grid along time, displayed-trial, and ordered-channel
axes, then removes same-polarity 6-connected structures smaller than eight
rendered voxels. Its Off, Light, Balanced, and Strong levels do not affect the
dense view or embedded data. The default X-ray threshold is 30% of the selected
color limit; both settings remain adjustable.

The interactive head montage filters both cubes automatically. In **Recorded
channels** mode, the left, midline, and right parts of the head are separately
clickable and can be combined with **P–O**, **FC–C–CP**, or **F** sectors.
The representation selector can instead plot **left − right** or **right −
left** sample-wise differences for 12 homologous pairs; midline electrodes are
excluded from that transform. Linked channel-start and channel-end sliders
continue to scroll or trim the resulting channel or pair list from either
side. The montage distinguishes the complete selected pool (dim teal) from
the channels or homologous pairs currently feeding the cube (gold); when four
or fewer entries are visible, their electrode names appear on the head. The
visible pair list is also printed below the montage. A new region selection
resets the visible range to all matching entries, and the last selected region
cannot be deselected because an empty cube is rejected. Cube
adjacency follows the displayed list rather than physical inter-electrode
distance.

Smoothing allocates full-size floating-point presentation buffers in the
browser. The two 457 × 28 × 1,751 component files total about 62 MiB and expand
to approximately 85 MiB in memory; the
dense-smoothing recomputation can exceed 350 MiB before page and Canvas
overhead. On memory-constrained devices, keep
smoothing Off or use a low level. Smoothing can attenuate peaks, so threshold
occupancy should always be compared with the unsmoothed view and color or
threshold limits may need readjustment.

## References

- Ouyang, G., Schacht, A., Zhou, C., & Sommer, W. (2013). Overcoming
  limitations of the ERP method with Residue Iteration Decomposition (RIDE):
  A demonstration in go/no-go experiments. *Psychophysiology, 50*(3),
  253–265. <https://doi.org/10.1111/psyp.12004>
- Syrov, N., Muhammad, D. G., Medvedeva, A., Yakovlev, L., Kaplan, A., &
  Lebedev, M. (2025). Revealing the different levels of action monitoring in
  visuomotor transformation task: Evidence from decomposition of cortical
  potentials. *Psychophysiology, 62*(1), e14708.
  <https://doi.org/10.1111/psyp.14708>
