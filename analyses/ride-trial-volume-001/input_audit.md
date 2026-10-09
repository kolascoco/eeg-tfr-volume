# Input audit — S14 near RIDE result

Audit date: 2026-10-07

| Contract item | Status | Evidence |
|---|---|---|
| Source identity | PASS | `data/S14_near_RIDE_result.mat`, 169,461,081 bytes, SHA-256 `a25732b8159eaf2c6e4508be10d5bb49e02881ce4a932fe9ca371f3a7439fb5a` |
| File/schema | PASS | MATLAB v5; top-level `results` struct |
| Trial/component alignment | PASS | `stS`, `stC`, `stR`: 1751 × 28 × 147; RT length 147 |
| Trial identifiers | PASS-WITH-RISK | Original 1-based row index is the only available trial identifier |
| Time axis | PASS-WITH-RISK | `epoch_twd=[-1500,2000]`, `samp_interval=2`, 1751 samples; milliseconds inferred from configuration and paper |
| Behavioral RT | PASS | `latency0[2]`; 147 finite grid-aligned values, 306–860 ms |
| Missingness | PASS | No missing RT; all component arrays are finite |
| Channel labels | FAIL | No labels in MAT; associated paper reports 30 scalp electrodes, not a 28-column mapping |
| Amplitude unit | PASS-WITH-RISK | Unit not stored; viewer labels amplitude as “stored units” |
| Preprocessing provenance | PASS-WITH-RISK | Associated paper reports preprocessing; exact per-file history is not embedded in MAT |

The channel-label failure blocks anatomical channel claims but does not block a
clearly labeled diagnostic visualization using `Ch01`…`Ch28` placeholders.
