import json
import re
import unittest
from pathlib import Path

import numpy as np

from ride_volume import load_compact_ride_dataset


ROOT = Path(__file__).resolve().parents[1]
PUBLISHED = ROOT / "docs" / "ride.html"
PUBLISHED_BINARIES = {
    key: ROOT / "docs" / f"ride-volume-{key}.i16.gz" for key in ("S", "R")
}
PUBLISHED_MANIFEST = ROOT / "docs" / "ride-volume.json"


class TestRIDERealData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.components, cls.times, cls.rt, cls.channels, cls.metadata = load_compact_ride_dataset(
            PUBLISHED_MANIFEST
        )

    def test_real_shape_time_and_response_alignment(self):
        self.assertEqual({value.shape for value in self.components.values()}, {(457, 28, 1751)})
        self.assertEqual((float(self.times[0]), float(self.times[-1])), (-1500.0, 2000.0))
        self.assertEqual(np.flatnonzero(self.times == 0).tolist(), [750])
        self.assertEqual(self.rt.shape, (457,))
        self.assertTrue(np.all((self.rt >= self.times[0]) & (self.rt <= self.times[-1])))
        order = np.argsort(self.rt, kind="stable")
        self.assertTrue(np.all(np.diff(self.rt[order]) >= 0))
        identity = self.metadata["trial_identity"]
        keys = list(zip(identity["recording_ids"], identity["original_1_based_mat_trial"]))
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(identity["recording_order"], ["S02_far", "S04_far", "S07_far"])

    def test_real_components_are_finite_and_nonconstant(self):
        for value in self.components.values():
            self.assertTrue(np.all(np.isfinite(value)))
            self.assertGreater(float(np.ptp(value)), 0.0)
        self.assertEqual(self.channels[10], "C3")
        processing = self.metadata["processing"]["filter"]
        self.assertEqual((processing["l_freq_hz"], processing["h_freq_hz"]), (0.5, 20.0))
        self.assertEqual(processing["method"], "iir")
        self.assertEqual(processing["iir_params"]["order"], 4)
        self.assertEqual(processing["effective_order"], 16)
        self.assertIsNone(self.metadata["processing"]["source_decimation"])

    def test_published_viewer_uses_filtered_three_recording_stack(self):
        match = re.search(
            r'<script id="payload" type="application/json">(.*?)</script>',
            PUBLISHED.read_text(encoding="utf-8"),
            re.S,
        )
        self.assertIsNotNone(match)
        payload = json.loads(match.group(1))
        self.assertEqual(payload["metadata"]["input"]["path"], "stacked:S02_far+S04_far+S07_far")
        self.assertEqual(payload["volume"]["shape"], [457, 28, 1751])
        self.assertEqual([source["trials"] for source in payload["metadata"]["input"]["sources"]], [149, 137, 171])
        self.assertEqual(payload["channels"][10], "C3")
        filtering = payload["metadata"]["processing"]["filter"]
        self.assertEqual((filtering["l_freq_hz"], filtering["h_freq_hz"]), (0.5, 20.0))
        self.assertEqual(filtering["effective_order"], 16)
        self.assertRegex(PUBLISHED.read_text(encoding="utf-8"), r"boundary transients")
        self.assertEqual(payload["volume"]["storage"], "external_int16_le_split")
        self.assertEqual(payload["volume"]["dtype"], "int16_le")
        self.assertNotIn('data-component="C"', PUBLISHED.read_text(encoding="utf-8"))
        expected_component_bytes = 457 * 28 * 1751 * 2
        self.assertEqual(set(payload["volume"]["assets"]), {"S", "R"})
        for key, path in PUBLISHED_BINARIES.items():
            asset = payload["volume"]["assets"][key]
            self.assertEqual(asset["asset"], path.name)
            self.assertEqual(asset["compression"], "gzip")
            self.assertEqual(asset["uncompressed_bytes"], expected_component_bytes)
            self.assertEqual(asset["asset_bytes"], path.stat().st_size)
            self.assertLess(asset["asset_bytes"], 50 * 1024 * 1024)
        self.assertEqual(len(payload["metadata"]["trial_identity"]["recording_ids"]), 457)
        self.assertEqual(len(payload["metadata"]["bilateral_pairs"]), 12)


if __name__ == "__main__":
    unittest.main()
