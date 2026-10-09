# S/R smoothing-viewer report

An optional `Time → trial smoothing` slider was added to the right control
panel. It defaults to Off. Levels 1–8 apply a centered rolling mean over
±10–80 ms within each trial and channel, followed by a centered rolling mean
over ±1–8 trials in the currently displayed trial order. Edge windows shrink
instead of padding.

The operation is display-only. The embedded signed int16 payload, MNE filter,
source data, and provenance extrema do not change. Switching trial order while
smoothing is active rebuilds the smoothed arrays. Computation is debounced and
uses rolling sums over the full S/R arrays.

The page reports the active window and computation time. It also warns that
peaks may attenuate. At level 4 on S04, computation took 176–179 ms in repeated
browser checks. With the unchanged ±15.86 µV color limit and 75% X-ray
threshold, level 4 yielded zero sampled suprathreshold voxels; users must lower
vlim/threshold when they want to inspect attenuated smoothed structures and
should compare any interpretation with Off.

This is a diagnostic visualization control. Smoothing may merge, widen,
attenuate, or change the topology of displayed structures and does not confer
statistical significance.
