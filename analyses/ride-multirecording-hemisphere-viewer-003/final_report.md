# Final report

Status: PASS-WITH-RISKS. The compact-data transport amendment passed numerical,
automated, and browser checks. Publication is ready for the data owner to commit
and push; no RIDE Git LFS objects are required.

## Outcome

The RIDE viewer now stacks all 457 trials from S02_far (149), S04_far (137),
and S07_far (171). Each recording is filtered independently from 0.5 to 20 Hz
before concatenation. The S and R component volumes retain their full 2 ms time
sampling, 28 recorded channels, and recording-aware trial provenance.

The three large source MAT files are replaced for distribution by separate
32,370,614-byte S and 32,402,319-byte R gzip assets plus a 47 KiB JSON manifest.
Each data file stays below GitHub's 50 MiB warning threshold. The compact
binary data retain all 457 × 28 × 1,751 samples and use the viewer's existing
0.01 µV signed-int16 representation. C and unused MATLAB fields are omitted.
Source filenames, byte sizes, and SHA-256 hashes remain in the manifest.

The head montage now has independently selectable left, midline, and right
hemisphere regions in recorded-channel mode. Two additional representations
compute exact sample-wise homologous contrasts for 12 pairs: left minus right
(default) and right minus left. Midline channels are excluded from bilateral
contrasts because they have no homologous counterpart. Channel-window sliders
remain available in every representation. The head map now distinguishes the
selected region pool (dim teal) from the exact channels or pair electrodes
currently feeding the cube (gold). Up to four visible entries also receive
electrode-name labels, and the visible pair/channel list is printed explicitly.

Both S/R viewports now occupy the full page above the controls. All selectors,
sliders, montage controls, checkboxes, and orientation buttons are arranged in
a responsive horizontal card grid below the viewports. At the measured 774 px
browser width, the grid uses two columns; narrow screens collapse to one.

Linked trial-start and trial-end sliders now select an inclusive visible rank
window from the currently selected RT-sorted or recording order. All 457 trials
remain loaded. The trial window drives dense surfaces and interior points,
X-ray sampling, trial-axis labels, and the response-time curtain; a one-trial
window is supported explicitly.

## Validation

- Real-data comparison against freshly filtered MAT sources found a maximum
  absolute difference of 0.0050004 µV for both S and R (the expected half-count
  quantization boundary including float32 rounding). Time, response-time, and
  channel arrays were exactly equal.
- The two `docs/ride-volume-{S,R}.i16.gz` files total 64,772,933 bytes and
  expand to 89,623,184 bytes. Browser validation decoded 22,405,796 samples per component, rendered
  both canvases, and recorded zero warnings or errors.
- The compact JSON records the binary SHA-256, source hashes, dimensions,
  scale, offsets, preprocessing, trial identities, times, response times, and
  channel order. The generator falls back to this compact pair when MAT files
  are absent.
- All 18 automated tests passed in 2.667 seconds using the compact real-data
  fixture.
- Independent compact-transport review reran source filtering/stacking,
  source-to-compact numerical comparison, ten targeted tests, deterministic
  byte-for-byte re-encoding, a same-size corruption control, instrument-chain
  validation, and live Safari rendering. Verdict: PASS-WITH-RISKS.

- Generated `docs/ride.html`: 74,305 bytes, SHA-256
  `eb680ccfd8fe04b3db5b6ec0eb8de6b19ae256c5e363ecd217de9bf8cb047516`.
- Generated `docs/ride-volume-S.i16.gz`: 32,370,614 bytes, SHA-256
  `482f7400c7009dcf8978231e11ed24e86ff9eab5d0b06cffc00f5ce8a21bd804`.
- Generated `docs/ride-volume-R.i16.gz`: 32,402,319 bytes, SHA-256
  `fa930222804802f8189f3931f2780156a569897b9db3bb39e45f2405fa1c000a`.
- Payload shape: 457 trials × 28 channels × 1,751 time samples for each of S
  and R; S is stored first and R second as little-endian signed int16 values
  before lossless gzip transport compression.
- The production subtraction helper passed sign and magnitude regression tests.
- The montage state regression passed all 14 non-empty bilateral region states,
  508 inclusive bilateral slider windows, and 49 recorded-mode region ×
  hemisphere states. Empty selection is rejected without corrupting state.
- Browser validation showed 457 trials, 28 recorded channels, 12 homologous
  pairs, exact C3/C4 highlighting for both C3−C4 and C4−C3, working group
  selection, preserved channel scrolling, and no console warnings or errors.
- Layout validation measured the viewport pair ending at page y=732 and the
  control panel beginning at y=748. At a 774 px browser width, visible control
  cards formed two 366 px columns; the full-width notes card remained below.
- Independent responsive review passed at 1200, 774, 719, and 390 px browser
  widths with 4, 2, 1, and 1 control columns, respectively, no horizontal
  overflow, correct mode visibility, and zero console warnings or errors.
- The production trial-window regression passed 313,959 inclusive and crossing
  cases with zero failures. Browser checks confirmed ranks 101–221, automatic
  crossing to the single rank 301, persistence across order changes, restored
  full range 1–457, updated X-ray occupancy, nonblank canvases, and no console
  messages.
- Fresh-context review reran the full 17-test suite, trial-window regression
  against both template and published HTML, live dense/X-ray/RT-curtain pixel
  checks, prior regressions, all manifest hashes, and the six-stage chain. The
  verdict was PASS-WITH-RISKS.
- A fresh-context adversarial reviewer reran the full suite (16/16), all 508
  bilateral montage windows, 172,550 channel-scroll transitions, every one of
  the 12 pair mappings in both subtraction directions, and live Chrome checks.
  The verdict was PASS-WITH-RISKS.
- Default X-ray occupancy after the production smoothing/connectivity pipeline:
  S positive 17 and negative 18 coherent voxels; R positive 16 and negative 20.
  These form three retained connected components in S (17, 10, and 8 voxels)
  and three in R (16, 12, and 8 voxels).

## Interpretation and limitations

This is a diagnostic visualization, not an inferential analysis. A homologous
left-minus-right value indicates amplitude asymmetry in µV at the selected
trial, time, and channel pair; it does not by itself establish source
lateralization or statistical significance. Stacking trials increases coverage
but retains participant/recording identity only as provenance metadata, not as
a statistical grouping factor. Browser memory use is higher than the earlier
single-recording version because both complete component volumes are decoded.
Browser validation used Chrome 154.0.0.0 through the Codex in-app browser. The
host-managed Playwright API does not expose its package version; this is
recorded rather than inferred. The release is not yet committed, and the saved
browser checklist does not contain per-action screenshots; these remain
explicit release/provenance risks rather than functional failures.
