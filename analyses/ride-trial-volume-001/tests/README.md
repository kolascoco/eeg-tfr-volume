# Test map

Automated tests live at `../../../tests/test_ride_volume.py`. Run the complete
repository suite with:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src MPLCONFIGDIR=/tmp/mpl-eeg \
  python3 -m unittest discover -v tests
```

The 2026-10-07 validation run passed all six repository tests.
