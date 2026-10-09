# Input audit

The input contract is inherited unchanged from
`analyses/ride-sr-threshold-viewer-001/input_audit.md` (SHA-256
`a7f8b9a6c5628b84fea74b130e71ed9e66664f5b224371c7b7b29ebf71013233`)
and `input_manifest.json` in that directory (SHA-256
`73fd60b9c2adde6cb48eb021b035e8d248014a045b15ae005cb904d5ca890083`).
This family member changes browser presentation only.

- The MAT source hash is
  `6bcfedd8b2b2b2960d1a088aa842049fa02c1d5fbfce397ac7299145ba2bf6d0`.
- `stS`, `stC`, and `stR` are finite, shape-aligned arrays of 1,751 time × 28
  channels × 137 trials; this viewer consumes S and R after transposition to
  trial × channel × time.
- No sample is missing or non-finite. Trial identity is positional MAT index;
  the 137 positions are unique and align one-to-one with the 137 finite
  response latencies.
- Time runs from −1,500 to 2,000 ms in 2 ms steps and contains one zero sample.
  Response latencies span 492–1,000 ms and fall inside the epoch.
- Source values are volts, as confirmed by the data owner, and are converted to
  µV with `source × 1e6`.
- Channel labels are external to the MAT and use the notebook-derived 28-label
  list; the viewer displays this provenance limitation.
- The source is filtered for presentation with MNE-Python 0.5–20 Hz,
  fourth-order Butterworth IIR, zero-phase forward–reverse filtering, without
  baseline correction, resampling, interpolation, or decimation.
- S/R filtered values are encoded as signed little-endian int16 at
  0.01 µV/count. Optional browser smoothing does not modify the source,
  filtering result, or embedded payload.
