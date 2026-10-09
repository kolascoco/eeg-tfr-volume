# Analysis log

- Selected S04 far based on the earlier C3 comparison requested by the data
  owner.
- Applied the predeclared MNE 0.5–20 Hz zero-phase Butterworth IIR filter.
- Replaced clipped uint8 display encoding with signed int16 at 0.01 µV/count.
- Reduced the public payload and UI to S and R only.
- Removed trial-bound sliders; retained fixed-all-trial ordering control.
- Added linked time/channel bounds, time stretch, zoom, and color limit.
- Added positive/negative/both threshold occupancy voxels, temporal links, and
  crisp screen-space outer strokes without blur.
- First independent audit returned REVISE: corrected point-cloud semantics,
  painter order, color-slider quantization, disclosure, tests, and audit files.
- Added a 2,400-voxel per-component strongest-amplitude safety cap and
  same-polarity neighbor culling so only exposed voxel faces are emitted.
- Stress-tested the minimum vlim/threshold setting in-browser: 45,214 S and
  45,241 R candidates were safely capped, controls remained responsive, and
  no console warnings/errors occurred.
- Completed the formal four-stage load → filter → encode → render instrument
  record; the canonical validator passed with file checks.
- Final independent re-review: PASS-WITH-RISKS. No further implementation
  changes required; residual risks are preserved in the final report.
