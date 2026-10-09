# Input audit

- The source contains finite `results.stS`, `results.stC`, and `results.stR`
  arrays with identical source shape 1,751 time × 28 channel × 137 trial.
- The viewer consumes only stS and stR after transposition to
  137 trial × 28 channel × 1,751 time.
- The configured time vector is −1,500 to 2,000 ms in 2 ms steps and contains
  exactly one zero sample at index 750.
- The 137 response latencies are finite, span 492–1,000 ms, and lie inside the
  epoch.
- Channel labels are external to the MAT and follow the explicit notebook list;
  this limitation is displayed in the UI.
- The data owner confirmed the source amplitudes are volts; conversion to µV is
  `source × 1e6`.
