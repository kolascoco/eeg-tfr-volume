# Input audit

PASS for descriptive plotting with limitations.

- Four MAT files are available: S01 near (140 trials), S04 far (137), S14
  near (147), and S17 near (162).
- Every S/C/R array is finite and structurally time × channel × trial with
  1,751 time samples and 28 channels.
- Every file declares −1500…2000 ms at 2 ms/sample and carries one behavioral
  RT per trial in `latency0[2]`.
- The channel list is recovered from the analysis project and explicitly
  confirmed for use by the user. C3 is index 10.
- Source volts → display microvolts was explicitly confirmed by the data owner.
- Trial identity has no independent ID key; indexwise component/RT alignment is
  inherited from the exported RIDE structure and remains a residual risk.
