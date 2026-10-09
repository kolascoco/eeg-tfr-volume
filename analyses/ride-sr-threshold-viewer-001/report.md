# S/R threshold-volume viewer report

The public RIDE viewer now presents only the S and R clusters in synchronized
left and right boxes. The browser always retains all 137 trials. Users can
change trial order, crop the time and channel ranges from either side, stretch
the time axis, zoom the scene, and adjust the shared symmetric color limit.

The new threshold-volume view supports positive, negative, and combined
polarity. Suprathreshold rendered samples are drawn as occupancy voxels with
crisp polarity-specific outer strokes; consecutive occupied rendered bins at
the same trial and channel are joined only along the time dimension. This
produces explicit threads rather than a blur operation.
The threshold is a descriptive display cutoff relative to the selected color
limit and is not a statistical threshold.

The payload contains S and R only. Every filtered source voxel is embedded as
signed little-endian int16 with 0.01 µV per count. No amplitude clipping occurs:
the filtered extrema are −47.66 to 54.92 µV for S and −48.67 to 54.89 µV for
R. The initial shared display limit is the largest component-wise 99.5th
percentile of absolute amplitude (15.86 µV). At the default 75% threshold,
about 1.48% of full-grid voxels exceed the absolute cutoff in each component.

Limitations remain visible in the app: labels come from the owner's notebook,
finite-epoch filtering can create edge transients, and thresholded structures
should not be read as inferentially significant. Browser drawing samples up to
64 time × 36 trial × 20 channel native-grid positions for performance; this is
rendering only, not source decimation, smoothing, or interpolation. A
2,400-voxel per-component safety budget selects the largest absolute displayed
amplitudes when permissive controls would otherwise saturate the grid, and the
UI reports both displayed and eligible voxel counts. Only exposed faces of
same-polarity neighboring voxels are drawn.
