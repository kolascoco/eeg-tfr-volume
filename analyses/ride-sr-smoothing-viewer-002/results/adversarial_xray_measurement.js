const fs = require('fs');

const html = fs.readFileSync(process.argv[2], 'utf8');
const match = html.match(/<script id="payload" type="application\/json">(.*?)<\/script>/s);
if (!match) throw new Error('payload not found');
const payload = JSON.parse(match[1]);
const [NR, NC, NT] = payload.volume.shape;
const scale = payload.volume.microvolts_per_count;
const rt = payload.response_times_ms;
const order = Array.from({length: NR}, (_, i) => i).sort((a, b) => rt[a] - rt[b] || a - b);
const idx = (r, c, t) => (r * NC + c) * NT + t;

function decode(s) {
  const b = Buffer.from(s, 'base64');
  return new Int16Array(b.buffer, b.byteOffset, b.byteLength / 2);
}

function blur(source, rs, cs, ts, axis) {
  const out = new Float32Array(source.length);
  const at = (r, c, t) => (r * cs + c) * ts + t;
  for (let r = 0; r < rs; r++) for (let c = 0; c < cs; c++) for (let t = 0; t < ts; t++) {
    let sum = 2 * source[at(r,c,t)], weight = 2;
    if (axis === 0) {
      if (r > 0) { sum += source[at(r-1,c,t)]; weight++; }
      if (r+1 < rs) { sum += source[at(r+1,c,t)]; weight++; }
    } else if (axis === 1) {
      if (c > 0) { sum += source[at(r,c-1,t)]; weight++; }
      if (c+1 < cs) { sum += source[at(r,c+1,t)]; weight++; }
    } else {
      if (t > 0) { sum += source[at(r,c,t-1)]; weight++; }
      if (t+1 < ts) { sum += source[at(r,c,t+1)]; weight++; }
    }
    out[at(r,c,t)] = sum / weight;
  }
  return out;
}

function smooth(source, rs, cs, ts, level) {
  let out = source;
  if (level >= 1) out = blur(out, rs, cs, ts, 2);
  if (level >= 2) { out = blur(out, rs, cs, ts, 0); out = blur(out, rs, cs, ts, 1); }
  if (level >= 3) { out = blur(out, rs, cs, ts, 2); out = blur(out, rs, cs, ts, 0); }
  return out;
}

function coherent(values, threshold, rs, cs, ts, minSize) {
  const code = new Uint8Array(values.length), keep = new Uint8Array(values.length), seen = new Uint8Array(values.length);
  const at = (r,c,t) => (r*cs+c)*ts+t;
  for (let i = 0; i < values.length; i++) if (Math.abs(values[i]) >= threshold) code[i] = values[i] >= 0 ? 1 : 2;
  if (minSize <= 1) return code;
  for (let seed = 0; seed < code.length; seed++) {
    if (!code[seed] || seen[seed]) continue;
    const sign = code[seed], stack = [seed], group = [];
    seen[seed] = 1;
    while (stack.length) {
      const i = stack.pop(); group.push(i);
      const t = i % ts, q = (i-t)/ts, c = q % cs, r = (q-c)/cs;
      const neighbors = [];
      if (r>0) neighbors.push(at(r-1,c,t)); if (r+1<rs) neighbors.push(at(r+1,c,t));
      if (c>0) neighbors.push(at(r,c-1,t)); if (c+1<cs) neighbors.push(at(r,c+1,t));
      if (t>0) neighbors.push(at(r,c,t-1)); if (t+1<ts) neighbors.push(at(r,c,t+1));
      for (const n of neighbors) if (!seen[n] && code[n] === sign) { seen[n] = 1; stack.push(n); }
    }
    if (group.length >= minSize) for (const i of group) keep[i] = sign;
  }
  return keep;
}

const rs = 36, cs = 20, ts = 64;
const minSize = [1,3,8,8];
const vlim = Number(payload.volume.default_limit_uv.toFixed(2));
console.log(JSON.stringify({shape:[NR,NC,NT], scale, default_limit_raw:payload.volume.default_limit_uv, default_limit_control:vlim,
  defaults:{threshold:Number((html.match(/id="threshold"[^>]*value="([0-9]+)"/)||[])[1]), xray:Number((html.match(/id="xraySmoothing"[^>]*value="([0-9]+)"/)||[])[1]), dense:Number((html.match(/id="smoothing"[^>]*value="([0-9]+)"/)||[])[1])}}, null, 2));

for (const key of ['S','R']) {
  const raw = decode(payload.volume.data[key]);
  const sampled = new Float32Array(rs*cs*ts);
  const at = (r,c,t) => (r*cs+c)*ts+t;
  for (let ri=0;ri<rs;ri++) {
    const rank=Math.round(ri/(rs-1)*(NR-1));
    for (let ci=0;ci<cs;ci++) {
      const c=Math.round(ci/(cs-1)*(NC-1));
      for (let ti=0;ti<ts;ti++) {
        const t=Math.round(ti/(ts-1)*(NT-1));
        sampled[at(ri,ci,ti)] = raw[idx(order[rank],c,t)] * scale;
      }
    }
  }
  const rows=[];
  for (let level=0;level<=3;level++) {
    const grid=smooth(sampled,rs,cs,ts,level);
    for (const pct of (level===3?[29,30,31]:[30])) {
      const mask=coherent(grid,vlim*pct/100,rs,cs,ts,minSize[level]);
      rows.push({level,pct,positive:mask.filter(x=>x===1).length,negative:mask.filter(x=>x===2).length,total:mask.filter(Boolean).length});
    }
  }
  console.log(key, JSON.stringify(rows));
}

const edge = blur(new Float32Array([8,0,0]), 1,1,3,2);
const adversarial = coherent(new Float32Array([5,5,5,5,-5,-5,-5,-5]),4,1,1,8,8);
console.log(JSON.stringify({edge_renormalization:Array.from(edge), opposite_sign_adjacent_min8_retained:adversarial.filter(Boolean).length}));

// Execute the production functions extracted verbatim from the published artifact.
const prodStart = html.indexOf('function blurGridAxis');
const prodEnd = html.indexOf('function validateXrayKernel');
if (prodStart < 0 || prodEnd < 0) throw new Error('production X-ray functions not found');
const controls = {polarity: {value: 'both'}};
function passes(v, threshold) { const p=controls.polarity.value; return p==='positive'?v>=threshold:p==='negative'?v<=-threshold:Math.abs(v)>=threshold; }
eval(html.slice(prodStart, prodEnd));
const prodEdge = blurGridAxis(new Float32Array([8,0,0]), 1,1,3,2);
const prodOpposite = coherentMask(new Float32Array([5,5,5,5,-5,-5,-5,-5]),4,1,1,8,8);
const prodDiagonal = coherentMask(new Float32Array([5,0,0,5]),4,2,1,2,2);
const prodChannel = blurGridAxis(new Float32Array([0,8,0]),1,3,1,1);
const prodStrong = smoothXrayGrid(new Float32Array([0,0,0,0,8,0,0,0,0]),3,1,3,3);
console.log(JSON.stringify({production:{edge:Array.from(prodEdge),opposite_sign_adjacent_min8_retained:prodOpposite.filter(Boolean).length,diagonal_min2_retained:prodDiagonal.filter(Boolean).length,channel_blur:Array.from(prodChannel),strong_center:prodStrong[4]}}));
