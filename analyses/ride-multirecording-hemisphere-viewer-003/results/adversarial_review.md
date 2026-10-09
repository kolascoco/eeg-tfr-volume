# Independent adversarial review — compact RIDE transport

Reviewed at: 2026-10-09T14:47:33+02:00
Verdict: **PASS-WITH-RISKS**
Reproduction tier: independent hash check, targeted rerun, full source-to-compact numerical comparison, negative corruption control, deterministic re-encode, and live browser load/render check.

## Verdict basis

The corrected artifact chain implements the approved transport-only amendment. It publishes only S and R, retains all 457 trials × 28 channels × 1,751 samples, uses signed little-endian int16 at 0.01 µV/count, and stores one deterministic gzip asset per component. No trial or time decimation is present.

The previous REVISE findings are resolved:

- `plan.md` now records the compact split-transport amendment, quantization, omitted C component, no-decimation rule, per-file size requirement, regeneration path, and required controls.
- The encode instrument record now names the two current assets, their sizes and hashes, and a 2026-10-09T14:32:00+02:00 validation time. Transform and render references are chronologically consistent.
- All six instrument stages are `PASS`; none is `STALE`.

No inferential analysis is performed, so leakage and multiplicity are not applicable. The viewer remains diagnostic and descriptive.

## Independent measurements

- All three source MAT SHA-256 hashes match `input_manifest.json` and `config.json`.
- `docs/ride.html`: 75,349 bytes, SHA-256 `cb74cc9d528138994679cea87972ceaec1e16424e0090f51cae44a8eca1f6727`.
- S asset: 32,370,614 compressed bytes; SHA-256 `482f7400c7009dcf8978231e11ed24e86ff9eab5d0b06cffc00f5ce8a21bd804`; 44,811,592 expanded bytes; 22,405,796 int16 samples.
- R asset: 32,402,319 compressed bytes; SHA-256 `fa930222804802f8189f3931f2780156a569897b9db3bb39e45f2405fa1c000a`; 44,811,592 expanded bytes; 22,405,796 int16 samples.
- Both gzip CRC checks pass and both assets are below 50 MiB.
- Fresh per-recording 0.5–20 Hz filter and stack completed in 14.849 s; compact load completed in 0.587 s.
- Source and compact shapes are both `[457, 28, 1751]` for S and R.
- Maximum absolute source-to-compact error is 0.0050004018703475595 µV for both components. Mean absolute error is 0.002500287036254955 µV for S and 0.002499789296630322 µV for R.
- Time, response-time, and channel arrays are exactly equal. All 457 `(recording_id, original_trial)` keys are unique and the order is S02 → S04 → S07.
- Ten permitted targeted Python tests passed in 1.163 s.
- Compact load followed by split re-encoding reproduced both gzip files byte-for-byte. A same-size one-bit corruption of S was rejected with `compact S asset SHA-256 does not match the manifest`.
- A live Safari load from a localhost static server displayed `457 trials loaded`, `28 recorded channels / 12 homologous pairs`, and `1751 samples · 2 ms/sample`; both S and R canvases were visibly nonblank. The default X-ray occupancies were S 35/35 and R 36/36 coherent voxels.

## Exact commands

Run from the repository root.

```sh
shasum -a 256 \
  data/S02_far_RIDE_result.mat \
  data/S04_far_RIDE_result.mat \
  data/S07_far_RIDE_result.mat \
  docs/ride.html docs/ride-volume.json \
  docs/ride-volume-S.i16.gz docs/ride-volume-R.i16.gz \
  src/ride_volume.py src/ride_viewer_template.html \
  scripts/generate_ride_viewer.py \
  tests/test_ride_volume.py tests/test_ride_real_data.py \
  analyses/ride-multirecording-hemisphere-viewer-003/results/compact_transport_validation.json

stat -f '%N %z bytes' \
  docs/ride.html docs/ride-volume.json \
  docs/ride-volume-S.i16.gz docs/ride-volume-R.i16.gz

gzip -tv docs/ride-volume-S.i16.gz docs/ride-volume-R.i16.gz
```

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-eeg \
python3 -c $'import time\nfrom pathlib import Path\nimport numpy as np\nfrom ride_volume import load_ride_collection,load_compact_ride_dataset\nsources=[Path("data")/n for n in ("S02_far_RIDE_result.mat","S04_far_RIDE_result.mat","S07_far_RIDE_result.mat")]\nt0=time.perf_counter(); src,t,rt,ch,md=load_ride_collection(sources,l_freq=.5,h_freq=20.,iir_order=4); t1=time.perf_counter(); compact,ct,crt,cch,cmd=load_compact_ride_dataset(Path("docs/ride-volume.json")); t2=time.perf_counter()\nprint("source_load_filter_stack_s",round(t1-t0,3),"compact_load_s",round(t2-t1,3))\nprint("source_shapes",{k:list(src[k].shape) for k in ("S","R")},"compact_shapes",{k:list(compact[k].shape) for k in ("S","R")})\nfor k in ("S","R"): print(k,"max_abs_diff_uv",repr(float(np.max(np.abs(src[k].astype(np.float64)-compact[k].astype(np.float64)))*1e6)),"mean_abs_diff_uv",repr(float(np.mean(np.abs(src[k].astype(np.float64)-compact[k].astype(np.float64)))*1e6)))\nprint("times_exact",np.array_equal(t,ct),"rt_exact",np.array_equal(rt,crt),"channels_exact",list(ch)==list(cch))\nids=cmd["trial_identity"]["recording_ids"]; nums=cmd["trial_identity"]["original_1_based_mat_trial"]; keys=list(zip(ids,nums)); print("trial_keys",len(keys),"unique",len(set(keys)),"recording_order",cmd["trial_identity"]["recording_order"])'
```

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-eeg \
python3 -m unittest -v \
  tests.test_ride_volume.TestRIDEVolume.test_signed_encoding_preserves_microvolt_samples \
  tests.test_ride_volume.TestRIDEVolume.test_component_shape_mismatch_fails \
  tests.test_ride_volume.TestRIDEVolume.test_gzip_compact_round_trip_preserves_quantized_samples \
  tests.test_ride_volume.TestRIDEVolume.test_mne_bandpass_preserves_shape_and_prefers_in_band_signal \
  tests.test_ride_volume.TestRIDEVolume.test_html_has_two_boxes_trial_window_and_threshold_controls \
  tests.test_ride_volume.TestRIDEVolume.test_external_binary_encoding_and_offsets \
  tests.test_ride_volume.TestRIDEVolume.test_writer_rejects_axis_mismatch \
  tests.test_ride_real_data.TestRIDERealData.test_real_shape_time_and_response_alignment \
  tests.test_ride_real_data.TestRIDERealData.test_real_components_are_finite_and_nonconstant \
  tests.test_ride_real_data.TestRIDERealData.test_published_viewer_uses_filtered_three_recording_stack
```

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -c $'import hashlib,shutil,tempfile\nfrom pathlib import Path\nfrom ride_volume import load_compact_ride_dataset,encode_components_binary_split\nroot=Path("docs")\ncomponents,t,rt,ch,md=load_compact_ride_dataset(root/"ride-volume.json")\nwith tempfile.TemporaryDirectory() as d:\n tmp=Path(d); outputs={k:tmp/f"reencoded-{k}.i16.gz" for k in ("S","R")}; encode_components_binary_split(components,outputs,{k:outputs[k].name for k in outputs})\n for k in ("S","R"):\n  original=root/f"ride-volume-{k}.i16.gz"; print(k,"reencode_equal",original.read_bytes()==outputs[k].read_bytes(),"sha256",hashlib.sha256(outputs[k].read_bytes()).hexdigest())\n for name in ("ride-volume.json","ride-volume-S.i16.gz","ride-volume-R.i16.gz"): shutil.copyfile(root/name,tmp/name)\n p=tmp/"ride-volume-S.i16.gz"; b=bytearray(p.read_bytes()); b[len(b)//2]^=1; p.write_bytes(b)\n try: load_compact_ride_dataset(tmp/"ride-volume.json")\n except ValueError as e: print("same_size_corruption_rejected",str(e))\n else: raise SystemExit("corruption accepted")'
```

```sh
jq -n \
  --slurpfile gate analyses/ride-multirecording-hemisphere-viewer-003/gate_status.json \
  --slurpfile manifest docs/ride-volume.json \
  --slurpfile evidence analyses/ride-multirecording-hemisphere-viewer-003/results/compact_transport_validation.json \
  '{statuses:[$gate[0].instrument_status[].status],
    stages:[$gate[0].instrument_status[].stage],
    timestamps:[$gate[0].instrument_status[].validated_at],
    encode:($gate[0].instrument_status[]|select(.stage=="encode")),
    assets:$manifest[0].volume.assets,
    evidence_assets:$evidence[0].assets}'
```

Live rendering was checked with:

```sh
python3 -m http.server 8766 --bind 127.0.0.1
```

and Safari at `http://127.0.0.1:8766/ride.html`.

## Residual risks and fragility

- Fixed-point transport introduces the measured half-count-scale error. It is negligible relative to the current display range but can move values lying exactly on a display threshold.
- The most defensible change likely to weaken visual structures is a change in EEG reference or X-ray threshold/smoothing settings; homologous scalp subtraction is reference-dependent and descriptive, not source-localized lateralization.
- Finite-epoch zero-phase filtering can create boundary transients near −1.5 s and 2.0 s.
- Browser support for `DecompressionStream('gzip')` remains required. The live recheck used Safari; the recorded Chrome validation reports zero warnings/errors, but browser behavior can vary.
- The complete in-memory payload is approximately 89.6 MB before renderer workspaces; dense smoothing can allocate additional full Float32 volumes.

No flaw found invalidates the compact export. The result is sound for its stated diagnostic purpose within these limits.
