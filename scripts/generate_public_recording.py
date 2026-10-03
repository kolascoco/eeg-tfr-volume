#!/usr/bin/env python3
"""Generate GitHub Pages viewers from the repository owner's EEG recording."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eeg_tfr_volume import BuildConfig, compute_tfr_volume, write_viewer  # noqa: E402


EVENT_PAGES = (
    ("11/3", "index.html"),
    ("11/100", "event-11-100.html"),
    ("11/200", "event-11-200.html"),
)


def main() -> None:
    fif = ROOT / "data" / "NS_MI_TS_raw.fif"
    if not fif.is_file() or fif.stat().st_size < 1_000_000:
        raise SystemExit(
            "data/NS_MI_TS_raw.fif is missing or is only a Git LFS pointer; "
            "run `git lfs pull` first"
        )

    public_pages = [
        {"event": event, "label": f"Event {event}", "href": filename}
        for event, filename in EVENT_PAGES
    ]
    for event, filename in EVENT_PAGES:
        config = BuildConfig(
            input=str(fif),
            event=event,
            tmin=-0.4,
            tmax=2.0,
            fmin=4.0,
            fmax=40.0,
            n_freqs=24,
            frequency_scale="log",
            cycles=3.0,
            time_step=0.025,
            epoch_batch_size=4,
        )
        volume, times, freqs, channels, metadata = compute_tfr_volume(config)
        # Keep public provenance reproducible without exposing a local filesystem path.
        metadata["input"]["path"] = "data/NS_MI_TS_raw.fif"
        metadata["config"]["input"] = "data/NS_MI_TS_raw.fif"
        metadata["public_event_pages"] = public_pages
        output = ROOT / "docs" / filename
        write_viewer(output, volume, times, freqs, channels, metadata)
        print(f"{event}: {output}")


if __name__ == "__main__":
    main()
