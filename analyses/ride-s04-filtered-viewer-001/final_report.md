# Filtered S04 RIDE viewer

## Result

`docs/ride.html` now presents `S04_far_RIDE_result.mat` as three linked S, C,
and R trial × channel × time volumes. The presentation data are filtered with
MNE from 0.5 to 20 Hz using a zero-phase Butterworth IIR with design order 4
(effective order 16 after band-pass transformation and forward–reverse
application).

All 137 trials, 28 channels, and 1,751 samples are retained in each component
payload. There is no baseline correction, resampling, interpolation, or
source-data decimation. The browser renderer still selects deterministic native
samples for interactive drawing, as disclosed in the UI.

## Validation

- Real input shape, time, RT, finiteness, and ordered electrode count passed.
- Filtering preserved every array shape and finite value.
- Synthetic response control amplitudes: 0.00261 at 0.1 Hz, 0.99794 at 10 Hz,
  and 0.00000276 at 80 Hz.
- Freshly encoded filtered arrays exactly matched every embedded payload byte.
- Full repository suite: 11 passed, 0 failed.
- Browser inspection confirmed nonblank boxes, S04/filter labels, electrode
  endpoints F3/O2, controls, scale, and references.

The shared robust display range is ±15.8589 µV. Saturated filtered voxels are
0.500% for S, 0.493% for C, and 0.493% for R.

## Limitations

This is configuration 2 in a selection-informed visualization family: S04 was
chosen after comparing four recordings. The MAT file is not self-describing
for electrode names or amplitude units; these rely on notebook/user provenance.
Zero-phase filtering of finite epochs can create boundary transients, so the
ends of the −1.5 to 2.0 s window should not be overinterpreted.
