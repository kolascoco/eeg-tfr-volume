# Example EEG recording

`NS_MI_TS_raw.fif` is a publicly shared recording supplied by the repository
owner. It is tracked with Git LFS because it exceeds GitHub's 100 MiB regular
file limit.

MNE metadata audit at repository preparation time:

- 124 EEG channels
- 1,000 Hz sampling frequency
- 372.869 seconds duration
- annotations: `11/100` (40), `11/200` (30), `11/3` (80)
- no `subject_info`, experimenter, project name, measurement date, description,
  or device information recorded in `raw.info`

The absence of those fields does not guarantee irreversible anonymization.
Users should treat EEG and sensor geometry as human-participant data and
follow applicable consent, data-sharing, and citation requirements.

## RIDE example

`docs/ride-volume-S.i16.gz`, `docs/ride-volume-R.i16.gz`, and
`docs/ride-volume.json` are the compact,
presentation-ready RIDE dataset used by `docs/ride.html`. They replace three
large source MAT files and can be tracked by regular Git. The binary contains
only the filtered S and R arrays required by the viewer: 457 trials × 28
channels × 1,751 time samples, with no trial or time decimation. The JSON
manifest contains the time axis, 457 behavioral response times, channel order,
trial identities, preprocessing provenance, original source file hashes, and
binary integrity metadata. The unused C component and other MATLAB fields are
not distributed.

The original MAT files did not contain channel names. The viewer uses the
explicit ordered 28-channel list in the data owner's analysis notebook. Each
recording was independently filtered with
an MNE 0.5–20 Hz zero-phase Butterworth IIR filter with design order 4
(effective order 16 after band-pass transformation and forward–reverse
application), then trials are concatenated in S02 → S04 → S07 order. The
compact values are quantized to 0.01 µV signed-int16 counts (maximum error
0.005 µV) and gzip-compressed. Filtering finite epochs can produce boundary
transients, so the epoch edges should not be overinterpreted.

Source publication: Syrov et al. (2025), *Psychophysiology, 62*(1), e14708,
<https://doi.org/10.1111/psyp.14708>.
