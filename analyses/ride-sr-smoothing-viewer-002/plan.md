# Plan: interactive separable smoothing

## Purpose

Add optional visualization-only smoothing to the S/R trial × channel × time
viewer so transitions can be made visually continuous without changing the
embedded filtered EEG payload.

## Frozen choices

- The slider is off by default and ranges from level 0 to 8.
- Each level adds a centered time radius of 10 ms and a centered trial radius
  of one displayed trial. Level 4 therefore means ±40 ms followed by ±4 trials.
- The rolling mean is separable and ordered: centered time mean first, then
  centered trial mean, independently for every channel and component.
- Trial smoothing follows the currently displayed order (RT-sorted or original
  MAT order). Changing trial order rebuilds the smoothed display.
- Edge windows shrink to available samples/trials rather than padding.
- Smoothing affects only browser rendering. It does not alter the signed int16
  payload, MNE filtering, saved source arrays, or provenance extrema.
- Computation is debounced while dragging and cached until smoothing strength
  or trial order changes.

## Validation

1. Unit-test a reference separable rolling mean, constant preservation, impulse
   spreading, edge normalization, and slider/disclosure presence.
2. Verify the off state reproduces the unsmoothed renderer.
3. Exercise smoothing and trial-order changes on the real S04 page; check
   responsiveness and browser diagnostics.
4. Rebuild the static artifact, validate hashes/config, and obtain an
   independent adversarial review.

## Interpretation

This is a diagnostic presentation control. Smoothing can merge, widen, or
attenuate apparent structures and must not be used to claim statistical
significance or substitute for unsmoothed inspection.

## Post-hoc amendment — X-ray coherence display (2026-10-07)

After inspection of the real S04_far render, the X-ray defaults were tuned for
legibility and are explicitly selection-informed rather than pre-specified.

- X-ray smoothing has levels 0–3 and is independent of dense-view smoothing.
  It always begins from unsmoothed embedded microvolt values.
- Each pass uses an edge-renormalized separable `[1, 2, 1]` kernel. Strong
  (level 3) applies, in order: time, displayed trial, ordered channel, time,
  displayed trial. Channel adjacency means adjacency in the displayed electrode
  list, not a physical scalp-neighbor graph.
- Threshold masks are built separately for positive and negative values using
  face-only 6-connectivity. Minimum retained component sizes by level are
  1, 3, 8, and 8 sampled voxels.
- The selected defaults are Strong and 30% of the current color limit. This was
  chosen after comparing alternatives and is a diagnostic presentation default,
  not an inferential threshold.
- Numerical regression controls must cover every axis, edge renormalization,
  the full Strong sequence, diagonal rejection, polarity separation, default
  real-data occupancy, and independence from dense smoothing.

## Post-hoc amendment — scalp montage channel filtering (2026-10-07)

- Add shared channel filtering for both S and R cubes through an interactive
  head schematic.
- Sector groups are P–O (`P3`, `Pz`, `P4`, `O1`, `O2`), FC–C–CP (all recorded
  `FC*`, `C*`, and `CP*` channels), and F (`F3`, `F4`).
- Hemisphere groups use conventional label suffixes: odd numeric labels are
  left, even numeric labels are right, and `z` labels are midline.
- Multiple selections within each dimension are unions; sector and hemisphere
  dimensions are intersected. A zero-channel intersection is rejected and the
  last valid selection remains active.
- The cube channel axis is rebuilt in the original electrode-list order. This
  is a display filter only and does not change the embedded EEG payload.
- Validate all-channel reset, exact group membership, active-dot count,
  two-channel posterior-left and one-channel frontal-right rendering, empty
  selection protection, both visualization modes, and browser diagnostics.

## Post-hoc amendment — channel-range scrolling (2026-10-08)

- Keep the montage as the channel-pool selector and restore linked start/end
  sliders as an inclusive visible window within that pool.
- Moving either endpoint past the other collapses the window to the moved
  endpoint, preserving a valid one-channel cube.
- Changing the montage selection resets the visible window to all channels in
  the new pool; “All” restores the full F3-through-O2 range.
- Both dense and X-ray paths, axis labels, and occupancy calculations must use
  only the current visible window.
- Validate a multi-channel trim, a one-channel collapse, crossed endpoints,
  montage-driven range reset, all-channel restore, and browser diagnostics.
