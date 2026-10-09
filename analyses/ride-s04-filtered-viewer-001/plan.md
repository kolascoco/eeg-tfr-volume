# Filtered S04 RIDE viewer plan

Status: user-confirmed implementation specification on 2026-10-07.

## Purpose

Rebuild the descriptive three-box RIDE viewer with `S04_far` because the data
owner judged it to be the cleanest available recording. The browser presentation
uses filtered component arrays and makes no inferential claim.

## Frozen choices

- Input: `data/S04_far_RIDE_result.mat`.
- Components: `results.stS`, `results.stC`, and `results.stR`.
- Axes: trial × channel × stimulus-relative time.
- Preserve all 137 trials, all 28 channels, and all 1,751 time samples.
- MNE band-pass: `l_freq=0.5`, `h_freq=20` Hz.
- Defensible implementation default: zero-phase Butterworth IIR with design
  order 4 (`method='iir'`, SOS representation, `pad='reflect_limited'`). The
  effective order is 16 after band-pass transformation and forward–reverse
  application. A default FIR at 0.5 Hz would be longer than these 3.5-second
  epochs.
- No baseline correction, resampling, interpolation, or source-data decimation.
- Display quantization and deterministic Canvas sampling remain presentation
  mechanisms and are disclosed in the interface.
- Electrode order follows the data owner's analysis notebook:
  F3, F4, FC5, FC3, FC1, FCz, FC2, FC4, FC6, C5, C3, C1, Cz, C2, C4,
  C6, CP5, CP3, CP1, CPz, CP2, CP4, CP6, P3, Pz, P4, O1, O2.

## Controls

- Validate MAT shapes, finiteness, time axis, RT length/range, and channel count.
- Verify filtering preserves array shape and finite values.
- Verify an in-band 10 Hz signal is retained while 0.1 and 80 Hz signals are
  attenuated in a synthetic frequency-response control.
- Verify generated HTML embeds S04, the exact filter parameters, electrode
  labels, and all three nonconstant component payloads.
- Inspect the rebuilt page in a browser and run the repository test suite.

## Interpretation limits

S04 was selected after visual inspection of four recordings, so this is a
selection-informed presentation choice. Filtering changes the displayed
waveform and can introduce edge transients, especially near epoch boundaries.
The MAT file does not embed channel labels or amplitude units; those remain
external provenance from the user's notebooks and explicit confirmation.
