# Adversarial review

Final verdict: **PASS-WITH-RISKS**.

The independent reviewer reproduced the raw S/C/R arrays, filtering,
quantization, and embedded browser payload. The first review requested three
revisions: distinguish Butterworth design order 4 from effective order 16,
show the finite-epoch boundary-transient warning in the public UI, and manifest
all three test files behind the 11-test claim. All three were corrected and
independently rechecked.

Verified after correction:

- S04 SHA-256, `137 × 28 × 1751` shapes, time/RT alignment, and finiteness.
- Fresh filtered/quantized arrays exactly match all embedded payload bytes.
- Visible design/effective-order and boundary-risk disclosures.
- Three nonblank, distinct canvases.
- Shared scale ±15.8588669365 µV and recorded saturation percentages.
- All freeze/result hashes match; 11 tests pass; all instrument stages PASS.
- No stale S14 or placeholder-channel claims remain.

Residual risks are the selection-informed choice of S04, external provenance
for electrodes/units, positional trial/RT alignment, and possible edge effects
from filtering finite epochs.
