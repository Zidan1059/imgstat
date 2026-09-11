"""Unit tests for imgstat.core."""

import numpy as np
import pytest

from imgstat.core import ascii_histogram, compute_stats, load_image


def test_compute_stats_grayscale():
    arr = np.array([[0, 255], [0, 255]], dtype=np.uint8)
    stats = compute_stats(arr, mode="L")

    assert stats.width == 2
    assert stats.height == 2
    assert len(stats.channels) == 1

    ch = stats.channels[0]
    assert ch.name == "gray"
    assert ch.min == 0.0
    assert ch.max == 255.0
    assert ch.mean == pytest.approx(127.5)


def test_compute_stats_rgb_channel_names():
    arr = np.zeros((3, 4, 3), dtype=np.uint8)
    stats = compute_stats(arr, mode="RGB")

    assert [c.name for c in stats.channels] == ["red", "green", "blue"]
    assert all(c.mean == 0.0 for c in stats.channels)


def test_to_dict_is_serializable():
    import json

    arr = np.zeros((2, 2, 3), dtype=np.uint8)
    stats = compute_stats(arr, mode="RGB", path="x.png")
    # Should not raise.
    json.dumps(stats.to_dict())


def test_ascii_histogram_row_count():
    values = np.arange(100)
    out = ascii_histogram(values, bins=10, width=20)
    assert len(out.splitlines()) == 10


def test_load_image_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_image(tmp_path / "does_not_exist.png")
