#!/usr/bin/env python3
"""Generate full-resolution C3 trial-time comparisons for RIDE recordings."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np
import scipy
from scipy.io import loadmat


ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = Path(__file__).resolve().parents[1]
RESULTS = ANALYSIS / "results"
CHANNELS = ["F3", "F4", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6", "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6", "P3", "Pz", "P4", "O1", "O2"]
COMPONENTS = (("S", "stS"), ("C", "stC"), ("R", "stR"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_recording(path: Path) -> dict:
    started = time.perf_counter()
    result = loadmat(path, squeeze_me=True, struct_as_record=False)["results"]
    cfg = result.cfg
    start_ms, stop_ms = map(float, np.asarray(cfg.epoch_twd).reshape(-1))
    step_ms = float(cfg.samp_interval)
    sfreq = 1000.0 / step_ms
    arrays = {}
    source_shape = None
    for key, field in COMPONENTS:
        value = np.asarray(getattr(result, field), dtype=np.float64)
        if value.ndim != 3 or not np.all(np.isfinite(value)):
            raise ValueError(f"{path.name}:{field} invalid shape/values")
        if source_shape is None:
            source_shape = value.shape
        elif value.shape != source_shape:
            raise ValueError(f"{path.name}: component shape mismatch")
        arrays[key] = np.transpose(value, (2, 1, 0))
    n_times, n_channels, n_trials = source_shape
    if n_channels != len(CHANNELS):
        raise ValueError(f"{path.name}: {n_channels} channels, expected {len(CHANNELS)}")
    times_ms = start_ms + np.arange(n_times) * step_ms
    if not np.isclose(times_ms[-1], stop_ms) or np.flatnonzero(np.isclose(times_ms, 0)).size != 1:
        raise ValueError(f"{path.name}: invalid time axis")
    latency0 = np.asarray(result.latency0, dtype=object).reshape(-1)
    rt = np.asarray(latency0[2], dtype=np.float64).reshape(-1)
    if rt.size != n_trials or not np.all(np.isfinite(rt)) or np.any(rt < start_ms) or np.any(rt > stop_ms):
        raise ValueError(f"{path.name}: invalid behavioral RT")
    order = np.argsort(rt, kind="stable")
    if not np.array_equal(np.sort(order), np.arange(n_trials)) or np.any(np.diff(rt[order]) < 0):
        raise ValueError(f"{path.name}: invalid RT permutation")
    info = mne.create_info(CHANNELS, sfreq=sfreq, ch_types=["eeg"] * n_channels)
    c3 = {}
    for key, _ in COMPONENTS:
        epochs = mne.EpochsArray(arrays[key], info, tmin=start_ms / 1000.0, verbose=False)
        # MNE receives all trials/channels/times; only the requested channel is selected.
        c3[key] = epochs.get_data(picks=["C3"], copy=True)[:, 0, :] * 1e6
    stem = path.stem.replace("_RIDE_result", "")
    subject, condition = stem.split("_", 1)
    return {
        "name": stem, "subject": subject, "condition": condition, "path": path,
        "sha256": sha256(path), "times_ms": times_ms, "rt_ms": rt,
        "order": order, "c3_uv": c3, "shape": list(source_shape),
        "runtime_s": time.perf_counter() - started,
    }


def render(records: list[dict]) -> dict:
    RESULTS.mkdir(parents=True, exist_ok=True)
    all_values = np.concatenate([record["c3_uv"][key].ravel() for record in records for key, _ in COMPONENTS])
    limit = float(np.percentile(np.abs(all_values), 99.5))
    rows = []
    for record in records:
        component_scores = {}
        for key, _ in COMPONENTS:
            value = record["c3_uv"][key]
            score = float(np.percentile(np.abs(value), 99.0))
            component_scores[key] = score
            rows.append({
                "recording": record["name"], "subject": record["subject"], "condition": record["condition"],
                "component": key, "trials": value.shape[0], "times": value.shape[1],
                "q99_abs_uv": score, "rms_uv": float(np.sqrt(np.mean(value ** 2))),
                "minimum_uv": float(value.min()), "maximum_uv": float(value.max()),
                "saturated_percent": float(np.mean(np.abs(value) > limit) * 100),
            })
        record["score_uv"] = max(component_scores.values())

    fig, axes = plt.subplots(len(records), 3, figsize=(17, 14), constrained_layout=True, sharex=True)
    image = None
    for row_index, record in enumerate(records):
        order = record["order"]
        times = record["times_ms"]
        for col_index, (key, _) in enumerate(COMPONENTS):
            ax = axes[row_index, col_index]
            matrix = record["c3_uv"][key][order]
            image = ax.imshow(matrix, origin="lower", aspect="auto", interpolation="none",
                              extent=[times[0], times[-1], 1, matrix.shape[0]],
                              cmap="RdBu_r", vmin=-limit, vmax=limit, rasterized=True)
            ax.axvline(0, color="#ffb26b", linewidth=1.3)
            ax.plot(record["rt_ms"][order], np.arange(1, matrix.shape[0] + 1),
                    color="#171717", linewidth=1.2, alpha=.9)
            if row_index == 0:
                ax.set_title(f"{key} component")
            if col_index == 0:
                ax.set_ylabel(f"{record['name']}\nRT-sorted trial")
            if row_index == len(records) - 1:
                ax.set_xlabel("Stimulus-relative time (ms)")
    colorbar = fig.colorbar(image, ax=axes, shrink=.75, pad=.015)
    colorbar.set_label("C3 amplitude (µV); shared 99.5th-percentile range")
    fig.suptitle("Full-resolution C3 RIDE components · black curve = behavioral RT", fontsize=16)
    heatmap_path = RESULTS / "c3_all_recordings_heatmaps.png"
    fig.savefig(heatmap_path, dpi=180, facecolor="white")
    plt.close(fig)

    fig, axes = plt.subplots(3, 1, figsize=(13, 10), constrained_layout=True, sharex=True)
    colors = plt.cm.tab10(np.linspace(0, 1, len(records)))
    for ax, (key, _) in zip(axes, COMPONENTS):
        for color, record in zip(colors, records):
            waveform = record["c3_uv"][key].mean(axis=0)
            ax.plot(record["times_ms"], waveform, label=record["name"], color=color, linewidth=1.8)
        ax.axvline(0, color="black", linestyle=":", linewidth=1)
        ax.axhline(0, color="black", linestyle=":", linewidth=1)
        ax.set_ylabel(f"{key} · C3 (µV)")
        ax.legend(ncol=4, frameon=False)
    axes[-1].set_xlabel("Stimulus-relative time (ms)")
    fig.suptitle("C3 trial-mean RIDE waveforms · no filtering or decimation", fontsize=15)
    waveform_path = RESULTS / "c3_mean_waveforms.png"
    fig.savefig(waveform_path, dpi=180, facecolor="white")
    plt.close(fig)

    metrics_path = RESULTS / "c3_metrics.csv"
    with metrics_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    ranking = sorted(({"recording": r["name"], "score_uv": r["score_uv"]} for r in records), key=lambda item: item["score_uv"], reverse=True)
    summary = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "software": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "mne": mne.__version__, "matplotlib": matplotlib.__version__},
        "channel": "C3", "channel_index_zero_based": CHANNELS.index("C3"),
        "shared_limit_uv": [-limit, limit], "ranking": ranking,
        "inputs": [{"name": r["name"], "sha256": r["sha256"], "shape_time_channels_trials": r["shape"], "runtime_s": r["runtime_s"]} for r in records],
        "processing": "All trials and all 1751 samples; no filtering, baseline, resampling, smoothing, interpolation, or decimation.",
    }
    (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    paths = sorted((ROOT / "data").glob("*_RIDE_result.mat"))
    if len(paths) != 4:
        raise SystemExit(f"Expected exactly four RIDE MAT files, found {len(paths)}")
    records = [load_recording(path) for path in paths]
    summary = render(records)
    print(json.dumps(summary["ranking"], indent=2))


if __name__ == "__main__":
    main()
