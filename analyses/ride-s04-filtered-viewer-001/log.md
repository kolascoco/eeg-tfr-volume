# Analysis log

- 2026-10-07 — Data owner selected S04_far as the cleanest recording and explicitly requested MNE 0.5–20 Hz filtering for presentation.
- 2026-10-07 — Specification frozen before rebuilding the viewer. Fourth-order zero-phase Butterworth IIR selected as the documented implementation default to avoid a low-cutoff FIR kernel longer than the epoch.
- 2026-10-07T16:06:10+02:00 — Rebuilt `docs/ride.html` from filtered S04 data.
- 2026-10-07T16:08:00+02:00 — Browser inspection confirmed S04 title, 137 trials, named electrodes, filter disclosure, three rendered boxes, controls, scale, and citations.
- 2026-10-07T16:15:00+02:00 — Full repository suite passed: 11 tests, 0 failures.
- 2026-10-07T16:17:39+02:00 — Sequential real-data chain revalidation passed and fresh encoded bytes exactly matched the published payload.
- 2026-10-07 — Adversarial review returned REVISE: clarify design/effective filter order, expose boundary-transient risk in the UI, and manifest the full test suite. These documentation/provenance changes do not alter the filtered arrays.
- 2026-10-07T16:29:24+02:00 — Rebuilt and revalidated the complete chain after the disclosure fixes; 11 tests passed and the fresh payload again matched byte-for-byte.
- 2026-10-07 — Independent re-audit returned PASS-WITH-RISKS; no blocking or revision-level finding remains.
