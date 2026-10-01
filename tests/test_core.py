import numpy as np
import pytest
from vec_slim.core import plan_for_task, semantic_fingerprint


def test_task_plan():
    assert not plan_for_task('T1').keep_spatial
    assert plan_for_task('T2').keep_spatial
    assert plan_for_task('T3').keep_spatial


def test_float64_and_float32_have_same_scorer_fingerprint():
    x = np.array([[1.1, 2.2], [3.3, 4.4]], dtype=np.float64)
    assert semantic_fingerprint(x, ['a', 'b'], 'T1') == semantic_fingerprint(x.astype('float32'), ['a', 'b'], 'T1')


def test_spatial_extra_columns_ignored():
    x = np.ones((2, 2))
    c = np.array([[1,2,3,99],[4,5,6,88]], dtype=float)
    c2 = c.copy(); c2[:, 3] += 1000
    assert semantic_fingerprint(x, ['a','b'], 'T2', c) == semantic_fingerprint(x, ['a','b'], 'T2', c2)


def test_spatial_change_detected():
    x = np.ones((2, 2))
    c = np.zeros((2, 3)); c2 = c.copy(); c2[0,0] = 1
    assert semantic_fingerprint(x, ['a','b'], 'T2', c) != semantic_fingerprint(x, ['a','b'], 'T2', c2)


def test_missing_spatial_rejected():
    with pytest.raises(ValueError):
        semantic_fingerprint(np.ones((2,2)), ['a','b'], 'T2')
