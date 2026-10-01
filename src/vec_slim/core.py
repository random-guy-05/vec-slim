from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np
from scipy import sparse


@dataclass(frozen=True)
class SlimPlan:
    task: str
    keep_spatial: bool
    expression_dtype: str = "float32"
    spatial_columns: int = 3


def plan_for_task(task: str) -> SlimPlan:
    task = task.upper()
    if task not in {"T1", "T2", "T3"}:
        raise ValueError("task must be T1, T2, or T3")
    return SlimPlan(task=task, keep_spatial=task in {"T2", "T3"})


def _update_matrix_hash(digest, matrix, chunk_rows: int = 512) -> None:
    n_rows = int(matrix.shape[0])
    for start in range(0, n_rows, chunk_rows):
        part = matrix[start : start + chunk_rows]
        if sparse.issparse(part):
            part = part.toarray()
        array = np.ascontiguousarray(np.asarray(part, dtype=np.float32))
        digest.update(array.tobytes())


def semantic_fingerprint(matrix, var_names, task: str, spatial=None) -> str:
    plan = plan_for_task(task)
    digest = hashlib.sha256()
    digest.update(plan.task.encode())
    digest.update(str(tuple(matrix.shape)).encode())

    for gene in var_names:
        digest.update(str(gene).encode("utf-8"))
        digest.update(b"\0")

    _update_matrix_hash(digest, matrix)

    if plan.keep_spatial:
        if spatial is None:
            raise ValueError("T2/T3 require spatial_3D")
        coordinates = np.asarray(spatial, dtype=np.float32)
        if (
            coordinates.ndim != 2
            or coordinates.shape[0] != matrix.shape[0]
            or coordinates.shape[1] < 3
        ):
            raise ValueError("spatial_3D must be cells x >=3")
        digest.update(
            np.ascontiguousarray(coordinates[:, :3]).tobytes()
        )

    return digest.hexdigest()
