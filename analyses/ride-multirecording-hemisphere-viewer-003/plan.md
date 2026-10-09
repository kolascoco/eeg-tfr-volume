# Plan — multi-recording RIDE hemisphere viewer

## Status and purpose

Confirmed by the data owner on 2026-10-08. This is a diagnostic-only,
descriptive visualization extension of `ride-sr-smoothing-viewer-002`; it
does not estimate or test a population effect.

## Data and unit of display

- Stack every trial from `S02_far_RIDE_result.mat`,
  `S04_far_RIDE_result.mat`, and `S07_far_RIDE_result.mat`.
- A unique trial key is `(recording_id, original_1_based_trial_number)`.
- Preserve the common 28-channel notebook order and the common −1500 to
  2000 ms, 2 ms/sample time axis.
- Original order is recording order S02 → S04 → S07, then original MAT trial
  order. The alternative display order is a global stable ascending RT sort.
- Display only the RIDE S and R component clusters.

## Preprocessing and transforms

- Apply MNE-Python `filter_data` independently to each recording and component:
  0.5–20 Hz, Butterworth IIR design order 4, SOS, zero phase,
  `reflect_limited` padding. Do not baseline, resample, decimate, interpolate,
  average, or normalize between recordings.
- Concatenate only after each recording is filtered.
- Recorded-channel view retains the sector and independently selectable left,
  midline, and right montage controls.
- Bilateral view computes exact sample-wise homologous differences after
  filtering: left − right by default, with right − left available. Pairs are
  F3/F4, FC5/FC6, FC3/FC4, FC1/FC2, C5/C6, C3/C4, C1/C2, CP5/CP6,
  CP3/CP4, CP1/CP2, P3/P4, and O1/O2. Midline channels are excluded.
- Channel start/end sliders remain an inclusive visible window after either
  recorded-channel filtering or bilateral pair construction.

## Outputs and controls

- Regenerate `docs/ride.html` and an external signed-int16 little-endian
  binary asset so the stacked viewer remains deployable with GitHub Pages.
- Store recording ID and original trial number for every displayed trial in
  the payload metadata.
- Add structural alignment, unique-key, subtraction-sign, one-channel,
  montage, stacked-shape, external-asset, nonblank-render, and provenance
  checks.
- Keep all display smoothing off by default. Threshold structures and
  hemispheric differences are descriptive, not statistical significance.

## Compute and interpretation limits

One local end-to-end build is expected to complete in minutes, not hours.
The much larger stack increases download and browser memory cost. Dense
smoothing can allocate multiple full Float32 volumes and remains optional.
List-order channel adjacency is not physical scalp adjacency. A left−right
difference depends on the inherited reference and is not source-localized
lateralization.

## Post-hoc implementation amendment — 2026-10-08

This amendment changes presentation state only; it does not change the sample,
filtering, component values, homologous pairs, subtraction sign, or scientific
interpretation.

- Keep the region buttons as an inclusive multi-select filter. Reject an
  attempted empty selection and preserve the last valid region set.
- In bilateral representations, map every selected pair to both of its raw
  electrodes; hemisphere buttons remain disabled because both sides are
  required for a difference.
- Distinguish the selected region pool from the channel-slider window. Dimly
  mark electrodes in the pool, strongly highlight only electrodes feeding the
  currently visible pair window, and print the visible pair labels below the
  montage.
- Recompute montage highlighting on every channel-start or channel-end input.
- Regression-test every non-empty region subset in left−right and right−left
  modes, empty-selection protection, representation switching, and all
  inclusive slider windows.

## Post-hoc layout amendment — 2026-10-08

This amendment changes document layout only. The data, preprocessing,
subtraction, rendering algorithms, defaults, and interpretation are unchanged.

- Place the two S/R viewports across the full page width before every control.
- Move all selectors, sliders, montage controls, checkboxes, and orientation
  buttons below the viewports.
- Arrange controls as responsive horizontal cards: multiple columns when
  space permits and one column on narrow screens. Do not restore a sidebar.
- Keep every existing control ID and event path so scientific behavior remains
  covered by the established regression suite.
- Move references below the controls and retain provenance notes.

## Post-hoc trial-window amendment — 2026-10-08

This amendment changes the displayed trial subset only. The complete 457-trial
payload, preprocessing, trial ordering definitions, component values, and
scientific interpretation are unchanged.

- Add linked inclusive trial-start and trial-end rank sliders, initialized to
  all trials.
- Interpret ranks within the currently selected RT-sorted or recording order.
- Apply the trial bounds to dense faces/interior points, X-ray sampling, trial
  axis labels, and the response-time curtain.
- Permit a single-trial window and guard X-ray coordinates and the response
  marker against zero trial span.
- Preserve the selected rank bounds when switching trial order.
- Regression-test inclusive and crossing behavior, full/trimmed/single windows,
  every rendering consumer, and real-browser interaction.

## Compact transport amendment — 2026-10-09

This owner-requested amendment changes repository packaging and browser
transport only. It does not change filtering, trials, channels, time sampling,
component values beyond the viewer's existing fixed-point representation, or
scientific interpretation.

- Distribute only the S and R components used by the app; omit C and unrelated
  MATLAB fields.
- Retain all 457 trials, 28 channels, and 1,751 time samples without trial or
  time decimation.
- Store amplitudes as signed little-endian int16 counts at 0.01 µV/count. The
  maximum rounding error is one half count (0.005 µV, apart from floating-point
  representation at the boundary).
- Gzip S and R into separate files, each below GitHub's 50 MiB warning
  threshold, and decompress them in the browser before rendering.
- Store dimensions, scale, axes, response times, channel order, trial identity,
  original source hashes, preprocessing provenance, asset sizes, and asset
  hashes in `docs/ride-volume.json`.
- Permit regeneration from the compact manifest and assets after the original
  MAT files are removed.
- Validate source-to-compact error, deterministic re-encoding, gzip integrity,
  same-size corruption rejection, full sample counts, automated regressions,
  and live browser rendering.
