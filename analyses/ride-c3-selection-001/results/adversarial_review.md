# Adversarial review

## Initial verdict: BLOCK

The independent reviewer exactly reproduced all numerical results, ranking,
shared scale, MNE/raw equivalence, shapes, timing, RT sorting, hashes, and
figure integrity. It blocked release because (1) labels and units are not
embedded in the MAT files, (2) the untracked specification could not support
an independently auditable pre-declaration claim, and (3) the instrument-chain
records did not conform to the required schema.

## Resolution

- The report now identifies the work as retrospective, selection-informed
  exploration rather than a preregistration or independently pre-declared run.
- Exact notebook paths and cells now document the user-directed electrode
  order, use of `raw_eps.ch_names`, C3 selection, MNE representation, and
  `× 1e6` display conversion. The external-provenance limitation remains
  explicit because the MAT files are not self-describing.
- `config.json` now contains the required sources, decisions, compute gates,
  outputs, interpretation, instrument chain, and family fields.
- Each PASS instrument record now includes a timestamp, runtime, output shape,
  and timestamped upstream reference. The official schema validator reports:
  `CONFIG VALID -- instrument chain: PASS (3 stages)`.
- The raw analysis, plots, metrics, and S14 > S17 > S04 > S01 ranking were not
  changed.

## Final verdict: PASS-WITH-RISKS

The reviewer verified all corrections, the official config/instrument-chain
validation, current specification hashes, and unchanged numerical artifacts.
No blocking or revision-level inconsistency remains. Residual risks are the
retrospective design, external notebook/user provenance for electrode identity
and µV units, trial alignment inherited by index, and subject–condition
confounding because only one far recording is available.
