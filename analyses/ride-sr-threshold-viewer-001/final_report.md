# Final report: S/R RIDE threshold-volume viewer

## Result status

**PASS-WITH-RISKS.** This is a descriptive visualization artifact, not an
inferential analysis. It is configuration 2 of 2 viewer configurations tried
in the RIDE viewer family and is selection-informed by the data owner's choice
of S04 far as the cleanest recording.

## What ran

The S04 far RIDE MAT file was validated, transposed from time × channel × trial
to trial × channel × time, and filtered with MNE at 0.5–20 Hz using a
zero-phase Butterworth IIR design (design order 4; effective order 16). Only S
and R were encoded into the page, as little-endian int16 at 0.01 µV/count.
The generated static HTML renders synchronized left/right volumes.

## Support and controls

- N = 137 fixed trials, 28 channels, 1,751 samples from −1,500 to 2,000 ms.
- Response times: 492–1,000 ms; trials may be RT-sorted without exclusion.
- S extrema: −47.66 to 54.92 µV; R extrema: −48.67 to 54.89 µV.
- Initial symmetric color limit: ±15.86 µV (largest component-wise 99.5th
  percentile of absolute amplitude).
- Adjustable: time/channel bounds, time stretch, scene zoom, color limit,
  threshold, structure opacity, polarity, threads, outlines, and camera plane.
- Not adjustable: trial count or trial bounds.

No effect sizes, confidence intervals, p-values, null tests, or multiplicity
family apply because no inferential claim is made.

## Verification

- Canonical config/file validation: `CONFIG VALID -- instrument chain: PASS
  (4 stages)`.
- Automated tests: 11/11 passed.
- Signed payload reconstruction error: at most 0.0051 µV; no clipping.
- Browser: dense and threshold views nonblank; signed polarity and time/channel
  controls exercised; no warnings/errors.
- Worst case at ±0.50 µV and 5% threshold: S 2,400/45,214 and R
  2,400/45,241 eligible render voxels shown; paired dense/threshold operation
  completed in 95 ms in the local check.
- Independent adversarial verdict: PASS-WITH-RISKS.

## Residual risks and interpretation limits

- When the 2,400-voxel safety budget activates, the strongest eligible voxels
  are shown; weaker eligible voxels are omitted, potentially changing apparent
  topology and breaking weaker threads. The UI reports this live.
- Rendering samples at most 64 time × 36 trial × 20 channel native positions;
  every source voxel is embedded but not simultaneously drawn.
- Channel names come from the owner's notebook, not the MAT file.
- Finite-epoch filtering can create boundary transients near epoch edges.
- Canvas interaction checks are manual rather than automated end-to-end tests.
- Thresholded structures are descriptive and must not be interpreted as
  statistically significant components.
