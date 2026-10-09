# Log

- 2026-10-07: froze the visualization-only smoothing plan before implementation.
- Implemented an O(N) separable centered rolling mean over full embedded S/R
  arrays, with shrinking edge windows, displayed-order trial smoothing,
  debounced recomputation, and a built-in numeric canary.
- Rebuilt `docs/ride.html`; the full repository suite passed with the exact
  command `PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-eeg-smoothing python3 -m
  unittest discover -s tests -v`: 11 tests, 0 failures, 5.962 s. The suite is
  formed by `test_eeg_tfr_volume.py` (3), `test_ride_real_data.py` (3), and
  `test_ride_volume.py` (5).
- Browser validation passed for level 4, trial-order recomputation, both display
  modes, and level-0 reset; no warnings/errors were logged.
- Added visible disclosure that smoothing is display-only and can attenuate
  peaks.
- Independent review found the numerical kernel correct across 128 comparison
  cases (worst absolute Float32 difference 3.052e−05 µV) and requested
  provenance/disclosure corrections. The analysis remains on hold until those
  corrections are rebuilt and re-reviewed.
- After corrections, rebuilt `docs/ride.html` and reran the same complete suite:
  11 tests, 0 failures, 6.023 s. Configuration validation again reported
  `CONFIG VALID -- instrument chain: PASS (5 stages)`.
- Final real-browser check: Off restored S 897/897 and R 907/907 sampled X-ray
  voxels; level 2 completed at ±20 ms/±2 trials; switching to original trial
  order recomputed the smoothed view; zero browser warnings/errors. Viewer was
  returned to RT order with smoothing Off.
- Independent re-review verdict: PASS-WITH-RISKS. All six revisions and the
  numerical/artifact checks passed. Release status closed accordingly.
- Removed the channel-label provenance warning banner and its embedded warning
  text at the user's request. Rebuilt the viewer, confirmed the banner count is
  zero in the real browser, and reran the full suite: 11/11 passed in 5.807 s.
- Increased reference-overlay contrast: the stimulus plane now has a stronger
  translucent coral fill with a dark/light double outline, while the RT curtain
  uses a brighter yellow fill, highlighted front/back curves, and depth ticks.
  Real-browser visual QA passed with no warnings/errors; 11/11 tests passed in
  5.813 s.
- 2026-10-07 post-hoc X-ray amendment: inspected the S04_far threshold view and
  found the prior unsmoothed rendering visually fragmented (historical browser
  count S 897/897, R 907/907 sampled voxels). Balanced smoothing at 35% yielded
  S 125 / R 130 coherent voxels; Strong at 30% yielded S 113 / R 143 and was
  selected as the cleaner default. A trial that stacked dense smoothing with
  Strong X-ray smoothing erased the default-threshold structures, so the
  pipelines were separated: X-ray always samples unsmoothed embedded values.
- Added the four-level X-ray structure-smoothing control, 30% default threshold,
  edge-renormalized `[1,2,1]` passes, polarity-separated 6-connected cleanup,
  and a deterministic canary. Rebuilt `docs/ride.html`; the full suite passed
  11/11 in 5.853 s. Real-browser QA found S 113 / R 143 coherent voxels and
  unchanged X-ray occupancy after dense smoothing level 1. Amendment held for
  fresh independent adversarial review.
- Initial amended adversarial verdict was REVISE: numerical production checks
  reproduced S 113 / R 143, but the plan lacked the dated amendment, the
  maintained suite lacked numerical X-ray regression cases, manifest hashes
  were stale, and browser runtime identity was absent.
- Added the dated post-hoc plan amendment and a maintained Node-backed numerical
  regression test covering edge normalization, channel smoothing, the complete
  Strong pass sequence, diagonal rejection, polarity separation, exact S/R
  default occupancy, and dense/X-ray source-path separation. The expanded suite
  passed 12/12 in 6.195 s.
- Final browser rerun used Chrome/154.0.0.0 (AppleWebKit/537.36) with
  CanvasRenderingContext2D in the Codex in-app browser. It reproduced S 113 / R
  143 coherent voxels, with no browser warnings or errors. Runtime identity is
  now displayed inside the viewer's Provenance disclosure.
- Final focused independent re-review passed: 12/12 maintained tests in 6.734 s,
  exact S 113 / R 143 occupancy reproduction, numerical X-ray controls, runtime
  provenance, and dense/X-ray separation. Verdict: PASS-WITH-RISKS.
- Added a linked interactive head montage for post-hoc display-only channel
  filtering. Regions are P–O (5 channels), FC–C–CP (21), and F (2);
  hemispheres follow odd/`z`/even label suffixes. The cube uses the intersection
  while preserving source channel order, and rejects empty intersections.
- Rebuilt `docs/ride.html`; 12/12 tests passed in 6.392 s. Browser checks on
  real S04_far data confirmed 28/28 reset, posterior 5/28, posterior-left 2/28,
  and frontal-right F4 1/28 selections; both dense and X-ray modes rendered,
  the zero-channel attempt was rejected, and no warnings/errors were logged.
- Independent montage review completed at 2026-10-07T19:59:46+02:00 with
  PASS-WITH-RISKS. It measured sectors 5/21/2 and hemispheres 12/4/12, checked
  all 49 subset pairs with zero order violations, and simulated 294 toggles:
  all 84 empty outcomes were rejected with zero state mutations. Targeted
  tests passed 4/4; the five-stage instrument chain remained current.
- 2026-10-08: restored linked channel start/end sliders inside the montage-
  filtered pool. Full tests passed 12/12 in 6.757 s. Real-browser checks moved
  the window to FCz–C3, collapsed it to C3, crossed the end back to FCz without
  an invalid range, reset a posterior pool to P3–O2, then restored F3–O2. Both
  cubes redrew and the browser logged no warnings/errors.
- The initial independent channel-window review reproduced 172,550 endpoint
  transitions with zero failures but requested maintained behavioral coverage.
  Added `tests/channel_window_regression.js`, which executes the window
  functions extracted from the production template and checks inclusive
  endpoints, both crossing directions, one-channel safety, montage reset, full
  restore, labels, and dense/X-ray consumers. The complete command
  `PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-eeg-channel-scroll-final python3 -m
  unittest discover -s tests -v` passed 13/13 tests in 8.218 s.
- Independent recheck reproduced 172,550 production-template cases with zero
  failures and passed 10/10 relevant maintained tests in 6.862 s. Its interim
  verdict was REVISE for provenance closure only: add the helper to the result
  manifest, refresh changed hashes, and replace the obsolete 12/12 count.
- After provenance closure, final independent re-review matched all 18/18
  manifest entries, reproduced 172,550 endpoint transitions with zero failures
  in both template and published HTML, and passed 10/10 relevant maintained
  tests in 6.397 s. Final verdict and release status: PASS-WITH-RISKS.
