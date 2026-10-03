#!/usr/bin/env python3
"""Build an interactive channel x time x frequency EEG power volume.

Signal processing is performed with MNE-Python.  The generated viewer is a
self-contained HTML file with a small canvas renderer and no Python/web-server
dependency.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import http.server
import json
import math
import os
import platform
import re
import shutil
import sys
import time
import urllib.parse
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from string import Template
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import mne
import numpy as np


MAX_UPLOAD_BYTES = 8 * 1024**3


@dataclass(frozen=True)
class BuildConfig:
    input: str
    event: str
    tmin: float = -0.4
    tmax: float = 2.0
    fmin: float = 4.0
    fmax: float = 80.0
    n_freqs: int = 30
    frequency_scale: str = "log"
    cycles: float = 3.0
    time_step: float = 0.02
    baseline_start: float = -0.4
    baseline_end: float = 0.0
    baseline_mode: str = "logratio"
    aggregate: str = "mean"
    epoch_batch_size: int = 8
    average_reference: bool = False
    reject_peak_to_peak_uv: Optional[float] = None
    n_jobs: int = 1


def _sha256(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(block_size)
            if not block:
                return digest.hexdigest()
            digest.update(block)


def inspect_files(paths: Sequence[Path], hash_files: bool = False) -> List[dict]:
    """Return a metadata-only inventory; EEG samples are not preloaded."""
    rows: List[dict] = []
    for path in paths:
        raw = mne.io.read_raw_fif(path, preload=False, verbose="ERROR")
        events, event_id = mne.events_from_annotations(raw, verbose="ERROR")
        counts = {
            label: int(np.sum(events[:, 2] == code))
            for label, code in event_id.items()
        }
        row = {
            "path": str(path.resolve()),
            "bytes": int(path.stat().st_size),
            "sha256": _sha256(path) if hash_files else None,
            "sfreq_hz": float(raw.info["sfreq"]),
            "duration_s": float(raw.times[-1]),
            "n_channels": len(raw.ch_names),
            "channel_types": sorted(set(raw.get_channel_types())),
            "bad_channels": list(raw.info["bads"]),
            "event_counts": counts,
        }
        rows.append(row)
    return rows


def _frequencies(config: BuildConfig) -> np.ndarray:
    if config.frequency_scale == "log":
        return np.geomspace(config.fmin, config.fmax, config.n_freqs)
    return np.linspace(config.fmin, config.fmax, config.n_freqs)


def _validate_config(config: BuildConfig, sfreq: float) -> None:
    if config.tmin >= config.tmax:
        raise ValueError("tmin must be smaller than tmax")
    if not (config.tmin <= config.baseline_start < config.baseline_end <= config.tmax):
        raise ValueError("baseline must be ordered and lie within the epoch")
    if config.fmin <= 0 or config.fmin >= config.fmax:
        raise ValueError("frequencies must satisfy 0 < fmin < fmax")
    if config.fmax >= sfreq / 2:
        raise ValueError(f"fmax must be below Nyquist ({sfreq / 2:g} Hz)")
    if config.time_step < 1 / sfreq:
        raise ValueError("time-step cannot be smaller than one input sample")
    if config.n_freqs < 2:
        raise ValueError("n-freqs must be at least 2")
    if config.cycles <= 0:
        raise ValueError("cycles must be positive")
    if config.epoch_batch_size < 1:
        raise ValueError("epoch-batch-size must be positive")


def _posterior_anterior_order(raw: mne.io.BaseRaw) -> Tuple[List[str], str, List[Optional[float]]]:
    """Return EEG channels ordered from occipital/posterior to frontal/anterior."""
    names = list(raw.ch_names)
    y = np.asarray([channel["loc"][1] for channel in raw.info["chs"]], dtype=float)
    valid = np.isfinite(y) & (np.abs(y) > 1e-9)
    if int(valid.sum()) >= max(4, int(0.8 * len(names))):
        # In MNE head coordinates +y is anterior, so ascending y is O -> F.
        order = sorted(range(len(names)), key=lambda index: (not valid[index], y[index], names[index].casefold()))
        return [names[index] for index in order], "sensor_y_coordinate", [float(y[index]) for index in order]

    def region_rank(name: str) -> Tuple[int, str]:
        normalized = name.casefold().replace(".", "")
        ranks = (
            ("i", 0), ("o", 1), ("po", 2), ("p", 3), ("cp", 4),
            ("c", 5), ("fc", 6), ("f", 7), ("af", 8), ("fp", 9),
        )
        # Longest prefixes first prevents F from capturing FC/FP.
        matches = [(rank, prefix) for prefix, rank in ranks if normalized.startswith(prefix)]
        rank = max(matches, key=lambda item: len(item[1]))[0] if matches else 10
        return rank, normalized

    order = sorted(range(len(names)), key=lambda index: region_rank(names[index]))
    return [names[index] for index in order], "channel_name_heuristic", [None] * len(order)


def compute_tfr_volume(config: BuildConfig) -> Tuple[np.ndarray, np.ndarray, np.ndarray, List[str], dict]:
    """Epoch a FIF recording and aggregate Morlet power in bounded memory."""
    started = time.time()
    input_path = Path(config.input)
    raw = mne.io.read_raw_fif(input_path, preload=False, verbose="ERROR")
    _validate_config(config, float(raw.info["sfreq"]))

    raw.pick("eeg", exclude="bads")
    ordered_channels, channel_sort_method, channel_y = _posterior_anterior_order(raw)
    raw.reorder_channels(ordered_channels)
    if config.average_reference:
        raw.load_data()
        raw.set_eeg_reference("average", projection=False, verbose="ERROR")

    events, event_id = mne.events_from_annotations(raw, verbose="ERROR")
    if config.event not in event_id:
        available = ", ".join(sorted(event_id))
        raise ValueError(f"event {config.event!r} not found; choose one of: {available}")

    reject = None
    if config.reject_peak_to_peak_uv is not None:
        reject = {"eeg": config.reject_peak_to_peak_uv * 1e-6}
    epochs = mne.Epochs(
        raw,
        events,
        event_id={config.event: event_id[config.event]},
        tmin=config.tmin,
        tmax=config.tmax,
        baseline=None,
        picks="eeg",
        preload=False,
        reject=reject,
        reject_by_annotation=True,
        detrend=None,
        verbose="ERROR",
    )
    epochs.drop_bad(verbose="ERROR")
    if len(epochs) == 0:
        raise RuntimeError("no epochs remain after boundary/annotation/rejection checks")

    sfreq = float(epochs.info["sfreq"])
    decim = max(1, int(round(config.time_step * sfreq)))
    freqs = _frequencies(config)
    n_cycles = np.full(freqs.shape, config.cycles, dtype=float)
    total: Optional[np.ndarray] = None
    seen = 0

    if config.aggregate == "median":
        raise ValueError(
            "median aggregation is intentionally unavailable: exact median would "
            "materialize the full epoch tensor. Use mean for bounded-memory processing."
        )

    for start in range(0, len(epochs), config.epoch_batch_size):
        stop = min(start + config.epoch_batch_size, len(epochs))
        data = epochs[start:stop].get_data(copy=True)
        power = mne.time_frequency.tfr_array_morlet(
            data,
            sfreq=sfreq,
            freqs=freqs,
            n_cycles=n_cycles,
            output="power",
            use_fft=True,
            decim=decim,
            n_jobs=config.n_jobs,
            zero_mean=True,
            verbose="ERROR",
        )
        batch_sum = power.sum(axis=0, dtype=np.float64)
        total = batch_sum if total is None else total + batch_sum
        seen += power.shape[0]

    assert total is not None
    volume = total / seen
    times = epochs.times[::decim]
    mne.baseline.rescale(
        volume,
        times,
        baseline=(config.baseline_start, config.baseline_end),
        mode=config.baseline_mode,
        copy=False,
        verbose="ERROR",
    )
    if not np.all(np.isfinite(volume)):
        bad_fraction = float(1 - np.isfinite(volume).mean())
        raise RuntimeError(f"TFR contains non-finite values (fraction={bad_fraction:.6f})")

    metadata = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "software": {
            "python": platform.python_version(),
            "mne": mne.__version__,
            "numpy": np.__version__,
        },
        "config": asdict(config),
        "input": {
            "path": str(input_path.resolve()),
            "bytes": int(input_path.stat().st_size),
            "sha256": _sha256(input_path),
        },
        "event_code": int(event_id[config.event]),
        "n_events_found": int(np.sum(events[:, 2] == event_id[config.event])),
        "n_epochs_used": int(seen),
        "n_epochs_dropped": int(np.sum(events[:, 2] == event_id[config.event]) - seen),
        "channels": list(epochs.ch_names),
        "channel_axis": {
            "direction": "posterior_to_anterior",
            "landmarks": ["O", "P", "C", "F"],
            "sort_method": channel_sort_method,
            "head_y_m": channel_y,
        },
        "shape": list(volume.shape),
        "units": "log10(power / baseline)" if config.baseline_mode == "logratio" else config.baseline_mode,
        "runtime_s": round(time.time() - started, 3),
    }
    return volume.astype(np.float32), times.astype(np.float32), freqs.astype(np.float32), list(epochs.ch_names), metadata


def _encode_volume(volume: np.ndarray) -> dict:
    """Quantize to uint8 for a compact, browser-friendly embedded payload."""
    low, high = np.percentile(volume, [1.0, 99.0])
    if not np.isfinite(low) or not np.isfinite(high) or high <= low:
        raise RuntimeError("volume has a degenerate display range")
    scaled = np.clip((volume - low) / (high - low), 0, 1)
    quantized = np.rint(scaled * 255).astype(np.uint8)
    return {
        "shape": list(volume.shape),
        "low": float(low),
        "high": float(high),
        "data": base64.b64encode(quantized.tobytes(order="C")).decode("ascii"),
    }


def write_viewer(
    output: Path,
    volume: np.ndarray,
    times: np.ndarray,
    freqs: np.ndarray,
    channels: Sequence[str],
    metadata: dict,
) -> None:
    template_path = Path(__file__).with_name("viewer_template.html")
    if not template_path.exists():
        raise FileNotFoundError(f"viewer template not found: {template_path}")
    payload = {
        "volume": _encode_volume(volume),
        "times": [round(float(x), 6) for x in times],
        "freqs": [round(float(x), 6) for x in freqs],
        "channels": list(channels),
        "metadata": metadata,
    }
    html = Template(template_path.read_text(encoding="utf-8")).safe_substitute(
        PAYLOAD=json.dumps(payload, separators=(",", ":"))
    )
    output.write_text(html, encoding="utf-8")


def _safe_stem(value: str) -> str:
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(value).stem).strip("-.")
    return stem[:100] or "eeg"


def serve_app(host: str, port: int, work_dir: Path) -> None:
    """Serve a localhost upload/event-selection UI backed by MNE processing."""
    work_dir = work_dir.resolve()
    uploads_dir = work_dir / "uploads"
    outputs_dir = work_dir / "outputs"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)
    app_path = Path(__file__).with_name("app_template.html")
    if not app_path.exists():
        raise FileNotFoundError(f"app template not found: {app_path}")
    app_html = app_path.read_bytes()

    class Handler(http.server.BaseHTTPRequestHandler):
        server_version = "EEGVolume/1.0"

        def log_message(self, fmt: str, *args: object) -> None:
            print(f"[{self.log_date_time_string()}] {fmt % args}")

        def _send_bytes(self, status: int, data: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _send_json(self, status: int, payload: dict) -> None:
            self._send_bytes(status, json.dumps(payload).encode("utf-8"), "application/json; charset=utf-8")

        def _error(self, status: int, exc: object) -> None:
            self._send_json(status, {"error": str(exc)})

        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                self._send_bytes(200, app_html, "text/html; charset=utf-8")
                return
            if parsed.path.startswith("/viewer/"):
                name = Path(urllib.parse.unquote(parsed.path[len("/viewer/"):])).name
                candidate = outputs_dir / name
                if candidate.is_file() and candidate.suffix == ".html":
                    self._send_bytes(200, candidate.read_bytes(), "text/html; charset=utf-8")
                else:
                    self._error(404, "viewer not found")
                return
            self._error(404, "not found")

        def do_POST(self) -> None:  # noqa: N802 - stdlib handler API
            parsed = urllib.parse.urlparse(self.path)
            try:
                if parsed.path == "/api/inspect":
                    self._inspect_upload(parsed)
                elif parsed.path == "/api/build":
                    self._build_viewer()
                else:
                    self._error(404, "not found")
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception as exc:
                self._error(400, exc)

        def _inspect_upload(self, parsed: urllib.parse.ParseResult) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                raise ValueError("empty upload")
            if length > MAX_UPLOAD_BYTES:
                raise ValueError("file exceeds the 8 GiB local upload limit")
            query = urllib.parse.parse_qs(parsed.query)
            original_name = Path(query.get("name", ["recording_raw.fif"])[0]).name
            if not original_name.lower().endswith(".fif"):
                raise ValueError("choose an MNE FIF file ending in .fif")
            upload_id = uuid.uuid4().hex
            destination = uploads_dir / f"{upload_id}-{_safe_stem(original_name)}.fif"
            remaining = length
            with destination.open("wb") as handle:
                while remaining:
                    block = self.rfile.read(min(1024 * 1024, remaining))
                    if not block:
                        raise IOError("upload ended before Content-Length bytes were received")
                    handle.write(block)
                    remaining -= len(block)
            try:
                info = inspect_files([destination], hash_files=False)[0]
            except Exception:
                destination.unlink(missing_ok=True)
                raise
            info["path"] = original_name
            self._send_json(200, {"upload_id": upload_id, "file": info})

        def _build_viewer(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 128 * 1024:
                raise ValueError("invalid build request")
            request = json.loads(self.rfile.read(length))
            upload_id = str(request.get("upload_id", ""))
            if not re.fullmatch(r"[0-9a-f]{32}", upload_id):
                raise ValueError("invalid upload id")
            matches = list(uploads_dir.glob(f"{upload_id}-*.fif"))
            if len(matches) != 1:
                raise ValueError("uploaded recording was not found")
            event = str(request.get("event", ""))
            if not event:
                raise ValueError("choose an epoch event")
            config = BuildConfig(
                input=str(matches[0]),
                event=event,
                tmin=float(request.get("tmin", -0.4)),
                tmax=float(request.get("tmax", 2.0)),
                fmin=float(request.get("fmin", 4.0)),
                fmax=float(request.get("fmax", 80.0)),
                n_freqs=int(request.get("n_freqs", 30)),
                cycles=float(request.get("cycles", 3.0)),
                time_step=float(request.get("time_step", 0.02)),
                baseline_start=float(request.get("baseline_start", -0.4)),
                baseline_end=float(request.get("baseline_end", 0.0)),
                average_reference=bool(request.get("average_reference", False)),
                reject_peak_to_peak_uv=(
                    float(request["reject_peak_to_peak_uv"])
                    if request.get("reject_peak_to_peak_uv") not in (None, "")
                    else None
                ),
                n_jobs=max(1, int(request.get("n_jobs", 1))),
            )
            volume, times, freqs, channels, metadata = compute_tfr_volume(config)
            output_name = f"{_safe_stem(matches[0].name)}-{_safe_stem(event)}-tfr-volume.html"
            output = outputs_dir / output_name
            write_viewer(output, volume, times, freqs, channels, metadata)
            cache = output.with_suffix(".npz")
            np.savez_compressed(
                cache,
                power=volume,
                times=times,
                freqs=freqs,
                channels=np.asarray(channels),
                metadata=json.dumps(metadata),
            )
            self._send_json(
                200,
                {
                    "viewer_url": f"/viewer/{urllib.parse.quote(output.name)}",
                    "viewer_path": str(output),
                    "cache_path": str(cache),
                    "n_epochs_used": metadata["n_epochs_used"],
                },
            )

    server = http.server.ThreadingHTTPServer((host, port), Handler)
    print(f"EEG volume app: http://{host}:{server.server_port}")
    print(f"Local work directory: {work_dir}")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping EEG volume app.")
    finally:
        server.server_close()


def _expand_inputs(items: Sequence[str], exclude_clean: bool) -> List[Path]:
    paths: List[Path] = []
    for item in items:
        candidate = Path(item)
        if candidate.is_dir():
            matches = sorted(candidate.glob("*.fif"))
        else:
            matches = sorted(candidate.parent.glob(candidate.name))
        for match in matches:
            if exclude_clean and "_clean" in match.stem:
                continue
            if match not in paths:
                paths.append(match)
    return paths


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_p = sub.add_parser("inspect", help="inventory FIF metadata and annotation events")
    inspect_p.add_argument("inputs", nargs="+", help="FIF path, glob, or directory")
    inspect_p.add_argument("--exclude-clean", action="store_true", help="skip names containing _clean")
    inspect_p.add_argument("--hash", action="store_true", help="compute SHA-256 (slow for large files)")
    inspect_p.add_argument("--output", type=Path, help="write JSON instead of stdout")

    build = sub.add_parser("build", help="compute one event-locked TFR volume and HTML viewer")
    build.add_argument("input", type=Path)
    build.add_argument("--event", required=True, help="annotation label, e.g. 11/3")
    build.add_argument("--output", type=Path, default=Path("eeg-tfr-volume.html"))
    build.add_argument("--cache", type=Path, help="optional compressed NPZ with full float32 volume")
    build.add_argument("--tmin", type=float, default=-0.4)
    build.add_argument("--tmax", type=float, default=2.0)
    build.add_argument("--fmin", type=float, default=4.0)
    build.add_argument("--fmax", type=float, default=80.0)
    build.add_argument("--n-freqs", type=int, default=30)
    build.add_argument("--frequency-scale", choices=["linear", "log"], default="log")
    build.add_argument("--cycles", type=float, default=3.0)
    build.add_argument("--time-step", type=float, default=0.02, help="viewer time resolution in seconds")
    build.add_argument("--baseline", nargs=2, type=float, default=(-0.4, 0.0), metavar=("START", "END"))
    build.add_argument(
        "--baseline-mode",
        choices=["mean", "ratio", "logratio", "percent", "zscore", "zlogratio"],
        default="logratio",
    )
    build.add_argument("--epoch-batch-size", type=int, default=8)
    build.add_argument("--average-reference", action="store_true")
    build.add_argument("--reject-peak-to-peak-uv", type=float)
    build.add_argument("--n-jobs", type=int, default=1)

    serve = sub.add_parser("serve", help="start the local upload and event-selection web app")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--work-dir", type=Path, default=Path("eeg-volume-work"))
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(argv)
    mne.set_log_level("WARNING")
    if args.command == "inspect":
        paths = _expand_inputs(args.inputs, args.exclude_clean)
        if not paths:
            raise SystemExit("no FIF inputs matched")
        report = inspect_files(paths, hash_files=args.hash)
        text = json.dumps(report, indent=2)
        if args.output:
            args.output.write_text(text + "\n", encoding="utf-8")
            print(args.output.resolve())
        else:
            print(text)
        return 0

    if args.command == "serve":
        serve_app(args.host, args.port, args.work_dir)
        return 0

    config = BuildConfig(
        input=str(args.input),
        event=args.event,
        tmin=args.tmin,
        tmax=args.tmax,
        fmin=args.fmin,
        fmax=args.fmax,
        n_freqs=args.n_freqs,
        frequency_scale=args.frequency_scale,
        cycles=args.cycles,
        time_step=args.time_step,
        baseline_start=args.baseline[0],
        baseline_end=args.baseline[1],
        baseline_mode=args.baseline_mode,
        epoch_batch_size=args.epoch_batch_size,
        average_reference=args.average_reference,
        reject_peak_to_peak_uv=args.reject_peak_to_peak_uv,
        n_jobs=args.n_jobs,
    )
    volume, times, freqs, channels, metadata = compute_tfr_volume(config)
    write_viewer(args.output, volume, times, freqs, channels, metadata)
    if args.cache:
        np.savez_compressed(
            args.cache,
            power=volume,
            times=times,
            freqs=freqs,
            channels=np.asarray(channels),
            metadata=json.dumps(metadata),
        )
    print(json.dumps({"viewer": str(args.output.resolve()), "metadata": metadata}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
