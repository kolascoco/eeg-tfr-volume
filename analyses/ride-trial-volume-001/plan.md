# RIDE trial-volume viewer plan

Status: frozen for exploratory visualization on 2026-10-07.

## Purpose

Build a descriptive, interactive visualization of the three single-trial RIDE
component clusters in `data/S14_near_RIDE_result.mat`. This is not an
inferential analysis and makes no statistical claim.

## Data and axes

- Unit: one retained near-condition trial from participant S14.
- Volume axes: trial × channel × stimulus-relative time.
- Trial count: 147; channel count: 28; sample count: 1751.
- Time: inferred from the RIDE configuration as -1500 to 2000 ms at 2 ms/sample.
- Behavioral response time: `results.latency0[2]`, 306–860 ms, one value per trial.
- Default trial order: behavioral response time ascending; original order remains available.
- Original trial index is retained after sorting.

## Three displayed volumes

1. `stS`: stimulus-locked component cluster (S component).
2. `stC`: non-marker-locked component cluster (C component).
3. `stR`: response-locked component cluster (R component).

No component summation, filtering, baseline correction, interpolation, or
resampling will be applied. Values are displayed as stored. All three volumes
use one shared symmetric robust color limit: the largest component-specific
99.5th percentile of absolute amplitude.

## Timing overlays

- A stimulus-onset plane marks 0 ms in every volume.
- A response-time curtain connects each trial's behavioral RT through the
  channel dimension in every volume.
- The response time is behavioral RT, not RIDE's `latency_r` shift.

## Channel identity limitation

The MAT file has 28 channels but no labels. The associated paper documents a
30-electrode acquisition montage, which cannot be mapped bijectively to these
28 columns. The viewer therefore uses `Ch01`…`Ch28` and shows a visible warning.
The labels will be replaced only when an ordered 28-label source is supplied.

## Interaction

- Three synchronized 3-D boxes with linked camera rotation and zoom.
- Shared time, trial, and channel limits.
- RT-sorted/original trial-order selector.
- Trial selection reports sorted rank, original trial index, and RT.
- Plane-orientation buttons and stimulus/response overlays.
- Native voxel rendering only; cross-trial interpolation is prohibited.

## Post-hoc rendering amendment — 2026-10-07

The phrase “native voxel rendering only” above is narrowed after implementation
review. The self-contained browser page stores every encoded voxel, but Canvas
rendering deterministically selects native samples from the six boundary
surfaces and sparse interior. At full bounds it makes at most 17,244 draw
accesses covering 17,094 unique voxels per component (0.237% of 7,207,116
stored voxels). It does not
interpolate, average, or smooth across time, channels, or trials. This sampling
density is disclosed in the UI. The viewer is therefore an exploratory overview,
not a guarantee that every localized structure is visible.

## Outputs

- Reproducible MAT loader and payload encoder.
- Three-box HTML viewer template.
- `docs/ride.html` public demonstration page.
- Automated schema, alignment, encoding, and HTML tests.
- README links and both requested literature references.

## Controls and interpretation limits

- Positive: each encoded component is nonconstant and renders nonblank.
- Negative: malformed RT length or missing component fails loudly.
- Boundary: 0 ms and all RT values must fall on or within the time axis.
- Identity: sorted RT and component data must use the same permutation.
- Provenance: input SHA-256 and software versions are embedded.
- Interpretation: descriptive/exploratory visualization only; apparent
  structures are not statistical effects, and channel anatomy is unavailable.
