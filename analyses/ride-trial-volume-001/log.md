# Analysis log

- 2026-10-07T14:36:00+02:00 — Frozen descriptive visualization plan after user confirmed three separately named RIDE clusters.
- 2026-10-07T14:36:00+02:00 — Recorded unresolved 28-channel identity mapping; authorized only placeholder identifiers with visible warning.
- 2026-10-07T14:43:00+02:00 — Implemented loader, shared encoder, and three linked Canvas boxes for `stS`, `stC`, and `stR`.
- 2026-10-07T14:44:00+02:00 — Full repository test command passed 6/6 tests after aligning the RIDE polarity assertion with the always-visible diverging scale.
- 2026-10-07T14:44:30+02:00 — Generated `docs/ride.html` from the real MAT input; output size approximately 28 MiB.
- 2026-10-07T14:45:00+02:00 — Node parse check passed; input SHA-256 re-matched the frozen configuration; Git attributes confirmed LFS handling for the MAT input.
- 2026-10-07T14:47:36+02:00 — Targeted validation reproduced shape 147 × 28 × 1751, time -1500…2000 ms, zero index 750, RT range 306…860 ms, stable monotonic RT ordering, symmetric ±18.916752 µV scale, and 256 occupied byte values for every component.
- 2026-10-07T14:48:17+02:00 — Browser validation rendered three linked boxes, exercised plane orientation and both trial orders, and recorded zero console warnings/errors.
- 2026-10-07T14:55:00+02:00 — Data owner explicitly confirmed that the display unit is microvolts; recorded source volts ×10⁶ → µV provenance.
- 2026-10-07T14:55:30+02:00 — Added post-hoc rendering amendment and visible disclosure: full payload retained; Canvas uses deterministic native-sample decimation with no interpolation (17,244 samples, 0.239% at full bounds).
- 2026-10-07T14:56:00+02:00 — Added writer axis-length guards and real-MAT regression tests; full repository suite passed 9/9.
- 2026-10-07T14:56:14+02:00 — Regenerated viewer and revalidated in browser; unit and sampling disclosures visible, zero console warnings/errors.
- 2026-10-07T15:00:00+02:00 — Independent recheck refined renderer accounting to 17,244 draw accesses / 17,094 unique voxels (0.237%) and measured robust-scale saturation at 0.494% S, 0.500% C, 0.496% R; added both disclosures.
- 2026-10-07T15:02:08+02:00 — Final page regenerated and browser-revalidated after disclosures; instrument timestamps and result hash refreshed, with zero console warnings/errors.
- 2026-10-07T15:05:00+02:00 — Final audit found two disclosure mismatches; embedded per-component raw µV extrema in provenance and removed response-curtain decimation so every adjacent trial pair is rendered.
- 2026-10-07T15:07:02+02:00 — Regenerated and browser-validated final page: extrema present in provenance, complete RT curtain executed, 9/9 tests passed, and zero console warnings/errors.
