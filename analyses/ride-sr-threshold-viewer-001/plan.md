# Plan

Create a reproducible static S/R RIDE viewer from the S04 far-condition MAT
file. Filter each trial/channel time course with the declared MNE 0.5–20 Hz
zero-phase IIR pipeline, preserve every filtered sample in a signed microvolt
payload, and render two linked trial × channel × time boxes.

Acceptance criteria:

1. Only S and R are embedded and displayed side by side.
2. All 137 trials remain fixed; RT sorting may reorder but not exclude them.
3. Users can crop time/channels, stretch time, zoom, and set symmetric color
   limits.
4. Dense mode is a closed opaque six-face volume.
5. Threshold mode supports positive, negative, and both-polarity occupancy
   voxels, crisp outer strokes, and explicit temporal links without blur.
6. Sampling used only for browser drawing is disclosed and cannot be confused
   with preprocessing or source decimation.
7. Automated tests, browser inspection, and independent adversarial review
   pass before delivery.
