# Verification record

- `PYTHONPATH=src /usr/local/bin/python3 -m unittest discover -s tests -v`
- `git diff --check`
- Local browser load at `http://127.0.0.1:8766/ride.html`
- Threshold and dense modes visually inspected.
- Negative-only polarity, time-start crop, and channel-start crop exercised.
- Browser console checked for warnings/errors.
- Worst-case browser stress check at ±0.50 µV and 5% threshold: S displayed
  2,400/45,214 eligible voxels, R displayed 2,400/45,241; the safety-cap notice
  appeared, dense/threshold switching remained responsive (95 ms measured for
  the paired control operation), and no browser warnings/errors were logged.
- The canonical config validator passed with `--check-files` and reported a
  four-stage PASS instrument chain.

Repository tests assert S/R-only signed encoding, reconstruction error,
real-data dimensions/timing/filter metadata, absence of trial-count controls,
presence of the requested controls, far-to-near painter ordering, occupancy
voxel rendering, crisp outline implementation, and disclosure language.
