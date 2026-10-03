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
follow the repository license and citation guidance.
