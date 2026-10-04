import json
import tempfile
import unittest
from pathlib import Path

import mne
import numpy as np

from eeg_tfr_volume import BuildConfig, compute_tfr_volume, write_viewer


class TestEEGTFRVolume(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        sfreq = 100.0
        info = mne.create_info(["C3", "Cz", "C4"], sfreq, ch_types="eeg")
        rng = np.random.default_rng(7)
        data = rng.normal(scale=2e-6, size=(3, 1200))
        times = np.arange(data.shape[1]) / sfreq
        envelope = ((times >= 2.0) & (times < 2.8)).astype(float)
        data[0] += 8e-6 * np.sin(2 * np.pi * 10 * times) * envelope
        raw = mne.io.RawArray(data, info, verbose="ERROR")
        raw.set_annotations(mne.Annotations([2.0, 6.0], [0, 0], ["stim", "other"]))
        self.fif = Path(self.tmp.name) / "synthetic_raw.fif"
        raw.save(self.fif, overwrite=True, verbose="ERROR")

    def tearDown(self):
        self.tmp.cleanup()

    def config(self, event="stim"):
        return BuildConfig(
            input=str(self.fif), event=event, tmin=-0.4, tmax=2.0,
            fmin=5, fmax=30, n_freqs=6, frequency_scale="linear",
            cycles=2, time_step=0.05, epoch_batch_size=1,
        )

    def test_compute_shape_coordinates_and_finite_values(self):
        volume, times, freqs, channels, meta = compute_tfr_volume(self.config())
        self.assertEqual(volume.shape, (3, 6, len(times)))
        self.assertEqual(channels, ["C3", "C4", "Cz"])
        self.assertAlmostEqual(float(times[0]), -0.4, places=6)
        self.assertAlmostEqual(float(times[-1]), 2.0, places=6)
        self.assertTrue(np.allclose(freqs, np.linspace(5, 30, 6)))
        self.assertTrue(np.isfinite(volume).all())
        baseline = (times >= -0.4) & (times <= 0)
        # MNE logratio is log10(power / arithmetic baseline mean), so its
        # inverse—not the mean of the logarithms—must average to one.
        self.assertLess(abs(float(np.power(10.0, volume[..., baseline]).mean()) - 1.0), 1e-5)
        self.assertEqual(meta["n_epochs_used"], 1)

    def test_unknown_event_fails_with_available_labels(self):
        with self.assertRaisesRegex(ValueError, "choose one of"):
            compute_tfr_volume(self.config("missing"))

    def test_html_contains_embedded_payload(self):
        volume, times, freqs, channels, meta = compute_tfr_volume(self.config())
        output = Path(self.tmp.name) / "viewer.html"
        write_viewer(output, volume, times, freqs, channels, meta)
        text = output.read_text(encoding="utf-8")
        self.assertIn("Interactive EEG channel time frequency volume", text)
        self.assertNotIn("$PAYLOAD", text)
        self.assertIn('"channels":["C3","C4","Cz"]', text)
        self.assertIn('value="cubic" selected', text)
        self.assertIn("function cubic1", text)
        self.assertIn('id="eventPage"', text)
        self.assertIn("box(w,h,...extents)", text)
        self.assertIn("channelLandmarkTicks", text)
        self.assertIn("G[gidx(ci,fi,0)]", text)
        self.assertIn('id="opacity"', text)
        self.assertIn("Fill the cuboid", text)


if __name__ == "__main__":
    unittest.main()
