from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SlimPlan:
    task: str
    keep_spatial: bool
    expression_dtype: str = 'float32'
    spatial_columns: int = 3


def plan_for_task(task: str) -> SlimPlan:
    task = task.upper()
    if task not in {'T1', 'T2', 'T3'}:
        raise ValueError('task must be T1, T2, or T3')
    return SlimPlan(task=task, keep_spatial=task in {'T2', 'T3'})


def _update_matrix_hash(h, x, chunk_rows: int = 512) -> None:
    try:
        from scipy import sparse
    except Exception:
        sparse = None
    n = int(x.shape[0])
    for start in range(0, n, chunk_rows):
        part = x[start:start + chunk_rows]
        if sparse is not None and sparse.issparse(part):
            part = part.toarray()
        arr = np.ascontiguousarray(np.asarray(part, dtype=np.float32))
        h.update(arr.tobytes())


def semantic_fingerprint(x, var_names, task: str, spatial=None) -> str:
    plan = plan_for_task(task)
    h = hashlib.sha256()
    h.update(plan.task.encode())
    h.update(str(tuple(x.shape)).encode())
    for gene in var_names:
        h.update(str(gene).encode('utf-8'))
        h.update(b'\0')
    _update_matrix_hash(h, x)
    if plan.keep_spatial:
        if spatial is None:
            raise ValueError('T2/T3 require spatial_3D')
        c = np.asarray(spatial, dtype=np.float32)
        if c.ndim != 2 or c.shape[0] != x.shape[0] or c.shape[1] < 3:
            raise ValueError('spatial_3D must be cells x >=3')
        h.update(np.ascontiguousarray(c[:, :3]).tobytes())
    return h.hexdigest()
