# C3 RIDE recording comparison

Status: retrospective exploratory specification approved by the user before the
comparison script was executed. This is not a preregistration, and the folder
was not committed before outcomes were generated.

## Purpose

Produce descriptive 2-D C3 trial × time plots for every available RIDE
recording before changing the 3-D application. Select a visually pronounced
example transparently; this is selection-informed exploration, not inference.

## Inputs and channel identity

- All `data/*_RIDE_result.mat` files available at freeze time: S01 near, S04
  far, S14 near, and S17 near.
- Component fields: `results.stS`, `results.stC`, and `results.stR`.
- Data orientation in MAT: time × channel × trial; MNE orientation: trial ×
  channel × time.
- User-directed 28-channel order recovered from cell 111 of
  `Far_Close-MI_MA_ME.ipynb` in the analysis project:
  F3, F4, FC5, FC3, FC1, FCz, FC2, FC4, FC6, C5, C3, C1, Cz, C2, C4,
  C6, CP5, CP3, CP1, CPz, CP2, CP4, CP6, P3, Pz, P4, O1, O2.
- C3 is column 11 (zero-based index 10).

## Processing and plots

- Use MNE `EpochsArray` for component/channel handling at 500 Hz.
- Preserve every trial and every one of the 1,751 samples; no filtering,
  baseline correction, resampling, smoothing, interpolation, or decimation.
- Interpret MNE/RIDE arrays in volts and convert to microvolts (`× 10^6`) for
  display. This follows the supplied notebooks, which pass the arrays into
  MNE and multiply the same signals by `1e6` for plotting, and the user's
  explicit confirmation that the displayed unit is microvolts.
- Stable-sort trials by `results.latency0[2]`; preserve original trial index.
- Plot one 4 × 3 overview: recordings by S/C/R component, C3 trial × time,
  with stimulus onset and the behavioral-RT curve.
- Plot a separate 3 × 1 panel of trial-mean C3 waveforms for all recordings.
- Use one shared symmetric color limit: global 99.5th percentile of absolute
  C3 amplitude across all recordings/components. Record saturation explicitly.

## Descriptive selection metric

For each recording/component, report the 99th percentile of absolute C3
amplitude over every trial and time sample. The recording-level score is the
maximum of its three component scores. This robust metric is a visual-selection
aid only; the figures remain the primary basis for the user's choice.

## Controls

- Validate all three component shapes and finite values.
- Validate exactly 28 channels, a single 0-ms sample, and RT length equal to
  trial count with every RT inside the epoch.
- Validate stable sorting is a bijection and nondecreasing in RT.
- Validate saved figures are nonblank and dimensions are nonzero.
- Hash every input and result.

## Interpretation limits

The selected recording is chosen after outcome inspection and is therefore
selection-informed. The specification was user-approved before execution, but
its pre-outcome state is not independently certified by Git history. It must
not be presented as representative of subjects or conditions. Only one
far-condition recording is available, so this comparison cannot distinguish
subject from condition.
