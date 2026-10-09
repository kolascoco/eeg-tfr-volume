# Input audit

Status: PASS for the confirmed diagnostic visualization plan.

- Three immutable source paths were found and hashed.
- All `stS`, `stC`, and `stR` arrays are 3-D with 1,751 time samples and 28
  channels. Trial counts are 149, 137, and 171, for 457 total.
- Every file declares −1500 to 2000 ms at 2 ms/sample and therefore contains
  exactly one 0-ms sample.
- Every behavioral RT vector has the same length as its recording's trial
  axis, contains finite values, and lies inside the epoch.
- Trial identity is unique by recording ID plus original 1-based MAT trial
  number; recording IDs are derived from the three unique filenames.
- Channel labels and microvolt interpretation inherit the data owner's
  previously confirmed notebook-order and unit provenance.
- No missingness, identifier collision, time-axis mismatch, or unsupported
  channel count was found in the structural audit.
