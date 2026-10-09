const fs = require("fs");

const sourcePath = process.argv[2];
if (!sourcePath) {
  throw new Error("usage: node channel_window_regression.js <viewer-template.html>");
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

let activeChannels = [];
const range = () => ({ value: 0, min: 0, max: 0 });
const controls = { c0: range(), c1: range() };

// Execute the functions extracted from the production viewer, rather than a
// duplicate implementation maintained by the test.
eval(cut("function resetChannelWindow", "const MONTAGE_POS"));
eval(cut("function enforce", "for(const el of Object.values(controls))"));

let cases = 0;
const failures = [];
for (let size = 1; size <= 28; size += 1) {
  activeChannels = Array.from({ length: size }, (_, index) => 100 + index);
  resetChannelWindow();
  if (
    +controls.c0.value !== 0 ||
    +controls.c1.value !== size - 1 ||
    +controls.c0.max !== size - 1 ||
    +controls.c1.max !== size - 1
  ) {
    failures.push(["reset", size]);
  }
  if (
    displayChannels().length !== size ||
    displayChannels()[0] !== 100 ||
    displayChannels().at(-1) !== 99 + size
  ) {
    failures.push(["inclusive-reset", size]);
  }

  for (let low = 0; low < size; low += 1) {
    for (let high = low; high < size; high += 1) {
      for (let moved = 0; moved < size; moved += 1) {
        controls.c0.value = low;
        controls.c1.value = high;
        controls.c0.value = moved;
        enforce(controls.c0);
        const expectedLow = moved;
        const expectedHigh = moved > high ? moved : high;
        if (
          +controls.c0.value !== expectedLow ||
          +controls.c1.value !== expectedHigh ||
          displayChannels().length !== expectedHigh - expectedLow + 1
        ) {
          failures.push(["start", size, low, high, moved]);
        }

        controls.c0.value = low;
        controls.c1.value = high;
        controls.c1.value = moved;
        enforce(controls.c1);
        const expectedStart = moved < low ? moved : low;
        const expectedEnd = moved;
        if (
          +controls.c0.value !== expectedStart ||
          +controls.c1.value !== expectedEnd ||
          displayChannels().length !== expectedEnd - expectedStart + 1
        ) {
          failures.push(["end", size, low, high, moved]);
        }
        cases += 2;
      }
    }
  }
}

activeChannels = Array.from({ length: 28 }, (_, index) => index);
resetChannelWindow();
controls.c0.value = 5;
controls.c1.value = 10;
const trimmed = displayChannels();
controls.c0.value = 10;
enforce(controls.c0);
const one = displayChannels();

activeChannels = [23, 24, 25, 26, 27];
resetChannelWindow();
const montageReset = displayChannels();

activeChannels = Array.from({ length: 28 }, (_, index) => index);
resetChannelWindow();
const fullRestore = displayChannels();

const bodies = {
  axes: cut("function drawAxes", "function quad"),
  dense: cut("function drawDense", "function passes"),
  xray: cut("function drawThreshold", "function drawOnset"),
  text: cut("function updateText", "function drawAll"),
};
const result = {
  cases,
  failures: failures.length,
  trimmed,
  one,
  montageReset,
  fullRestore: [fullRestore[0], fullRestore.at(-1), fullRestore.length],
  visibleSliceConsumers: Object.fromEntries(
    Object.entries(bodies).map(([name, body]) => [
      name,
      (body.match(/displayChannels\(\)/g) || []).length,
    ]),
  ),
  axisUsesShownLabels: /channelLabel\(c\)/.test(bodies.axes),
  outputsUseShownEndpoints:
    /channelLabel\(shown\[0\]\)/.test(bodies.text) &&
    /channelLabel\(shown\[shown.length-1\]\)/.test(bodies.text),
};

if (failures.length) {
  throw new Error(`channel-window regression failures: ${JSON.stringify(failures.slice(0, 10))}`);
}
process.stdout.write(`${JSON.stringify(result)}\n`);
