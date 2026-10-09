# Analysis log

- 2026-10-08: data owner requested stacking the three far-condition recordings,
  split hemisphere montage picking, homologous hemisphere subtraction, and
  retention of channel scrolling. Structural audit passed and shared
  understanding was explicitly confirmed before signal outcome inspection.
- 2026-10-08: implemented collection loading with independent 0.5–20 Hz MNE
  filtering and concatenation in S02, S04, S07 order. Validation collection
  runtime was 14.792 s; result shape was 457 × 28 × 1,751 with 457 unique
  `(recording_id, original_trial)` keys.
- 2026-10-08: generated `docs/ride.html` and external little-endian int16 asset
  `docs/ride-volume.i16`. End-to-end generation runtime was 16.79 s. The asset
  is 89,623,184 bytes and contains S followed by R.
- 2026-10-08: added split left/midline/right montage selection, recorded,
  left-minus-right, and right-minus-left representations, and preserved channel
  range scrolling for recorded channels and homologous pairs.
- 2026-10-08: `PYTHONPATH=src python3 -m unittest discover -s tests -v` passed
  15/15 tests in 15.289 s. Production-JavaScript X-ray measurement returned S
  17 positive + 18 negative and R 16 positive + 20 negative coherent voxels at
  defaults. Independent 6-neighbor recount found three components in each cube.
- 2026-10-08: local browser QA passed at `http://127.0.0.1:8766/ride.html`:
  457 trials, 28 recorded channels, 12 bilateral pairs, independent hemisphere
  toggles in recorded mode, channel scrolling, both subtraction directions,
  and zero console warnings/errors.
- 2026-10-08: independent adversarial review requested; release remains HOLD
  until its canonical verdict is recorded.
- 2026-10-08: instrumented validation run measured load 3.353189 s, filter
  10.952014 s, stack 0.087563 s, external encode 1.139027 s, and HTML/binary
  render 1.151672 s. Production hemisphere-transform regression took 0.13 s.
- 2026-10-08: first adversarial review verdict REVISE. Corrected X-ray count
  terminology, test environment, validation hashes/runtime provenance, and the
  favicon request. Browser automation uses Chrome 154.0.0.0; its host-managed
  Playwright package version is not exposed.
- 2026-10-08: independent correction recheck returned PASS-WITH-RISKS. All
  requested behaviors and validation claims passed. Publication remains HOLD
  only because the generated files and LFS objects are not yet committed and
  pushed; publishing was intentionally left to the user.
- 2026-10-08: data owner requested post-hoc montage interaction repair. Live
  reproduction showed channel sliders changed the cube endpoints but did not
  change head-map highlights: a C3−C4-only window still highlighted all 24
  electrodes belonging to the 12-pair pool. Region filtering itself returned
  correct bilateral subsets and protected the last non-empty selection.
- 2026-10-08: separated selected-pool and visible-window montage state. Gold
  markers now identify only electrodes feeding the cube; dim teal markers show
  the wider selected pool. A visible pair/channel summary and labels for up to
  four visible entries were added. Channel slider input now synchronizes the
  montage before redrawing.
- 2026-10-08: an attempted run with the repository `.venv` failed before
  output generation because that environment lacks NumPy and MNE. Re-running
  with the previously validated system Python environment succeeded; no
  fallback analysis method was used.
- 2026-10-08: real-data viewer rebuilt in 16.99 s. The full command
  `PYTHONPATH=src python3 -m unittest discover -s tests -v` passed 16/16 tests
  in 16.586 s. Focused production-JavaScript checks covered 14 bilateral
  region states, 508 bilateral slider windows, 49 recorded-mode selection
  states, empty-selection protection, and both subtraction directions.
- 2026-10-08: final browser QA on Chrome 154 exercised central-only selection,
  C3−C4 and C4−C3 single-pair windows, group reset after representation
  changes, gold C3/C4 markers and labels, and zero warning/error messages.
- 2026-10-08T22:34:30+02:00: fresh-context adversarial review completed
  with PASS-WITH-RISKS. The reviewer independently reran 16/16 tests, 508
  bilateral montage windows, 172,550 scrolling transitions, all 12 pair
  mappings in both directions, live Chrome interaction checks, manifest
  hashes, and the six-stage instrument validator. Release remains HOLD pending
  user commit/push and Git LFS publication.
- 2026-10-08T22:51:45+02:00: implemented the user-requested layout-only
  amendment. Both canvases precede a responsive horizontal control-card grid;
  references follow the controls. Regenerated the published HTML and unchanged
  binary payload. Full suite passed 16/16 in 16.174 s; focused montage,
  scrolling, and subtraction regressions passed. Chrome measured controls below
  the canvases with two columns at 774 px and zero console messages. Independent
  review reopened; release remains HOLD.
- 2026-10-08: fresh-context layout review returned REVISE solely because
  `final_report.md` retained the pre-amendment HTML size/hash. Corrected it to
  the freshly measured 72,773 bytes and
  `baa8545fa3af9be9141a200bb10ce3c2193f4c8b3958f6c762e659af01709847`;
  implementation and browser checks required no change. Re-review requested.
- 2026-10-08: corrected-artifact re-review returned PASS-WITH-RISKS. Fresh
  full suite passed 16/16 in 16.177 s; 17/17 manifest hashes matched; the
  six-stage chain was current and ordered. Release remains HOLD pending user
  commit/push and Git LFS publication.
- 2026-10-08T23:19:20+02:00: implemented inclusive trial-rank scrolling in
  both directions. All 457 trials remain loaded; dense, X-ray, axes, and RT
  curtain consume the visible rank bounds. Added single-trial guards and a
  production-JavaScript regression covering 313,959 cases. Full suite passed
  17/17 in 15.674 s. Browser checked 101–221, crossing to rank 301, order
  switching, full restoration, nonblank canvases, and zero console messages.
  Independent review reopened; release remains HOLD.
- 2026-10-08: independent trial-window review returned PASS-WITH-RISKS. Fresh
  suite passed 17/17 in 16.130 s; trial regression passed 313,959 cases against
  template and published HTML; live Chrome verified default, trimmed, both
  crossing directions, order remapping, dense/X-ray/RT-curtain pixel changes,
  and no errors. All 18 manifest entries and six instrument stages passed.
- 2026-10-09: replaced the three distributable RIDE MAT files and uncompressed
  viewer asset with separate `docs/ride-volume-{S,R}.i16.gz` files plus
  `docs/ride-volume.json`; each binary stays below GitHub's 50 MiB warning.
  The compact dataset retains every S/R trial, channel, and time sample at
  0.01 µV/count, omits C and unused MATLAB fields, and stores original source
  hashes in the manifest. Real-data equivalence was within 0.0050004 µV; time,
  response-time, and channel arrays were exact. The final split-asset suite
  passed 18/18 in 2.667 s. Chrome decoded 22,405,796 samples per component, rendered both
  canvases, and emitted zero warnings/errors. RIDE data no longer require LFS.
- 2026-10-09T14:47:33+02:00: independent compact-transport recheck returned
  PASS-WITH-RISKS after fresh source filtering/stacking, exact axis and trial
  checks, deterministic byte-for-byte re-encoding, a one-bit corruption
  control, ten targeted tests, six-stage instrument validation, and live Safari
  rendering of both split assets.
