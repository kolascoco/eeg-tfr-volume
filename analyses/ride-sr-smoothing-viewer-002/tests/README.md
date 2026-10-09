# Tests

- All 11 repository tests passed.
- The production JavaScript runs a known 3 × 1 × 3 kernel canary at page load;
  it checks time-first/trial-second centered means, edge normalization, and a
  non-unit amplitude scale.
- Level 4 on real S04 displayed `±40 ms → ±4 trials` and completed in 176–179
  ms in repeated checks.
- Switching from RT order to original order recomputed level 4 in 189 ms.
- Dense and threshold modes rendered without browser warnings/errors.
- Returning the slider to level 0 restored `Off · unsmoothed embedded samples`
  and the original S 897/897, R 907/907 sampled X-ray occupancy.
- Level 4 at the unchanged ±15.86 µV color limit and 75% threshold produced no
  suprathreshold sampled voxels; this confirms meaningful peak attenuation and
  motivates the visible warning to compare with Off and lower vlim/threshold
  when appropriate.
