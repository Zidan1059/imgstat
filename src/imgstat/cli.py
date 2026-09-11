"""Command-line interface for imgstat."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

import numpy as np

from . import __version__
from .core import ascii_histogram, compute_stats, load_image


def _format_human(stats, hist: str | None) -> str:
    """Build the human-readable report for a single image."""
    lines = [
        f"{stats.path}",
        f"  size    : {stats.width} x {stats.height} px",
        f"  mode    : {stats.mode}",
        f"  channels: {len(stats.channels)}",
        "",
        f"  {'channel':<8} {'min':>8} {'max':>8} {'mean':>9} {'std':>9}",
        f"  {'-' * 8} {'-' * 8:>8} {'-' * 8:>8} {'-' * 9:>9} {'-' * 9:>9}",
    ]
    for c in stats.channels:
        lines.append(
            f"  {c.name:<8} {c.min:>8.1f} {c.max:>8.1f} {c.mean:>9.2f} {c.std:>9.2f}"
        )
    if hist is not None:
        lines += ["", "  intensity histogram:", ""]
        lines += ["  " + row for row in hist.splitlines()]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser."""
    parser = argparse.ArgumentParser(
        prog="imgstat",
        description="Report statistics and an ASCII intensity histogram for images.",
    )
    parser.add_argument("images", nargs="+", help="one or more image files")
    parser.add_argument(
        "--json", action="store_true", help="emit machine-readable JSON instead of text"
    )
    parser.add_argument(
        "--bins", type=int, default=32, help="histogram bucket count (default: 32)"
    )
    parser.add_argument(
        "--no-hist", action="store_true", help="skip the histogram in text output"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Program entry point. Returns a process exit code."""
    args = build_parser().parse_args(argv)

    results = []
    exit_code = 0
    for path in args.images:
        try:
            arr, mode = load_image(path)
        except (FileNotFoundError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        stats = compute_stats(arr, mode, path=path)

        if args.json:
            results.append(stats.to_dict())
        else:
            hist = None if args.no_hist else ascii_histogram(arr, bins=args.bins)
            print(_format_human(stats, hist))
            print()

    if args.json:
        print(json.dumps(results, indent=2))

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
