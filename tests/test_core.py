import numpy as np
import pytest

from vec_slim.core import plan_for_task, semantic_fingerprint


def test_task_plan():
    assert plan_for_task("T1").keep_spatial is False
    assert plan_for_task("T2").keep_spatial is True
    assert plan_for_task("t3").keep_spatial is True
    with pytest.raises(ValueError):
        plan_for_task("T4")


def test_float64_and_float32_share_scorer_fingerprint():
    matrix = np.array([[1.1, 2.2], [3.3, 4.4]], dtype=np.float64)
    assert semantic_fingerprint(matrix, ["a", "b"], "T1") == semantic_fingerprint(
        matrix.astype(np.float32),
        ["a", "b"],
        "T1",
    )


def test_spatial_extra_columns_are_ignored():
    matrix = np.ones((2, 2))
    coords = np.array([[1, 2, 3, 9], [4, 5, 6, 88]], dtype=float)
    changed = coords.copy()
    changed[:, 3] += 1000
    assert semantic_fingerprint(matrix, ["a", "b"], "T2", coords) == semantic_fingerprint(
        matrix,
        ["a", "b"],
        "T2",
        changed,
    )


def test_spatial_change_is_detected():
    matrix = np.ones((2, 2))
    coords = np.zeros((2, 3))
    changed = coords.copy()
    changed[0, 0] = 1
    assert semantic_fingerprint(matrix, ["a", "b"], "T2", coords) != semantic_fingerprint(
        matrix,
        ["a", "b"],
        "T2",
        changed,
    )
