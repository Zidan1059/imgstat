"""Core image statistics computation.

This module is deliberately free of any CLI concerns so it can be reused
as a library. Everything here operates on NumPy arrays.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

__all__ = ["ChannelStats", "ImageStats", "load_image", "compute_stats", "ascii_histogram"]


@dataclass(frozen=True)
class ChannelStats:
    """Summary statistics for a single image channel."""

    name: str
    min: float
    max: float
    mean: float
    std: float


@dataclass(frozen=True)
class ImageStats:
    """Full statistical summary of an image."""

    path: str
    width: int
    height: int
    mode: str
    channels: tuple[ChannelStats, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        data = asdict(self)
        data["channels"] = [asdict(c) for c in self.channels]
        return data


def load_image(path: str | Path) -> tuple[np.ndarray, str]:
    """Load an image from disk into a NumPy array.

    Args:
        path: Path to an image file readable by Pillow.

    Returns:
        A ``(array, mode)`` pair. The array has shape ``(H, W)`` for
        grayscale or ``(H, W, C)`` for multi-channel images, with dtype
        preserved from the source. ``mode`` is the Pillow mode string.

    Raises:
        FileNotFoundError: If the path does not exist.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"No such image file: {p}")
    with Image.open(p) as img:
        return np.asarray(img), img.mode


def _channel_names(mode: str, count: int) -> tuple[str, ...]:
    """Best-effort channel labels for a given Pillow mode."""
    known = {
        "L": ("gray",),
        "LA": ("gray", "alpha"),
        "RGB": ("red", "green", "blue"),
        "RGBA": ("red", "green", "blue", "alpha"),
        "CMYK": ("cyan", "magenta", "yellow", "black"),
    }
    if mode in known and len(known[mode]) == count:
        return known[mode]
    return tuple(f"ch{i}" for i in range(count))


def compute_stats(arr: np.ndarray, mode: str, path: str = "<array>") -> ImageStats:
    """Compute per-channel statistics for an image array.

    Args:
        arr: Image data of shape ``(H, W)`` or ``(H, W, C)``.
        mode: Pillow mode string (e.g. ``"RGB"``), used for channel labels.
        path: Optional source path, recorded on the result.

    Returns:
        An :class:`ImageStats` describing the image.
    """
    if arr.ndim == 2:
        arr = arr[:, :, np.newaxis]
    height, width, count = arr.shape
    names = _channel_names(mode, count)

    channels = tuple(
        ChannelStats(
            name=names[i],
            min=float(arr[:, :, i].min()),
            max=float(arr[:, :, i].max()),
            mean=float(arr[:, :, i].mean()),
            std=float(arr[:, :, i].std()),
        )
        for i in range(count)
    )
    return ImageStats(path=path, width=width, height=height, mode=mode, channels=channels)


def ascii_histogram(values: np.ndarray, bins: int = 32, width: int = 40) -> str:
    """Render a horizontal ASCII histogram of pixel intensities.

    Args:
        values: Flat or nested array of numeric intensities.
        bins: Number of histogram buckets.
        width: Maximum bar width in characters.

    Returns:
        A multi-line string, one row per bucket.
    """
    flat = np.asarray(values).ravel()
    counts, edges = np.histogram(flat, bins=bins)
    peak = counts.max() if counts.size and counts.max() > 0 else 1

    rows = []
    for count, lo in zip(counts, edges[:-1]):
        bar = "\u2588" * int(round(count / peak * width))
        rows.append(f"{lo:7.1f} | {bar}")
    return "\n".join(rows)
