# Code snapshot index

The implementation is maintained in repository source files rather than copied
into this audit directory:

- `src/ride_volume.py`: validation, MNE filtering, signed encoding, payload.
- `src/ride_viewer_template.html`: linked S/R Canvas viewer.
- `scripts/generate_ride_viewer.py`: deterministic S04 build entry point.

Exact source hashes are recorded in `../result_manifest.json` after the final
build.
