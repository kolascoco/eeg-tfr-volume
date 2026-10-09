import tempfile
import unittest
import base64
import json
import subprocess
from pathlib import Path

import numpy as np

from ride_volume import (
    encode_components,
    filter_ride_components,
    load_compact_ride_dataset,
    write_ride_viewer,
)


class TestRIDEVolume(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(19)
        self.components = {
            key: rng.normal(scale=4e-6, size=(5, 3, 9)).astype(np.float32)
            for key in ("S", "R")
        }
        self.times = np.arange(-8, 10, 2, dtype=np.float32)
        self.rt = np.array([8, 4, 6, 2, 0], dtype=np.float32)
        self.channels = ["Ch01", "Ch02", "Ch03"]
        self.metadata = {"component_titles": {"S": "S", "R": "R"}}

    def test_signed_encoding_preserves_microvolt_samples(self):
        payload = encode_components(self.components)
        self.assertEqual(payload["shape"], [5, 3, 9])
        self.assertEqual(payload["dtype"], "int16_le")
        self.assertEqual(set(payload["data"]), {"S", "R"})
        decoded = np.frombuffer(base64.b64decode(payload["data"]["S"]), dtype="<i2")
        reconstructed = decoded.reshape(self.components["S"].shape) * payload["microvolts_per_count"]
        expected = self.components["S"] * 1e6
        self.assertLessEqual(float(np.max(np.abs(reconstructed - expected))), 0.0051)
        self.assertGreaterEqual(payload["max_abs_uv"], payload["default_limit_uv"])

    def test_component_shape_mismatch_fails(self):
        bad = dict(self.components)
        bad["R"] = bad["R"][:, :, :-1]
        with self.assertRaisesRegex(ValueError, "shapes differ"):
            encode_components(bad)

    def test_gzip_compact_round_trip_preserves_quantized_samples(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            html = root / "ride.html"
            binary = root / "ride-volume.i16.gz"
            manifest = root / "ride-volume.json"
            write_ride_viewer(
                html,
                self.components,
                self.times,
                self.rt,
                self.channels,
                self.metadata,
                binary_output=binary,
                binary_asset_url=binary.name,
                manifest_output=manifest,
            )
            restored, times, rt, channels, _ = load_compact_ride_dataset(manifest, binary)
        self.assertEqual(channels, self.channels)
        np.testing.assert_array_equal(times, self.times)
        np.testing.assert_array_equal(rt, self.rt)
        for key in ("S", "R"):
            np.testing.assert_allclose(
                restored[key] * 1e6,
                np.rint(self.components[key] * 1e8) / 100,
                atol=1e-5,
            )

    def test_mne_bandpass_preserves_shape_and_prefers_in_band_signal(self):
        sfreq = 500.0
        times = np.arange(0, 20, 1 / sfreq)
        signal = (
            np.sin(2 * np.pi * 0.1 * times)
            + np.sin(2 * np.pi * 10 * times)
            + np.sin(2 * np.pi * 80 * times)
        )[None, None, :]
        components = {key: signal.astype(np.float32) for key in ("S", "R")}
        filtered = filter_ride_components(components, sfreq, 0.5, 20.0)
        self.assertEqual(filtered["S"].shape, signal.shape)
        self.assertTrue(np.all(np.isfinite(filtered["S"])))
        center = slice(int(2 * sfreq), int(18 * sfreq))
        values = filtered["S"][0, 0, center]
        center_times = times[center]
        amplitude = lambda hz: abs(
            2 * np.dot(values, np.sin(2 * np.pi * hz * center_times)) / values.size
        )
        self.assertGreater(amplitude(10), 0.8)
        self.assertLess(amplitude(0.1), 0.25)
        self.assertLess(amplitude(80), 0.05)

    def test_html_has_two_boxes_trial_window_and_threshold_controls(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ride.html"
            write_ride_viewer(
                output,
                self.components,
                self.times,
                self.rt,
                self.channels,
                self.metadata,
            )
            text = output.read_text(encoding="utf-8")
        self.assertNotIn("$PAYLOAD", text)
        self.assertEqual(text.count("class=\"volume-canvas\""), 2)
        self.assertNotIn('data-component="C"', text)
        self.assertIn('id="trialStart" type="range"', text)
        self.assertIn('id="trialEnd" type="range"', text)
        self.assertIn("visible trial window adjustable", text)
        self.assertIn("function bounds(){return{t0:+controls.t0.value,t1:+controls.t1.value,r0:+controls.r0.value,r1:+controls.r1.value}}", text)
        self.assertIn("Threshold volume (X-ray)", text)
        self.assertIn("Interactive scalp montage for channel selection", text)
        self.assertIn('data-region-button="posterior"', text)
        self.assertIn('data-region-button="central"', text)
        self.assertIn('data-region-button="frontal"', text)
        self.assertIn('data-hemi-button="left"', text)
        self.assertIn('data-hemi-button="midline"', text)
        self.assertIn('data-hemi-button="right"', text)
        self.assertIn("function validateMontageSelection", text)
        self.assertIn("function filterChannels", text)
        self.assertIn("Channel or pair adjacency follows the displayed list order", text)
        self.assertIn('id="channelStart" type="range"', text)
        self.assertIn('id="channelEnd" type="range"', text)
        self.assertIn("function displayChannels", text)
        self.assertIn("resetChannelWindow", text)
        self.assertIn("Positive + negative", text)
        self.assertIn("Temporal threads", text)
        self.assertIn("Crisp outer structure strokes", text)
        self.assertIn("X-ray structure smoothing", text)
        self.assertIn('id="xraySmoothing" type="range" min="0" max="3" value="3"', text)
        self.assertIn('id="threshold" type="range" min="5" max="100" value="30"', text)
        self.assertIn("function smoothXrayGrid", text)
        self.assertIn("function coherentMask", text)
        self.assertIn("function validateXrayKernel", text)
        self.assertIn("Small same-polarity 6-connected components are removed", text)
        self.assertIn("Color limit (±)", text)
        self.assertIn('id="vlim" type="range" data-scale="log10" step="0.001"', text)
        self.assertIn("DEFAULT_TIME_START_MS=-542,DEFAULT_VLIM_UV=2.41,MIN_VLIM_UV=.05", text)
        self.assertIn("function colorLimit(){return 10**(+controls.vlim.value)}", text)
        self.assertIn("Logarithmic control gives low-amplitude color limits more adjustment space", text)
        self.assertIn("Time-axis stretch", text)
        self.assertIn('id="stretch" type="range" min="0.5" max="3" value="1.8"', text)
        self.assertIn('id="zoom" type="range" min="0.45" max="2.6" value="0.45"', text)
        self.assertIn('<option value="recorded" selected>Recorded channels</option>', text)
        self.assertIn('<option value="dense" selected>Closed dense volume</option>', text)
        self.assertIn("Dense time → trial smoothing", text)
        self.assertIn('id="smoothing" type="range" min="0" max="8" value="4"', text)
        self.assertIn("if(+controls.smoothing.value>0)queueSmoothing();else drawAll()", text)
        self.assertIn("function separableSmooth", text)
        self.assertIn("function validateSmoothingKernel", text)
        self.assertIn("Dense-view time/trial smoothing and X-ray structure smoothing are separate display-only pipelines", text)
        self.assertIn("display-only", text)
        self.assertIn("queueSmoothing", text)
        self.assertIn("0 ms · stimulus onset", text)
        self.assertIn("10.1111/psyp.12004", text)
        self.assertIn("10.1111/psyp.14708", text)
        self.assertIn("Ch01", text)
        self.assertIn("Amplitude is shown in microvolts", text)
        self.assertIn("signed 16-bit data", text)
        self.assertIn("threads join adjacent rendered time bins", text)
        self.assertIn("Dense-view time/trial smoothing and X-ray structure smoothing are separate display-only pipelines", text)
        self.assertIn("descriptive, not statistical significance", text)
        self.assertIn("Browser runtime: ${navigator.userAgent}", text)
        self.assertIn("function voxelFaces", text)
        self.assertIn("function drawCrispOutline", text)
        self.assertIn("MAX_THRESHOLD_VOXELS=2400", text)
        self.assertIn("strongest coherent voxels", text)
        self.assertIn("Only exposed voxel faces are drawn", text)
        self.assertIn("requestAnimationFrame", text)
        self.assertIn("faces.sort((a,b)=>b.depth-a.depth)", text)
        self.assertIn("items.list.sort((a,b)=>b.depth-a.depth)", text)
        self.assertIn('id="representation"', text)
        self.assertIn('value="left-right"', text)
        self.assertIn('value="right-left"', text)
        self.assertIn('data-hemi-zone="left"', text)
        self.assertIn('data-hemi-zone="right"', text)
        self.assertIn("function representedValue", text)
        self.assertIn("function selectedRawSet", text)
        self.assertIn("function visibleRawSet", text)
        self.assertIn("Bilateral-pair validation failed", text)
        self.assertIn("async function loadVolume", text)

    def test_published_xray_numerical_regressions(self):
        root = Path(__file__).resolve().parents[1]
        helper = root / "analyses/ride-multirecording-hemisphere-viewer-003/results/xray_measurement.js"
        published = root / "docs/ride.html"
        result = subprocess.run(
            ["node", str(helper), str(published)],
            check=True,
            capture_output=True,
            text=True,
        )
        measurement = json.loads(result.stdout)
        self.assertEqual(measurement["shape"], [457, 28, 1751])
        self.assertEqual(measurement["pairCount"], 12)
        self.assertEqual(measurement["totals"]["S"], {"positive": 17, "negative": 18, "total": 35})
        self.assertEqual(measurement["totals"]["R"], {"positive": 16, "negative": 20, "total": 36})
        self.assertTrue(np.allclose(measurement["edge"], [16 / 3, 2, 0]))
        self.assertEqual(measurement["oppositeRetained"], 0)

        html = published.read_text(encoding="utf-8")
        threshold_body = html.split("function drawThreshold", 1)[1].split("function drawOnset", 1)[0]
        dense_body = html.split("function drawDense", 1)[1].split("function blurGridAxis", 1)[0]
        self.assertIn("rawValueAt", threshold_body)
        self.assertNotIn("valueAt(", threshold_body)
        self.assertIn("valueAt(", dense_body)

        montage_source = html.split("function validateMontageSelection", 1)[1].split("validateMontageSelection();", 1)[0]
        self.assertIn("P3,Pz,P4,O1,O2", montage_source)
        self.assertIn("FC5,FC3,FC1,C5,C3,C1,CP5,CP3,CP1", montage_source)
        self.assertIn("F4", montage_source)

    def test_channel_window_executes_production_javascript(self):
        root = Path(__file__).resolve().parents[1]
        helper = root / "tests/channel_window_regression.js"
        template = root / "src/ride_viewer_template.html"
        result = subprocess.run(
            ["node", str(helper), str(template)],
            check=True,
            capture_output=True,
            text=True,
        )
        measurement = json.loads(result.stdout)

        self.assertEqual(measurement["cases"], 172550)
        self.assertEqual(measurement["failures"], 0)
        self.assertEqual(measurement["trimmed"], [5, 6, 7, 8, 9, 10])
        self.assertEqual(measurement["one"], [10])
        self.assertEqual(measurement["montageReset"], [23, 24, 25, 26, 27])
        self.assertEqual(measurement["fullRestore"], [0, 27, 28])
        self.assertEqual(
            measurement["visibleSliceConsumers"],
            {"axes": 1, "dense": 1, "xray": 1, "text": 1},
        )
        self.assertTrue(measurement["axisUsesShownLabels"])
        self.assertTrue(measurement["outputsUseShownEndpoints"])

    def test_trial_window_executes_production_javascript(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [
                "node",
                str(root / "tests/trial_window_regression.js"),
                str(root / "src/ride_viewer_template.html"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        measurement = json.loads(result.stdout)
        self.assertEqual(measurement["cases"], 313959)
        self.assertEqual(measurement["failures"], 0)
        self.assertEqual(measurement["full"], [0, 456, 457])
        self.assertEqual(measurement["single"], [210, 210, 1])
        self.assertEqual(measurement["trimmed"], [100, 220, 121])
        self.assertTrue(all(measurement["consumers"].values()))
        self.assertTrue(measurement["outputsWired"])
        self.assertTrue(measurement["singleTrialXrayGuard"])
        self.assertTrue(measurement["singleTrialResponseGuard"])
        self.assertTrue(measurement["controlsInitialized"])

    def test_montage_pair_interactions_execute_production_javascript(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [
                "node",
                str(root / "tests/montage_interaction_regression.js"),
                str(root / "src/ride_viewer_template.html"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        measurement = json.loads(result.stdout)
        self.assertEqual(measurement["failures"], 0)
        self.assertEqual(measurement["bilateralRegionStates"], 14)
        self.assertEqual(measurement["bilateralWindows"], 508)
        self.assertEqual(measurement["recordedSelectionStates"], 49)
        self.assertTrue(measurement["emptySelectionProtected"])
        self.assertTrue(measurement["hemisphereIgnoredInBilateral"])
        self.assertEqual(measurement["c3c4VisibleRaw"], [10, 14])
        self.assertEqual(measurement["reversedC3C4Label"], "C4−C3")
        self.assertTrue(measurement["scrollSyncWired"])
        self.assertTrue(measurement["visibleSummaryWired"])

    def test_external_binary_encoding_and_offsets(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "ride.html"
            binary = Path(directory) / "ride-volume.i16"
            write_ride_viewer(
                output,
                self.components,
                self.times,
                self.rt,
                self.channels,
                self.metadata,
                binary_output=binary,
                binary_asset_url="ride-volume.i16",
            )
            binary_size = binary.stat().st_size
            match = __import__("re").search(
                r'<script id="payload" type="application/json">(.*?)</script>',
                output.read_text(encoding="utf-8"),
                __import__("re").S,
            )
            payload = json.loads(match.group(1))
        component_bytes = 5 * 3 * 9 * 2
        self.assertEqual(binary_size, component_bytes * 2)
        self.assertEqual(payload["volume"]["component_offsets_bytes"], {"S": 0, "R": component_bytes})
        self.assertNotIn("data", payload["volume"])

    def test_hemisphere_subtraction_executes_production_javascript(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [
                "node",
                str(root / "tests/hemisphere_regression.js"),
                str(root / "src/ride_viewer_template.html"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        measurement = json.loads(result.stdout)
        self.assertEqual(measurement["leftRight"], [-4.5, -9.0, -13.5])
        self.assertEqual(measurement["rightLeft"], [4.5, 9.0, 13.5])
        self.assertEqual(measurement["recorded"], [0.5, 1.0, 1.5])
        self.assertTrue(measurement["inverse"])

    def test_writer_rejects_axis_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "bad.html"
            with self.assertRaisesRegex(ValueError, "response_times_ms has length"):
                write_ride_viewer(output, self.components, self.times, self.rt[:-1], self.channels, self.metadata)
            with self.assertRaisesRegex(ValueError, "channels has length"):
                write_ride_viewer(output, self.components, self.times, self.rt, self.channels[:-1], self.metadata)


if __name__ == "__main__":
    unittest.main()
