#!/usr/bin/env python3
"""Generate the public S/R RIDE trial-volume viewer."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ride_volume import (  # noqa: E402
    load_compact_ride_dataset,
    load_ride_collection,
    write_ride_viewer,
)


def main() -> None:
    sources = [
        ROOT / "data" / name
        for name in (
            "S02_far_RIDE_result.mat",
            "S04_far_RIDE_result.mat",
            "S07_far_RIDE_result.mat",
        )
    ]
    binary_outputs = {
        key: ROOT / "docs" / f"ride-volume-{key}.i16.gz" for key in ("S", "R")
    }
    manifest_output = ROOT / "docs" / "ride-volume.json"
    if all(path.is_file() and path.stat().st_size > 1_000_000 for path in sources):
        components, times, response_times, channels, metadata = load_ride_collection(
            sources, l_freq=0.5, h_freq=20.0, iir_order=4
        )
    elif manifest_output.is_file() and all(path.is_file() for path in binary_outputs.values()):
        components, times, response_times, channels, metadata = load_compact_ride_dataset(
            manifest_output
        )
    else:
        raise SystemExit(
            "Neither the three source RIDE MAT files nor the compact RIDE "
            "dataset (docs/ride-volume.json + docs/ride-volume-{S,R}.i16.gz) is available"
        )
    components = {key: components[key] for key in ("S", "R")}
    metadata["component_fields"] = {
        key: metadata["component_fields"][key] for key in components
    }
    metadata["component_titles"] = {
        key: metadata["component_titles"][key] for key in components
    }
    metadata["amplitude"]["component_extrema_uv"] = {
        key: metadata["amplitude"]["component_extrema_uv"][key] for key in components
    }
    output = ROOT / "docs" / "ride.html"
    write_ride_viewer(
        output,
        components,
        times,
        response_times,
        channels,
        metadata,
        binary_outputs=binary_outputs,
        binary_asset_urls={key: path.name for key, path in binary_outputs.items()},
        manifest_output=manifest_output,
    )
    print(output)
    for path in binary_outputs.values():
        print(path)
    print(manifest_output)


if __name__ == "__main__":
    main()
