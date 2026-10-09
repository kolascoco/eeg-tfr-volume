# Independent adversarial review

## Initial verdict: REVISE

The independent reviewer confirmed correct S/R payload selection, dimensions,
int16 reconstruction, no clipping, filtering metadata, axes, and fixed trial
count. Required revisions were:

1. Replace sampled dot glyphs with volumetric occupancy cells and distinguish
   rendered-bin adjacency from native-sample adjacency.
2. Correct painter ordering to draw far geometry before near geometry.
3. Prevent the color slider from quantizing 15.86 µV to 15.75 µV.
4. Complete the analysis artifact chain and strengthen tests.

All four items were addressed. A second review found a pathological low-cutoff
rendering cost and an incomplete formal instrument schema. The renderer now
uses a disclosed 2,400-voxel per-component safety budget, strongest-amplitude
selection, exposed-face culling, and a live shown/eligible count. The formal
load → filter → encode → render chain now passes the canonical schema and file
validator.

## Final verdict: PASS-WITH-RISKS

The independent reviewer verified the generated artifact hash, all manifested
source hashes, all 11 tests, the four-stage PASS instrument chain, S/R-only
payload, fixed trial count, axis mapping, filtering, encoding, painter order,
controls, occupancy voxels, outlines, threads, and low-threshold safety cap.

Residual risks:

- When the safety cap activates, weaker eligible voxels are omitted, which can
  change apparent topology and sever weaker temporal threads.
- Browser rendering samples the native payload grid rather than drawing all
  6.7 million voxels per component simultaneously.
- Channel labels are externally supplied from the owner's notebook.
- Finite-epoch filtering can create boundary transients.
- Browser interaction checks are manual rather than automated canvas E2E tests.
