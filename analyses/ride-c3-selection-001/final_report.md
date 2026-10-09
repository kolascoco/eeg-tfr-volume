# C3 RIDE recording comparison

## Outcome

Under the frozen descriptive rule, **S14_near** is the most pronounced C3
recording. Its recording-level score is 18.9179 µV, followed by S17_near at
16.6188 µV, S04_far at 13.1178 µV, and S01_near at 11.2643 µV. The score is
the largest component-wise 99th percentile of absolute single-trial C3
amplitude.

The waveform panel also supports S14_near as a useful demonstration recording:
its C and R component averages have comparatively large, structured deflections.
S17_near has the largest negative S-component mean deflection near 150 ms, so
S17 remains a defensible alternative if the S component is the sole priority.

## Data handling

All 28 channels, every trial, and all 1,751 samples from -1500 to 2000 ms were
passed into MNE at 500 Hz. C3 was selected by name at zero-based index 10. No
filter, baseline, resampling, smoothing, interpolation, or decimation was
applied. Trial heatmaps use stable behavioral-RT ordering and display the RT
curve without changing the data.

The RIDE MAT files do not contain channel labels or unit metadata. The channel
mapping follows the explicit 28-electrode order in the user's analysis notebook
and their instruction to use those electrodes. The volts-to-µV conversion
follows their MNE notebook code (`× 1e6`) and their explicit confirmation that
the displayed unit is microvolts.

## Scope and limitations

This is a selection-informed exploratory comparison intended to choose a
demonstration file, not a population or condition analysis. Only one far file
is available, so subject and condition cannot be separated. The robust
amplitude score measures visual prominence, not signal quality, component
validity, or statistical significance. Although the user approved the plotting
plan before execution, its state was not committed beforehand, so this analysis
is not described as preregistered or independently pre-declared.
