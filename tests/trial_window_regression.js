const fs = require("fs");

const sourcePath = process.argv[2];
if (!sourcePath) {
  throw new Error("usage: node trial_window_regression.js <viewer-template.html>");
}

const source = fs.readFileSync(sourcePath, "utf8");
const cut = (start, end) => {
  const startIndex = source.indexOf(start);
  const endIndex = source.indexOf(end, startIndex);
  if (startIndex < 0 || endIndex < 0) {
    throw new Error(`could not extract production source between ${start} and ${end}`);
  }
  return source.slice(startIndex, endIndex);
};

const range = (value, max) => ({ value, min: 0, max });
const controls = {
  t0: range(0, 1750),
  t1: range(1750, 1750),
  r0: range(0, 456),
  r1: range(456, 456),
  c0: range(0, 11),
  c1: range(11, 11),
};

eval(cut("function bounds", "function representedValue"));
eval(cut("function enforce", "for(const el of Object.values(controls))"));

const failures = [];
let cases = 0;
for (let low = 0; low <= 456; low += 1) {
  for (let high = low; high <= 456; high += 1) {
    controls.r0.value = low;
    controls.r1.value = high;
    const initial = bounds();
    if (initial.r0 !== low || initial.r1 !== high || initial.r1 - initial.r0 + 1 !== high - low + 1) {
      failures.push(["inclusive", low, high, initial]);
    }

    const startMoved = Math.min(456, high + 1);
    controls.r0.value = startMoved;
    controls.r1.value = high;
    enforce(controls.r0);
    if (+controls.r0.value !== startMoved || +controls.r1.value !== startMoved) {
      failures.push(["start-cross", low, high, startMoved, controls.r0.value, controls.r1.value]);
    }

    const endMoved = Math.max(0, low - 1);
    controls.r0.value = low;
    controls.r1.value = endMoved;
    enforce(controls.r1);
    if (+controls.r0.value !== endMoved || +controls.r1.value !== endMoved) {
      failures.push(["end-cross", low, high, endMoved, controls.r0.value, controls.r1.value]);
    }
    cases += 3;
  }
}

controls.r0.value = 0;
controls.r1.value = 456;
const full = bounds();
controls.r0.value = 210;
controls.r1.value = 210;
const single = bounds();
controls.r0.value = 100;
controls.r1.value = 220;
const trimmed = bounds();

const bodies = {
  axes: cut("function drawAxes", "function quad"),
  faces: cut("function addFaces", "function drawDense"),
  dense: cut("function drawDense", "function passes"),
  xray: cut("function drawThreshold", "function drawOnset"),
  response: cut("function drawResponseCurtain", "function drawOne"),
  text: cut("function updateText", "function drawAll"),
};

const result = {
  cases,
  failures: failures.length,
  full: [full.r0, full.r1, full.r1 - full.r0 + 1],
  single: [single.r0, single.r1, single.r1 - single.r0 + 1],
  trimmed: [trimmed.r0, trimmed.r1, trimmed.r1 - trimmed.r0 + 1],
  consumers: Object.fromEntries(
    Object.entries(bodies).map(([name, body]) => [name, /b\.r[01]/.test(body)]),
  ),
  outputsWired:
    /trialStartOut/.test(bodies.text) &&
    /trialEndOut/.test(bodies.text),
  singleTrialXrayGuard:
    /rs===1\?b\.r0/.test(bodies.xray) &&
    /rs===1\?\.5/.test(bodies.xray),
  singleTrialResponseGuard: /span===0/.test(bodies.response),
  controlsInitialized:
    source.includes("[controls.r0,NR-1,0]") &&
    source.includes("[controls.r1,NR-1,NR-1]"),
};

if (failures.length) {
  throw new Error(`trial-window regression failures: ${JSON.stringify(failures.slice(0, 10))}`);
}
if (Object.values(result.consumers).some(value => !value)) {
  throw new Error(`trial window not consumed everywhere: ${JSON.stringify(result.consumers)}`);
}
process.stdout.write(`${JSON.stringify(result)}\n`);
