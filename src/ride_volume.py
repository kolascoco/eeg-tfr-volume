#!/usr/bin/env python3
"""Build a self-contained trial × channel × time RIDE volume viewer."""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import platform
import time
from pathlib import Path
from string import Template
from typing import Dict, Optional, Sequence, Tuple

import numpy as np
import scipy
import mne
from scipy.io import loadmat


COMPONENTS = (
    ("S", "stS", "Stimulus-locked component cluster (S component)"),
    ("C", "stC", "Non-marker-locked component cluster (C component)"),
    ("R", "stR", "Response-locked component cluster (R component)"),
)

PUBLISHED_COMPONENTS = ("S", "R")

BILATERAL_PAIRS = (
    ("F3", "F4"),
    ("FC5", "FC6"), ("FC3", "FC4"), ("FC1", "FC2"),
    ("C5", "C6"), ("C3", "C4"), ("C1", "C2"),
    ("CP5", "CP6"), ("CP3", "CP4"), ("CP1", "CP2"),
    ("P3", "P4"), ("O1", "O2"),
)

CHANNELS = [
    "F3", "F4", "FC5", "FC3", "FC1", "FCz", "FC2", "FC4", "FC6",
    "C5", "C3", "C1", "Cz", "C2", "C4", "C6", "CP5", "CP3", "CP1",
    "CPz", "CP2", "CP4", "CP6", "P3", "Pz", "P4", "O1", "O2",
]


def _sha256(path: Path, block_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_vector(value: object, name: str, length: int) -> np.ndarray:
    array = np.asarray(value).reshape(-1)
    if array.size != length:
        raise ValueError(f"{name} has length {array.size}; expected {length}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values")
    return array


def filter_ride_components(
    components: Dict[str, np.ndarray],
    sfreq: float,
    l_freq: float,
    h_freq: float,
    iir_order: int = 4,
) -> Dict[str, np.ndarray]:
    """Band-pass each trial/channel time course with MNE, preserving shape."""
    if not 0 < l_freq < h_freq < sfreq / 2:
        raise ValueError("filter frequencies must satisfy 0 < l_freq < h_freq < Nyquist")
    filtered = {}
    iir_params = {"order": iir_order, "ftype": "butter", "output": "sos"}
    for key, values in components.items():
        result = mne.filter.filter_data(
            np.asarray(values, dtype=np.float64),
            sfreq=sfreq,
            l_freq=l_freq,
            h_freq=h_freq,
            method="iir",
            iir_params=iir_params,
            phase="zero",
            pad="reflect_limited",
            verbose=False,
        )
        if result.shape != values.shape or not np.all(np.isfinite(result)):
            raise ValueError(f"filtered {key} has invalid shape or values")
        filtered[key] = result.astype(np.float32)
    return filtered


def load_ride_components(
    path: Path,
    l_freq: Optional[float] = None,
    h_freq: Optional[float] = None,
    iir_order: int = 4,
) -> Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray, Sequence[str], dict]:
    """Load, validate, and optionally filter RIDE single-trial components."""
    started = time.time()
    result = loadmat(path, squeeze_me=True, struct_as_record=False)["results"]

    arrays: Dict[str, np.ndarray] = {}
    source_shape = None
    for key, field, _ in COMPONENTS:
        source = np.asarray(getattr(result, field), dtype=np.float64)
        if source.ndim != 3:
            raise ValueError(f"results.{field} must be 3-D, got {source.shape}")
        if source_shape is None:
            source_shape = source.shape
        elif source.shape != source_shape:
            raise ValueError(f"component shape mismatch: {field}={source.shape}, expected {source_shape}")
        if not np.all(np.isfinite(source)):
            raise ValueError(f"results.{field} contains non-finite values")
        # MATLAB stores time × channels × trials. The viewer consumes trials × channels × time.
        arrays[key] = np.transpose(source, (2, 1, 0)).astype(np.float32, copy=False)

    assert source_shape is not None
    n_times, n_channels, n_trials = source_shape
    cfg = result.cfg
    start_ms, stop_ms = map(float, np.asarray(cfg.epoch_twd).reshape(-1))
    step_ms = float(cfg.samp_interval)
    sfreq = 1000.0 / step_ms
    times_ms = start_ms + np.arange(n_times, dtype=np.float64) * step_ms
    if not np.isclose(times_ms[-1], stop_ms):
        raise ValueError(
            f"time configuration produces {times_ms[-1]:g} ms, expected {stop_ms:g} ms"
        )
    zero_indices = np.flatnonzero(np.isclose(times_ms, 0.0))
    if zero_indices.size != 1:
        raise ValueError("time axis must contain exactly one 0-ms stimulus sample")

    latency0 = np.asarray(result.latency0, dtype=object).reshape(-1)
    if latency0.size < 3:
        raise ValueError("results.latency0 does not contain the behavioral RT vector")
    response_times_ms = _require_vector(latency0[2], "results.latency0[2]", n_trials).astype(
        np.float32
    )
    if np.any(response_times_ms < times_ms[0]) or np.any(response_times_ms > times_ms[-1]):
        raise ValueError("behavioral response times fall outside the epoch")

    if n_channels != len(CHANNELS):
        raise ValueError(f"expected {len(CHANNELS)} channels, found {n_channels}")
    channels = list(CHANNELS)
    if (l_freq is None) != (h_freq is None):
        raise ValueError("l_freq and h_freq must be provided together")
    if l_freq is not None and h_freq is not None:
        arrays = filter_ride_components(arrays, sfreq, l_freq, h_freq, iir_order)
    filtering = None if l_freq is None else {
        "tool": "mne.filter.filter_data",
        "l_freq_hz": float(l_freq),
        "h_freq_hz": float(h_freq),
        "method": "iir",
        "phase": "zero",
        "iir_params": {"order": int(iir_order), "ftype": "butter", "output": "sos"},
        "effective_order": int(iir_order) * 4,
        "effective_order_note": (
            "Band-pass transformation doubles the design order; zero-phase "
            "forward-reverse application doubles it again."
        ),
        "pad": "reflect_limited",
        "axis": "time within each trial/channel",
    }
    metadata = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "mne": mne.__version__,
        },
        "input": {
            "path": str(path),
            "bytes": int(path.stat().st_size),
            "sha256": _sha256(path),
            "matlab_variable": "results",
        },
        "source_shape_time_channels_trials": list(source_shape),
        "viewer_shape_trials_channels_time": [n_trials, n_channels, n_times],
        "time_axis": {
            "start_ms": start_ms,
            "stop_ms": stop_ms,
            "step_ms": step_ms,
            "stimulus_onset_index": int(zero_indices[0]),
            "sfreq_hz": sfreq,
            "units_status": "from_RIDE_configuration",
        },
        "response_time": {
            "field": "results.latency0[2]",
            "units": "ms",
            "units_status": "inferred_from_RIDE_configuration_and_publication",
            "minimum": float(response_times_ms.min()),
            "maximum": float(response_times_ms.max()),
            "n_unique": int(np.unique(response_times_ms).size),
        },
        "amplitude": {
            "payload_units": "microvolts",
            "source_units": "volts",
            "conversion": "source_value * 1e6",
            "units_status": "confirmed_by_data_owner_2026-10-07",
            "component_extrema_uv": {
                key: {
                    "minimum": float(array.min()) * 1e6,
                    "maximum": float(array.max()) * 1e6,
                }
                for key, array in arrays.items()
            },
        },
        "channel_labels": {
            "status": "user_directed_notebook_order",
            "labels": channels,
        },
        "trial_identity": "original 1-based MAT trial index",
        "component_fields": {key: field for key, field, _ in COMPONENTS},
        "component_titles": {key: title for key, _, title in COMPONENTS},
        "processing": {
            "filter": filtering,
            "baseline": None,
            "resample": None,
            "source_decimation": None,
            "interpolation": None,
            "presentation_note": "The browser payload contains filtered data.",
        },
        "runtime_s": round(time.time() - started, 3),
    }
    return arrays, times_ms.astype(np.float32), response_times_ms, channels, metadata


def load_ride_collection(
    paths: Sequence[Path],
    l_freq: Optional[float] = None,
    h_freq: Optional[float] = None,
    iir_order: int = 4,
) -> Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray, Sequence[str], dict]:
    """Load compatible RIDE files, filter each independently, and stack trials."""
    if not paths:
        raise ValueError("paths must contain at least one RIDE recording")
    started = time.time()
    loaded = [
        load_ride_components(Path(path), l_freq, h_freq, iir_order)
        for path in paths
    ]
    reference_times = loaded[0][1]
    reference_channels = list(loaded[0][3])
    for path, (_, times_ms, _, channels, _) in zip(paths[1:], loaded[1:]):
        if not np.array_equal(times_ms, reference_times):
            raise ValueError(f"time axis mismatch in {path}")
        if list(channels) != reference_channels:
            raise ValueError(f"channel order mismatch in {path}")

    arrays = {
        key: np.concatenate([entry[0][key] for entry in loaded], axis=0)
        for key, _, _ in COMPONENTS
    }
    response_times_ms = np.concatenate([entry[2] for entry in loaded]).astype(
        np.float32, copy=False
    )
    recording_ids = []
    original_trial_numbers = []
    sources = []
    for path, (component_data, _, rt, _, source_metadata) in zip(paths, loaded):
        recording_id = Path(path).name.replace("_RIDE_result.mat", "")
        n_trials = int(rt.size)
        recording_ids.extend([recording_id] * n_trials)
        original_trial_numbers.extend(range(1, n_trials + 1))
        sources.append({
            **source_metadata["input"],
            "recording_id": recording_id,
            "trials": n_trials,
            "viewer_shape_trials_channels_time": list(component_data["S"].shape),
        })

    first_metadata = loaded[0][4]
    metadata = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "software": first_metadata["software"],
        "input": {
            "path": "stacked:S02_far+S04_far+S07_far",
            "dataset_label": "S02 + S04 + S07 far-condition stack",
            "sources": sources,
        },
        "source_shapes_time_channels_trials": [
            entry[4]["source_shape_time_channels_trials"] for entry in loaded
        ],
        "viewer_shape_trials_channels_time": list(arrays["S"].shape),
        "time_axis": first_metadata["time_axis"],
        "response_time": {
            "field": "results.latency0[2]",
            "units": "ms",
            "units_status": "inferred_from_RIDE_configuration_and_publication",
            "minimum": float(response_times_ms.min()),
            "maximum": float(response_times_ms.max()),
            "n_unique": int(np.unique(response_times_ms).size),
        },
        "amplitude": {
            "payload_units": "microvolts",
            "source_units": "volts",
            "conversion": "source_value * 1e6",
            "units_status": "confirmed_by_data_owner_2026-10-07",
            "component_extrema_uv": {
                key: {
                    "minimum": float(array.min()) * 1e6,
                    "maximum": float(array.max()) * 1e6,
                }
                for key, array in arrays.items()
            },
        },
        "channel_labels": first_metadata["channel_labels"],
        "trial_identity": {
            "primary_key": ["recording_id", "original_1_based_mat_trial"],
            "recording_ids": recording_ids,
            "original_1_based_mat_trial": original_trial_numbers,
            "recording_order": [source["recording_id"] for source in sources],
        },
        "component_fields": first_metadata["component_fields"],
        "component_titles": first_metadata["component_titles"],
        "processing": {
            **first_metadata["processing"],
            "stack": {
                "axis": "trial",
                "after_filtering": True,
                "recording_order": [source["recording_id"] for source in sources],
            },
            "presentation_note": "Each recording was filtered independently before trial concatenation.",
        },
        "bilateral_pairs": [list(pair) for pair in BILATERAL_PAIRS],
        "runtime_s": round(time.time() - started, 3),
    }
    return arrays, reference_times, response_times_ms, reference_channels, metadata


def _encoding_parameters(
    components: Dict[str, np.ndarray],
    percentile: float,
    microvolts_per_count: float,
) -> dict:
    if set(components) != set(PUBLISHED_COMPONENTS):
        raise ValueError("components must contain exactly S and R")
    shapes = {array.shape for array in components.values()}
    if len(shapes) != 1:
        raise ValueError(f"component shapes differ: {sorted(shapes)}")
    robust_limits_uv = [
        float(np.percentile(np.abs(array.astype(np.float64) * 1e6), percentile))
        for array in components.values()
    ]
    default_limit_uv = max(robust_limits_uv)
    max_abs_uv = max(
        float(np.max(np.abs(array.astype(np.float64) * 1e6)))
        for array in components.values()
    )
    if not np.isfinite(default_limit_uv) or default_limit_uv <= 0:
        raise ValueError("components have a degenerate display range")
    if microvolts_per_count <= 0 or max_abs_uv / microvolts_per_count > np.iinfo(np.int16).max:
        raise ValueError("microvolts_per_count cannot represent the component extrema")
    return {
        "shape": list(next(iter(components.values())).shape),
        "dtype": "int16_le",
        "microvolts_per_count": microvolts_per_count,
        "default_limit_uv": default_limit_uv,
        "max_abs_uv": max_abs_uv,
        "percentile": percentile,
    }


def encode_components(
    components: Dict[str, np.ndarray],
    percentile: float = 99.5,
    microvolts_per_count: float = 0.01,
) -> dict:
    """Encode S/R as signed int16 microvolts without display-range clipping."""
    summary = _encoding_parameters(components, percentile, microvolts_per_count)
    encoded = {}
    for key, array in components.items():
        values_uv = array.astype(np.float64) * 1e6
        quantized = np.rint(values_uv / microvolts_per_count).astype("<i2")
        encoded[key] = base64.b64encode(quantized.tobytes(order="C")).decode("ascii")
    return {**summary, "storage": "embedded_base64", "data": encoded}


def encode_components_binary(
    components: Dict[str, np.ndarray],
    output: Path,
    asset_url: str,
    percentile: float = 99.5,
    microvolts_per_count: float = 0.01,
) -> dict:
    """Write contiguous S then R signed-int16 volumes for browser streaming.

    A ``.gz`` output is compressed deterministically while retaining every
    quantized voxel. The browser expands it before constructing Int16Array
    views, so compression changes transport size rather than data shape.
    """
    summary = _encoding_parameters(components, percentile, microvolts_per_count)
    output.parent.mkdir(parents=True, exist_ok=True)
    offsets = {}
    compressed = output.suffix == ".gz"
    raw_handle = output.open("wb")
    handle = (
        gzip.GzipFile(filename="", mode="wb", fileobj=raw_handle, compresslevel=9, mtime=0)
        if compressed
        else raw_handle
    )
    uncompressed_bytes = 0
    with raw_handle, handle:
        for key in PUBLISHED_COMPONENTS:
            offsets[key] = uncompressed_bytes
            values_uv = components[key].astype(np.float64) * 1e6
            quantized = np.rint(values_uv / microvolts_per_count).astype("<i2")
            payload = quantized.tobytes(order="C")
            handle.write(payload)
            uncompressed_bytes += len(payload)
    return {
        **summary,
        "storage": "external_int16_le",
        "asset": asset_url,
        "asset_bytes": int(output.stat().st_size),
        "asset_sha256": _sha256(output),
        "compression": "gzip" if compressed else None,
        "uncompressed_bytes": uncompressed_bytes,
        "component_offsets_bytes": offsets,
    }


def encode_components_binary_split(
    components: Dict[str, np.ndarray],
    outputs: Dict[str, Path],
    asset_urls: Dict[str, str],
    percentile: float = 99.5,
    microvolts_per_count: float = 0.01,
) -> dict:
    """Write one deterministic gzip-compressed int16 asset per component."""
    summary = _encoding_parameters(components, percentile, microvolts_per_count)
    if set(outputs) != set(PUBLISHED_COMPONENTS) or set(asset_urls) != set(PUBLISHED_COMPONENTS):
        raise ValueError("split outputs and asset URLs must contain exactly S and R")
    assets = {}
    component_bytes = int(np.prod(summary["shape"])) * np.dtype("<i2").itemsize
    for key in PUBLISHED_COMPONENTS:
        output = Path(outputs[key])
        output.parent.mkdir(parents=True, exist_ok=True)
        values_uv = components[key].astype(np.float64) * 1e6
        quantized = np.rint(values_uv / microvolts_per_count).astype("<i2")
        with output.open("wb") as raw_handle:
            with gzip.GzipFile(
                filename="", mode="wb", fileobj=raw_handle, compresslevel=9, mtime=0
            ) as handle:
                handle.write(quantized.tobytes(order="C"))
        assets[key] = {
            "asset": asset_urls[key],
            "asset_bytes": int(output.stat().st_size),
            "asset_sha256": _sha256(output),
            "compression": "gzip",
            "uncompressed_bytes": component_bytes,
        }
    return {
        **summary,
        "storage": "external_int16_le_split",
        "assets": assets,
    }


def load_compact_ride_dataset(
    manifest_path: Path,
    binary_path: Optional[Path] = None,
) -> Tuple[Dict[str, np.ndarray], np.ndarray, np.ndarray, Sequence[str], dict]:
    """Load the compact, presentation-ready S/R dataset without source MATs."""
    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    volume = payload["volume"]
    if volume.get("dtype") != "int16_le":
        raise ValueError("compact dataset must use little-endian int16 storage")
    shape = tuple(int(value) for value in volume["shape"])
    count = int(np.prod(shape))
    scale = float(volume["microvolts_per_count"]) / 1e6
    components = {}
    if volume.get("storage") == "external_int16_le_split":
        if binary_path is not None:
            raise ValueError("binary_path is only valid for a legacy combined compact asset")
        if set(volume.get("assets", {})) != set(PUBLISHED_COMPONENTS):
            raise ValueError("compact dataset must contain exactly S and R assets")
        for key in PUBLISHED_COMPONENTS:
            asset = volume["assets"][key]
            path = Path(manifest_path).with_name(asset["asset"])
            if int(path.stat().st_size) != int(asset["asset_bytes"]):
                raise ValueError(f"compact {key} asset size does not match the manifest")
            if asset.get("asset_sha256") and _sha256(path) != asset["asset_sha256"]:
                raise ValueError(f"compact {key} asset SHA-256 does not match the manifest")
            raw = gzip.decompress(path.read_bytes())
            if len(raw) != int(asset["uncompressed_bytes"]):
                raise ValueError(f"compact {key} asset expands to an unexpected byte length")
            values = np.frombuffer(raw, dtype="<i2", count=count)
            components[key] = values.reshape(shape).astype(np.float32) * scale
    elif volume.get("storage") == "external_int16_le":
        if set(volume.get("component_offsets_bytes", {})) != set(PUBLISHED_COMPONENTS):
            raise ValueError("compact dataset must contain exactly S and R offsets")
        path = Path(binary_path or Path(manifest_path).with_name(volume["asset"]))
        if int(path.stat().st_size) != int(volume["asset_bytes"]):
            raise ValueError("compact asset size does not match the manifest")
        if volume.get("asset_sha256") and _sha256(path) != volume["asset_sha256"]:
            raise ValueError("compact asset SHA-256 does not match the manifest")
        raw = gzip.decompress(path.read_bytes()) if volume.get("compression") == "gzip" else path.read_bytes()
        if len(raw) != int(volume["uncompressed_bytes"]):
            raise ValueError("compact asset expands to an unexpected byte length")
        for key in PUBLISHED_COMPONENTS:
            offset = int(volume["component_offsets_bytes"][key])
            values = np.frombuffer(raw, dtype="<i2", count=count, offset=offset)
            components[key] = values.reshape(shape).astype(np.float32) * scale
    else:
        raise ValueError("unsupported compact dataset storage")
    return (
        components,
        np.asarray(payload["times_ms"], dtype=np.float32),
        np.asarray(payload["response_times_ms"], dtype=np.float32),
        list(payload["channels"]),
        payload["metadata"],
    )


def write_ride_viewer(
    output: Path,
    components: Dict[str, np.ndarray],
    times_ms: np.ndarray,
    response_times_ms: np.ndarray,
    channels: Sequence[str],
    metadata: dict,
    binary_output: Optional[Path] = None,
    binary_asset_url: Optional[str] = None,
    binary_outputs: Optional[Dict[str, Path]] = None,
    binary_asset_urls: Optional[Dict[str, str]] = None,
    manifest_output: Optional[Path] = None,
) -> None:
    expected_keys = set(PUBLISHED_COMPONENTS)
    if set(components) != expected_keys:
        raise ValueError("components must contain exactly S and R")
    shapes = {np.asarray(value).shape for value in components.values()}
    if len(shapes) != 1:
        raise ValueError("component shapes differ")
    n_trials, n_channels, n_times = next(iter(shapes))
    times_ms = _require_vector(times_ms, "times_ms", n_times).astype(np.float32)
    response_times_ms = _require_vector(
        response_times_ms, "response_times_ms", n_trials
    ).astype(np.float32)
    if len(channels) != n_channels:
        raise ValueError(f"channels has length {len(channels)}; expected {n_channels}")
    if np.any(response_times_ms < times_ms[0]) or np.any(response_times_ms > times_ms[-1]):
        raise ValueError("response_times_ms values fall outside times_ms")
    template_path = Path(__file__).with_name("ride_viewer_template.html")
    if (binary_output is None) != (binary_asset_url is None):
        raise ValueError("binary_output and binary_asset_url must be provided together")
    if (binary_outputs is None) != (binary_asset_urls is None):
        raise ValueError("binary_outputs and binary_asset_urls must be provided together")
    if binary_output is not None and binary_outputs is not None:
        raise ValueError("combined and split binary outputs are mutually exclusive")
    if binary_outputs is not None and binary_asset_urls is not None:
        encoded = encode_components_binary_split(
            components, binary_outputs, binary_asset_urls
        )
    elif binary_output is not None and binary_asset_url is not None:
        encoded = encode_components_binary(components, binary_output, binary_asset_url)
    else:
        encoded = encode_components(components)
    metadata.setdefault("amplitude", {})["display"] = {
        "initial_symmetric_limit_uv": encoded["default_limit_uv"],
        "maximum_adjustable_limit_uv": encoded["max_abs_uv"],
        "percentile": encoded["percentile"],
        "encoding": {
            "dtype": encoded["dtype"],
            "microvolts_per_count": encoded["microvolts_per_count"],
            "clipped": False,
        },
    }
    metadata.setdefault("bilateral_pairs", [list(pair) for pair in BILATERAL_PAIRS])
    payload = {
        "volume": encoded,
        "times_ms": [float(value) for value in times_ms],
        "response_times_ms": [float(value) for value in response_times_ms],
        "channels": list(channels),
        "metadata": metadata,
        "citations": [
            {
                "text": "Ouyang, G., Schacht, A., Zhou, C., & Sommer, W. (2013). Overcoming limitations of the ERP method with Residue Iteration Decomposition (RIDE): A demonstration in go/no-go experiments. Psychophysiology, 50(3), 253–265.",
                "doi": "https://doi.org/10.1111/psyp.12004",
            },
            {
                "text": "Syrov, N., Muhammad, D. G., Medvedeva, A., Yakovlev, L., Kaplan, A., & Lebedev, M. (2025). Revealing the different levels of action monitoring in visuomotor transformation task: Evidence from decomposition of cortical potentials. Psychophysiology, 62(1), e14708.",
                "doi": "https://doi.org/10.1111/psyp.14708",
            },
        ],
    }
    if manifest_output is not None:
        manifest_output.parent.mkdir(parents=True, exist_ok=True)
        manifest_output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    html = Template(template_path.read_text(encoding="utf-8")).safe_substitute(
        PAYLOAD=json.dumps(payload, separators=(",", ":"))
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    components, times, response_times, channels, metadata = load_ride_components(args.input)
    metadata["input"]["path"] = str(args.input)
    published = {key: components[key] for key in PUBLISHED_COMPONENTS}
    write_ride_viewer(args.output, published, times, response_times, channels, metadata)
    print(args.output)


if __name__ == "__main__":
    main()
