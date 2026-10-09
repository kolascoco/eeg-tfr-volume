# Final report — amended X-ray rendering

## Outcome

The S/R single-trial volume viewer now uses separate display pipelines for the
dense and X-ray views. Dense mode retains its optional centered time-then-trial
rolling mean. Level 0 is the exact unsmoothed embedded signal; levels 1–8 use
±10–80 ms of time followed by ±1–8 displayed trials, independently within each
channel.

The X-ray view now defaults to Strong structure smoothing and a 30% threshold.
It samples the unsmoothed embedded values, applies an edge-renormalized
separable `[1, 2, 1]` kernel over time, displayed trials, and ordered channels,
repeats the time and trial passes at Strong, and removes same-polarity
6-connected components smaller than eight sampled voxels. Positive and
negative structures are cleaned separately. None of these controls changes the
MAT source, MNE filtering, or embedded signed-int16 payload.

Both cubes now share an interactive scalp montage. Users select P–O,
FC–C–CP, and/or F sectors and intersect them with left, midline, and/or right
hemisphere groups. The channel axis is rebuilt from matching electrodes in the
original list order; empty intersections are rejected without changing the
last valid selection.

Linked channel-start and channel-end sliders retain channel scrolling within
the montage-filtered pool. They form an inclusive visible window, may collapse
to one channel, and reset to the full matching range whenever the montage
selection changes.

## Validation

- The existing dense smoothing canary and a new X-ray kernel/connectivity
  canary both pass on page load.
- The complete repository suite passed 13/13 tests after the final rebuild.
  The added Node-backed regression executes the channel-window functions
  extracted from the production template across 172,550 endpoint transitions;
  it found zero failures and verifies both renderers consume the visible slice.
- In the real in-app browser, the selected Strong/30% X-ray default retained
  S 113/113 and R 143/143 coherent sampled voxels. The historical unsmoothed
  view had shown S 897/897 and R 907/907 sampled voxels.
- Switching dense smoothing to level 1 did not change the X-ray occupancy,
  confirming that the two display pipelines are independent. Both canvases
  remained nonblank.
- Real-browser montage checks reproduced 28 all channels, 5 posterior channels,
  2 posterior-left channels, and the single frontal-right channel F4. Dense and
  X-ray rendering both remained nonblank and the browser logged no errors.
- Independent selector enumeration covered all 49 sector/hemisphere subset
  pairs with zero source-order violations. Across 294 simulated toggle
  transitions, all 84 empty results were rejected without mutating selection
  state; the targeted independent suite passed 4/4 checks.
- Browser checks trimmed the full pool to FCz–C3, collapsed to C3, handled a
  crossed endpoint by preserving FCz alone, reset the posterior pool to P3–O2,
  and restored the full F3–O2 range without console errors.

## Interpretation and residual risks

All smoothing and connected-component cleanup are descriptive display
processing, not inferential preprocessing or statistical cluster detection.
The X-ray defaults were selected after inspecting this recording and are
therefore selection-informed. Strong smoothing can merge nearby structures,
and the eight-voxel cleanup can remove small genuine effects; users should
compare Strong with Balanced or Off.

Final independent re-review matched all 18 pre-review manifest entries,
reproduced 172,550 valid channel-window transitions with zero failures in both
the source template and published HTML, and returned PASS-WITH-RISKS.

Dense smoothing still allocates full-size Float32 buffers. For the bundled
137 × 28 × 1,751 example, steady-state array-buffer use is about 77 MiB and can
transiently approach 154 MiB during recomputation. Keeping dense smoothing Off
avoids those additional buffers. The final independent amended verdict is
PASS-WITH-RISKS; the residual risks are the selection-informed defaults,
list-order rather than physical-neighbor channel adjacency, the coarse
sector/hemisphere grouping, conventional-label assumptions and fallback for
unknown labels, threshold
sensitivity, and the browser memory cost of optional dense smoothing.
