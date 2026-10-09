const fs = require("fs");

const source = fs.readFileSync(process.argv[2], "utf8");
const start = source.indexOf("function bounds");
const end = source.indexOf("function color", start);
if (start < 0 || end < 0) throw new Error("production representation function not found");

const NR = 1;
const NC = 2;
const NT = 3;
const idx = (r, c, t) => (r * NC + c) * NT + t;
const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
const controls = {
  representation: { value: "left-right" },
  t0: { value: 0 },
  t1: { value: 2 },
};
const PAIR_DEFS = [{ leftIndex: 0, rightIndex: 1 }];
const trialOrder = [0];
const volume = {};
let smoothedVolume = null;
const uvPerCount = 0.5;

eval(source.slice(start, end));

const raw = new Int16Array([1, 2, 3, 10, 20, 30]);
controls.representation.value = "left-right";
const leftRight = [0, 1, 2].map((time) => representedValue(raw, 0, 0, time, uvPerCount));
controls.representation.value = "right-left";
const rightLeft = [0, 1, 2].map((time) => representedValue(raw, 0, 0, time, uvPerCount));
controls.representation.value = "recorded";
const recorded = [0, 1, 2].map((time) => representedValue(raw, 0, 0, time, uvPerCount));

const result = {
  leftRight,
  rightLeft,
  recorded,
  inverse: leftRight.every((value, index) => value === -rightLeft[index]),
};
if (!result.inverse) throw new Error("right-left is not the sign inverse of left-right");
process.stdout.write(`${JSON.stringify(result)}\n`);
