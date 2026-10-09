# Independent adversarial review

Verdict: **PASS-WITH-RISKS**

Final independent recheck confirmed:

- the raw MAT SHA-256 is
  `a25732b8159eaf2c6e4508be10d5bb49e02881ce4a932fe9ca371f3a7439fb5a`;
- the generated viewer SHA-256 is
  `a07c0e65dd715b899d2165370783727372909c0149dbc6e18fabf5dd72cb004a`;
- the full repository suite passes 9/9 tests;
- the payload reproduces from the source components, contains component extrema,
  and uses the expected 147 × 28 × 1751 dimensions;
- the response-time curtain covers every adjacent trial pair;
- loader → encoder → browser-renderer validation timestamps are ordered.

Residual risks are disclosed: the 28 columns have no names; the exploratory
Canvas view deterministically decimates display samples; the robust scale
saturates approximately 0.5% of values; and the browser engine/version is not
recorded. These limits do not invalidate the descriptive viewer but prohibit
inferential or anatomical interpretation.

Reproduction commands used by the reviewer:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
shasum -a 256 data/S14_near_RIDE_result.mat docs/ride.html
stat -f '%N %z bytes mtime=%Sm' -t '%Y-%m-%dT%H:%M:%S%z' \
  docs/ride.html \
  analyses/ride-trial-volume-001/results/validation_summary.json \
  analyses/ride-trial-volume-001/gate_status.json
```
