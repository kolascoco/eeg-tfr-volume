# Final independent adversarial closure review — channel-range scrolling

## Verdict: PASS-WITH-RISKS

The channel-range scrolling amendment is sound within its stated diagnostic,
browser-only scope. The maintained regression executes the production
JavaScript and passed from both the source template and published HTML. Before
this review was overwritten, every one of the 18 manifest-listed artifacts
matched its recorded SHA-256, including the previous canonical review, and the
primary artifact also matched its recorded byte count.

The only remaining bookkeeping action is the agreed post-write refresh of this
review's hash in `result_manifest.json`, followed by the normal gate/release
update. That expected self-hash change is not a substantive review finding.

## Independent measurements and controls

- **Endpoint state space:** PASS. Each production source completed 172,550
  endpoint transitions over every valid initial interval, every moved endpoint,
  and pool sizes 1–28, with zero failures.
- **Inclusive window:** PASS. Indices 5–10 returned six channels:
  `[5,6,7,8,9,10]`.
- **Crossing in both directions:** PASS. Moving the start beyond the end and
  moving the end below the start both collapse to the moved endpoint.
- **One-channel safety:** PASS. The collapse measurement returned `[10]`; dense
  and X-ray production paths contain their one-channel geometry guards.
- **Montage reset:** PASS. A five-channel pool reset to all
  `[23,24,25,26,27]`.
- **Full restore:** PASS. The all-channel pool returned first index 0, last 27,
  and length 28.
- **Axes, labels, occupancy, and consumers:** PASS. The executed source audit
  found one `displayChannels()` consumer in each of the axes, dense, X-ray, and
  text paths; displayed endpoint labels use the same slice. X-ray sampling,
  smoothing, connectivity, occupancy, faces, and safety-cap counts therefore
  operate on the visible window.
- **Published artifact identity:** PASS. `docs/ride.html` is exactly the current
  template with its 35,839,084-character payload substituted.
- **Relevant maintained suite:** PASS, 10/10 in 6.397 s. This includes the
  production window regression, real-data load/filter/shape checks, encoding,
  X-ray numerical regression, and writer boundary checks. The frozen log and
  final report additionally record the complete repository suite as 13/13 in
  8.218 s.
- **Manifest:** PASS before overwrite, 18/18 entries with zero mismatches.
- **Instrument chain:** PASS. Five declared and observed stages agree in order
  (`load → filter → encode → smooth → render`); all hold PASS, timestamps are
  nondecreasing, and downstream `input_ref` values match predecessor validation
  times. The recorded browser control used Chrome 154 and Canvas 2D.

## Plan adherence, leakage, and multiplicity

The implementation matches the frozen amendment: montage selection defines the
channel pool, the linked endpoints define a nonempty inclusive window, accepted
montage changes reset it, “All” restores the complete pool, and both rendering
paths use the visible slice. Empty montage intersections return before state
mutation.

This is a descriptive display control, not an inferential model. Train/test
leakage, statistical nulls, p-values, and inferential multiplicity do not apply.
The post-hoc X-ray defaults are explicitly identified as selection-informed and
must not be treated as statistical cluster detection.

## Residual risks

- Browser behavior was not independently repeated outside the recorded Chrome
  154 / Canvas 2D environment.
- X-ray smoothing and connectivity use displayed-list adjacency, not physical
  scalp neighbors.
- The visible window changes the channel neighborhood. Narrowing or shifting it
  can merge, attenuate, or remove structures near a window boundary; this is the
  single defensible change most likely to alter the display.
- Threshold choice, sampled X-ray resolution, eight-voxel cleanup, conventional
  label grouping, and the optional dense-smoothing memory cost remain documented
  presentation risks.

These limitations constrain interpretation but do not invalidate the viewer.

## Exact commands and outputs

### Complete manifest hash audit before review overwrite

```bash
cd /Users/nikolaj_syrov/Documents/GitHub/eeg-tfr-volume
python3 - <<'PY'
from pathlib import Path
import hashlib, json
root=Path('/Users/nikolaj_syrov/Documents/GitHub/eeg-tfr-volume')
m=json.loads((root/'analyses/ride-sr-smoothing-viewer-002/result_manifest.json').read_text())
rows=[]
p=m['primary_artifact']['path']; data=(root/p).read_bytes()
rows.append((p,len(data)==m['primary_artifact']['bytes'],hashlib.sha256(data).hexdigest()==m['primary_artifact']['sha256']))
for section in ('sources','governance'):
    for p,expected in m[section].items():
        actual=hashlib.sha256((root/p).read_bytes()).hexdigest()
        rows.append((p,True,actual==expected))
print('entries',len(rows),'failures',sum(not(a and b) for _,a,b in rows))
PY
```

Output: `entries 18 failures 0`.

### Maintained production-JavaScript regression

```bash
cd /Users/nikolaj_syrov/Documents/GitHub/eeg-tfr-volume
node tests/channel_window_regression.js src/ride_viewer_template.html
node tests/channel_window_regression.js docs/ride.html
```

Each command returned:

```json
{"cases":172550,"failures":0,"trimmed":[5,6,7,8,9,10],"one":[10],"montageReset":[23,24,25,26,27],"fullRestore":[0,27,28],"visibleSliceConsumers":{"axes":1,"dense":1,"xray":1,"text":1},"axisUsesShownLabels":true,"outputsUseShownEndpoints":true}
```

### Relevant maintained tests

```bash
cd /Users/nikolaj_syrov/Documents/GitHub/eeg-tfr-volume
PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-eeg-channel-scroll-closure python3 -m unittest -v tests.test_ride_volume tests.test_ride_real_data
```

Output: `Ran 10 tests in 6.397s` and `OK`.

### Template identity and instrument-chain audit

```bash
cd /Users/nikolaj_syrov/Documents/GitHub/eeg-tfr-volume
python3 - <<'PY'
from pathlib import Path
from datetime import datetime
import json, re
root=Path('/Users/nikolaj_syrov/Documents/GitHub/eeg-tfr-volume')
t=(root/'src/ride_viewer_template.html').read_text()
d=(root/'docs/ride.html').read_text()
m=re.search(r'<script id="payload" type="application/json">(.*?)</script>',d,re.S)
print('template_substitution_exact',bool(m) and t.replace('$PAYLOAD',m.group(1))==d,'payload_chars',len(m.group(1)))
a=root/'analyses/ride-sr-smoothing-viewer-002'
c=json.loads((a/'config.json').read_text()); g=json.loads((a/'gate_status.json').read_text())
obs={x['stage']:x for x in g['instrument_status']}; errors=[]; prev=None
for i,x in enumerate(c['instruments']):
    o=obs[x['stage']]; when=datetime.fromisoformat(o['validated_at'])
    if x['position']!=i: errors.append('position:'+x['stage'])
    if x['consumes']!=(None if i==0 else c['instruments'][i-1]['stage']): errors.append('consumes:'+x['stage'])
    if o['status']!='PASS': errors.append('status:'+x['stage'])
    if prev and when<prev: errors.append('stale:'+x['stage'])
    if i and o['input_ref']!=f'{x["consumes"]} at {obs[x["consumes"]]["validated_at"]}': errors.append('input_ref:'+x['stage'])
    prev=when
print('instrument_stages',len(c['instruments']),'errors',errors)
PY
```

Output: `template_substitution_exact True payload_chars 35839084` and
`instrument_stages 5 errors []`.

## Final bookkeeping

After writing this review, update only its SHA-256 entry in
`result_manifest.json`, then apply the approved adversarial-review and release
gate transitions and refresh hashes for those mutable governance artifacts.
