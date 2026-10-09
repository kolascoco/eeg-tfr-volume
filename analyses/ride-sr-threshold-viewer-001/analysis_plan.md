# Analysis plan: S/R threshold-volume viewer

## Objective

Publish the filtered S04 RIDE demonstration as two synchronized, side-by-side
trial × channel × time volumes: the stimulus-locked S cluster and the
response-locked R cluster. All 137 trials remain visible; the interactive
controls crop only time and channels, stretch time, change the camera, and
adjust the diverging color scale.

## Data contract

- Source: `data/S04_far_RIDE_result.mat` (`results.stS`, `results.stR`).
- Source layout: time × channel × trial; viewer layout: trial × channel × time.
- Amplitude: volts in the MAT arrays, converted to microvolts for the browser.
- Time and response latency: milliseconds.
- Channels: the ordered 28-label list recovered from the data owner's analysis
  notebook; the MAT file itself does not carry channel names.
- Processing: MNE 0.5–20 Hz zero-phase Butterworth IIR, design order 4;
  no baseline correction, resampling, interpolation, or source-data decimation.

## Visualization contract

- Dense mode: closed six-face volume plus a sparse interior sample.
- Threshold-volume mode: signed positive, negative, or both-polarity structures
  over an adjustable absolute threshold, with projected outlines and temporal
  threads connecting adjacent suprathreshold samples.
- Thresholding is a visualization operation, not inferential statistics.
- Rendering may sample the native grid for browser performance; embedded data
  retain every source sample.
- Color limits are adjustable in microvolts. Payload encoding must retain values
  beyond the initial robust display range without clipping.

## Checks

1. Unit tests validate S/R-only payloads, loss-bounded signed encoding, axis
   validation, controls, and threshold-volume features.
2. Real-data tests validate shape, timing, filtering, components, and payload
   byte size.
3. The generated HTML is opened locally and visually inspected.
4. An independent adversarial review checks scientific and implementation
   validity before handoff.
