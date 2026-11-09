#!/usr/bin/env python3
# SPDX-License-Identifier: CC0-1.0
"""Open an ASCII PLY point cloud and print a summary.

Viewing, segmentation, and ICP come later.
This script only reads the file and describes the points.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def default_cloud() -> Path:
    return (
        Path(__file__).resolve().parent.parent
        / "data"
        / "bunny"
        / "bun_zipper_res2.ply"
    )


def _read_header(handle):
    first = handle.readline()
    if first.strip() != "ply":
        raise ValueError("this file is not a PLY")

    ply_format = None
    elements = []
    current = None

    while True:
        line = handle.readline()
        if not line:
            raise ValueError("incomplete PLY header")
        parts = line.split()
        if not parts or parts[0] in {"comment", "obj_info"}:
            continue
        if parts[0] == "format":
            ply_format = parts[1]
            continue
        if parts[0] == "element":
            current = {
                "name": parts[1],
                "count": int(parts[2]),
                "properties": [],
            }
            elements.append(current)
            continue
        if parts[0] == "property":
            if current is None:
                raise ValueError("PLY property outside an element")
            current["properties"].append(parts[1:])
            continue
        if parts[0] == "end_header":
            break
        raise ValueError(f"unexpected header line: {line.rstrip()}")

    if ply_format != "ascii":
        raise ValueError(
            f"unsupported PLY format: {ply_format} (only ASCII PLY is read)"
        )
    return elements


def read_ascii_ply(path: Path) -> dict:
    with path.open("r", encoding="ascii") as handle:
        elements = _read_header(handle)
        points = None
        names = None

        for element in elements:
            if element["name"] != "vertex":
                for _ in range(element["count"]):
                    if not handle.readline():
                        raise ValueError(
                            f"truncated file in element {element['name']}"
                        )
                continue

            names = []
            for prop in element["properties"]:
                if prop[0] == "list":
                    raise ValueError("list property on a vertex is not supported")
                names.append(prop[-1])
            if not {"x", "y", "z"} <= set(names):
                raise ValueError("vertices have no x y z coordinates")

            points = []
            for _ in range(element["count"]):
                values = handle.readline().split()
                if len(values) < len(names):
                    raise ValueError("incomplete vertex line")
                points.append(
                    {name: float(raw) for name, raw in zip(names, values)}
                )

        if points is None:
            raise ValueError("this PLY has no vertices")

    return {"elements": elements, "names": names, "points": points}


def show(path: Path, cloud: dict) -> None:
    points = cloud["points"]
    count = len(points)
    print(f"file       : {path}")
    print("format     : PLY ascii")
    print(f"points     : {count}")
    print(f"properties : {', '.join(cloud['names'])}")

    for element in cloud["elements"]:
        if element["name"] != "vertex":
            print(f"{element['name']:<11}: {element['count']}")

    for axis in ("x", "y", "z"):
        values = [point[axis] for point in points]
        print(
            f"{axis}          : "
            f"min {min(values): .6f}   "
            f"max {max(values): .6f}   "
            f"mean {sum(values) / count: .6f}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Open an ASCII PLY point cloud and print a summary."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=default_cloud(),
        help="PLY file (default: data/bunny/bun_zipper_res2.ply)",
    )
    args = parser.parse_args(argv)
    path = args.path
    if not path.is_file():
        print(f"file not found: {path}", file=sys.stderr)
        return 1
    try:
        cloud = read_ascii_ply(path)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"cannot read file: {error}", file=sys.stderr)
        return 1
    show(path, cloud)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
