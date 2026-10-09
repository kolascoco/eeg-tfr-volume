const fs = require("fs");

const sourcePath = process.argv[2];
if (!sourcePath) throw new Error("usage: node montage_interaction_regression.js <viewer-template.html>");
const source = fs.readFileSync(sourcePath, "utf8");
const cut = (start, end) => {
  const startIndex = source.indexOf(start);
  const endIndex = source.indexOf(end, startIndex);
  if (startIndex < 0 || endIndex < 0) throw new Error(`could not extract ${start} … ${end}`);
  return source.slice(startIndex, endIndex);
};

const channels = [
  "F3", "F4", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
  "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "CP5", "CP3", "CP1",
  "CPz", "CP2", "CP4", "CP6", "P3", "Pz", "P4", "O1", "O2",
];
const NC = channels.length;
const pairs = [
  ["F3", "F4"], ["FC5", "FC6"], ["FC3", "FC4"], ["FC1", "FC2"],
  ["C5", "C6"], ["C3", "C4"], ["C1", "C2"], ["CP5", "CP6"],
  ["CP3", "CP4"], ["CP1", "CP2"], ["P3", "P4"], ["O1", "O2"],
];
const PAIR_DEFS = pairs.map(([left, right]) => ({
  left,
  right,
  leftIndex: channels.indexOf(left),
  rightIndex: channels.indexOf(right),
  label: `${left}−${right}`,
}));
const ALL_REGIONS = ["posterior", "central", "frontal"];
const ALL_HEMISPHERES = ["left", "midline", "right"];
const range = () => ({ value: 0, min: 0, max: 0 });
const controls = { representation: { value: "left-right" }, c0: range(), c1: range() };
let selectedRegions = new Set(ALL_REGIONS);
let selectedHemispheres = new Set(ALL_HEMISPHERES);
let activeChannels = [];

eval(cut("function channelRegion", "function validateMontageSelection"));
eval(cut("function resetChannelWindow", "const MONTAGE_POS"));

const failures = [];
let bilateralRegionStates = 0;
let bilateralWindows = 0;
for (const representation of ["left-right", "right-left"]) {
  controls.representation.value = representation;
  for (let mask = 1; mask < 1 << ALL_REGIONS.length; mask += 1) {
    selectedRegions = new Set(ALL_REGIONS.filter((_, index) => mask & (1 << index)));
    selectedHemispheres = new Set(ALL_HEMISPHERES);
    activeChannels = filterChannels();
    const expectedPool = PAIR_DEFS.map((pair, index) => ({ pair, index }))
      .filter(({ pair }) => selectedRegions.has(channelRegion(pair.left)))
      .map(({ index }) => index);
    if (JSON.stringify(activeChannels) !== JSON.stringify(expectedPool)) {
      failures.push(["bilateral-pool", representation, mask, activeChannels, expectedPool]);
    }
    resetChannelWindow();
    for (let start = 0; start < activeChannels.length; start += 1) {
      for (let end = start; end < activeChannels.length; end += 1) {
        controls.c0.value = start;
        controls.c1.value = end;
        const shown = activeChannels.slice(start, end + 1);
        const expectedRaw = [...new Set(shown.flatMap(index => [PAIR_DEFS[index].leftIndex, PAIR_DEFS[index].rightIndex]))].sort((a, b) => a - b);
        const actualRaw = [...visibleRawSet()].sort((a, b) => a - b);
        if (JSON.stringify(actualRaw) !== JSON.stringify(expectedRaw)) {
          failures.push(["visible-raw", representation, mask, start, end, actualRaw, expectedRaw]);
        }
        bilateralWindows += 1;
      }
    }
    bilateralRegionStates += 1;
  }
}

let recordedSelectionStates = 0;
controls.representation.value = "recorded";
for (let regionMask = 1; regionMask < 1 << ALL_REGIONS.length; regionMask += 1) {
  for (let hemiMask = 1; hemiMask < 1 << ALL_HEMISPHERES.length; hemiMask += 1) {
    selectedRegions = new Set(ALL_REGIONS.filter((_, index) => regionMask & (1 << index)));
    selectedHemispheres = new Set(ALL_HEMISPHERES.filter((_, index) => hemiMask & (1 << index)));
    const actual = filterChannels();
    const expected = channels.map((name, index) => ({ name, index }))
      .filter(({ name }) => selectedRegions.has(channelRegion(name)) && selectedHemispheres.has(channelHemisphere(name)))
      .map(({ index }) => index);
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      failures.push(["recorded-pool", regionMask, hemiMask, actual, expected]);
    }
    recordedSelectionStates += 1;
  }
}

const note = { textContent: "", classList: { add() {}, remove() {} } };
const $ = () => note;
const thresholdBudget = { S: null, R: null };
function syncMontage() {}
function scheduleDraw() {}
eval(cut("function setMontageSelection", "function setRepresentation"));

controls.representation.value = "left-right";
selectedRegions = new Set(["posterior"]);
selectedHemispheres = new Set(ALL_HEMISPHERES);
activeChannels = filterChannels();
resetChannelWindow();
const beforeEmpty = [...activeChannels];
setMontageSelection("region", "posterior");
const emptySelectionProtected = selectedRegions.has("posterior") &&
  JSON.stringify(activeChannels) === JSON.stringify(beforeEmpty) &&
  note.textContent.includes("no displayable channels");
const beforeHemisphere = [...activeChannels];
setMontageSelection("hemisphere", "left");
const hemisphereIgnoredInBilateral = JSON.stringify(activeChannels) === JSON.stringify(beforeHemisphere);

selectedRegions = new Set(ALL_REGIONS);
activeChannels = filterChannels();
resetChannelWindow();
controls.c0.value = 5;
controls.c1.value = 5;
const c3c4VisibleRaw = [...visibleRawSet()].sort((a, b) => a - b);
controls.representation.value = "right-left";
const reversedC3C4Label = channelLabel(5);
const scrollSyncWired = source.includes("if(el===controls.c0||el===controls.c1)syncMontage()");
const visibleSummaryWired = source.includes("Visible ${paired?'pair window':'channel window'}");

if (failures.length) throw new Error(JSON.stringify(failures.slice(0, 10)));
process.stdout.write(`${JSON.stringify({
  failures: failures.length,
  bilateralRegionStates,
  bilateralWindows,
  recordedSelectionStates,
  emptySelectionProtected,
  hemisphereIgnoredInBilateral,
  c3c4VisibleRaw,
  reversedC3C4Label,
  scrollSyncWired,
  visibleSummaryWired,
})}\n`);
