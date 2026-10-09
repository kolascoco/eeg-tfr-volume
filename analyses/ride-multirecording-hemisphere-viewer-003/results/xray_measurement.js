const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const htmlPath = process.argv[2];
const html = fs.readFileSync(htmlPath, "utf8");
const match = html.match(/<script id="payload" type="application\/json">(.*?)<\/script>/s);
if (!match) throw new Error("payload not found");
const payload = JSON.parse(match[1]);
const [NR, NC, NT] = payload.volume.shape;
const scale = payload.volume.microvolts_per_count;
const rt = payload.response_times_ms;
const order = Array.from({ length: NR }, (_, index) => index).sort(
  (a, b) => rt[a] - rt[b] || a - b,
);
const index = (trial, channel, time) => (trial * NC + channel) * NT + time;
const count = NR * NC * NT;
const volumes = {};
for (const key of ["S", "R"]) {
  const asset = payload.volume.assets[key];
  const assetBytes = fs.readFileSync(path.resolve(path.dirname(htmlPath), asset.asset));
  if (assetBytes.byteLength !== asset.asset_bytes) throw new Error(`${key} volume byte length mismatch`);
  const bytes = asset.compression === "gzip" ? zlib.gunzipSync(assetBytes) : assetBytes;
  if (bytes.byteLength !== asset.uncompressed_bytes) throw new Error(`${key} expanded byte length mismatch`);
  volumes[key] = new Int16Array(bytes.buffer, bytes.byteOffset, count);
}
const pairs = payload.metadata.bilateral_pairs.map(([left, right]) => [
  payload.channels.indexOf(left),
  payload.channels.indexOf(right),
]);
if (pairs.length !== 12 || pairs.some(([left, right]) => left < 0 || right < 0)) {
  throw new Error("bilateral pair contract failed");
}

const controls = { polarity: { value: "both" } };
function passes(value, threshold) {
  const polarity = controls.polarity.value;
  return polarity === "positive"
    ? value >= threshold
    : polarity === "negative"
      ? value <= -threshold
      : Math.abs(value) >= threshold;
}
const productionStart = html.indexOf("function blurGridAxis");
const productionEnd = html.indexOf("function validateXrayKernel");
if (productionStart < 0 || productionEnd < 0) throw new Error("production X-ray functions not found");
eval(html.slice(productionStart, productionEnd));

const rs = 36;
const cs = pairs.length;
const ts = 64;
const at = (trial, channel, time) => (trial * cs + channel) * ts + time;
const threshold = Number(payload.volume.default_limit_uv.toFixed(2)) * 0.30;
const totals = {};
for (const key of ["S", "R"]) {
  const sampled = new Float32Array(rs * cs * ts);
  for (let ri = 0; ri < rs; ri += 1) {
    const rank = Math.round((ri / (rs - 1)) * (NR - 1));
    for (let ci = 0; ci < cs; ci += 1) {
      const [left, right] = pairs[ci];
      for (let ti = 0; ti < ts; ti += 1) {
        const time = Math.round((ti / (ts - 1)) * (NT - 1));
        sampled[at(ri, ci, ti)] =
          (volumes[key][index(order[rank], left, time)] -
            volumes[key][index(order[rank], right, time)]) * scale;
      }
    }
  }
  const grid = smoothXrayGrid(sampled, rs, cs, ts, 3);
  const mask = coherentMask(grid, threshold, rs, cs, ts, 8);
  totals[key] = {
    positive: mask.filter((value) => value === 1).length,
    negative: mask.filter((value) => value === 2).length,
    total: mask.filter(Boolean).length,
  };
}

const edge = blurGridAxis(new Float32Array([8, 0, 0]), 1, 1, 3, 2);
const opposite = coherentMask(
  new Float32Array([5, 5, 5, 5, -5, -5, -5, -5]),
  4,
  1,
  1,
  8,
  8,
);
process.stdout.write(`${JSON.stringify({ shape: [NR, NC, NT], pairCount: pairs.length, totals, edge: Array.from(edge), oppositeRetained: opposite.filter(Boolean).length })}\n`);
