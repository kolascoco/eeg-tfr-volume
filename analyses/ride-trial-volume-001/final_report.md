# Final report — RIDE trial-volume viewer

## Result status

Descriptive/exploratory visualization only. No inferential effect, interval, or
p-value was estimated, and there is no multiplicity family.

## What ran

`data/S14_near_RIDE_result.mat` was loaded with SciPy, validated, transposed
from time × channel × trial to trial × channel × time, converted from volts to
microvolts as confirmed by the data owner, and quantized with one shared
symmetric 99.5th-percentile display range. The build generated a self-contained
`docs/ride.html` with three separately rendered, linked boxes for `stS`, `stC`,
and `stR`.

## Support and checks

- One participant/condition; 147 trials, 28 unnamed channel columns, and 1,751
  samples from −1500 to 2000 ms at 2 ms/sample.
- Behavioral RT: 147 finite values, 306–860 ms; stable ascending ordering keeps
  original trial identity.
- Shared display range: −18.916752 to +18.916752 µV.
- Full repository suite: 9 passed, 0 failed, including two real-MAT tests.
- Generated page: three canvases, valid JavaScript, linked plane/order controls,
  and zero browser console errors or warnings in the validation run.
- Every declared instrument stage is PASS with an ordered provenance chain.

## Rendering amendment and limits

The HTML payload retains all encoded voxels. For interactivity, Canvas draws a
deterministic selection of native samples from six surfaces and sparse interior:
up to 17,244 draw accesses covering 17,094 unique voxels per component at full
bounds, or 0.237% of stored voxels.
No interpolation, smoothing, or averaging is used. A localized feature between
sampled display locations can therefore be missed.

The robust shared color limit saturates 35,631 S voxels (0.494%), 36,036 C
voxels (0.500%), and 35,744 R voxels (0.496%). The viewer discloses this while
retaining all encoded values in the payload.

The file contains no channel names. `Ch01`–`Ch28` are explicit placeholders;
the 30-electrode montage reported in the paper is not guessed onto 28 columns.
Trial/RT correspondence is supported by equal index length and the exported
structure but cannot be checked against an independent trial-ID key. RT sorting
can make trends visually salient and must not be interpreted as statistical
evidence. This is a single-participant, single-condition exploratory view.

## Literature context

The page cites Ouyang et al. (2013) for RIDE and Syrov et al. (2025) for the
dataset/publication context. These citations do not change the descriptive
status of this visualization.
