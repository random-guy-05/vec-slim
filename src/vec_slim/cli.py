from __future__ import annotations

import argparse
from contextlib import suppress
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

from .core import plan_for_task, semantic_fingerprint


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scorer-aware VEC H5AD slimmer.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--task", required=True, choices=["T1", "T2", "T3"])
    args = parser.parse_args(argv)

    import anndata as ad

    source = ad.read_h5ad(args.input)
    plan = plan_for_task(args.task)
    spatial = (
        source.obsm["spatial_3D"]
        if plan.keep_spatial and "spatial_3D" in source.obsm
        else None
    )

    if plan.keep_spatial and spatial is None:
        print('ERROR: T2/T3 input is missing obsm["spatial_3D"]')
        return 2

    before_fingerprint = semantic_fingerprint(
        source.X,
        source.var_names,
        args.task,
        spatial,
    )

    expression = source.X.astype(np.float32)
    if sparse.issparse(expression):
        expression = expression.copy()

    output = ad.AnnData(
        X=expression,
        var=pd.DataFrame(index=source.var_names.astype(str)),
    )
    if plan.keep_spatial:
        output.obsm["spatial_3D"] = np.asarray(
            spatial,
            dtype=np.float32,
        )[:, :3]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.write_h5ad(args.output, compression="gzip")

    check = ad.read_h5ad(args.output, backed="r")
    try:
        after_spatial = (
            check.obsm["spatial_3D"] if plan.keep_spatial else None
        )
        after_fingerprint = semantic_fingerprint(
            check.X,
            check.var_names,
            args.task,
            after_spatial,
        )
    finally:
        with suppress(AttributeError, OSError, ValueError):
            check.file.close()

    if before_fingerprint != after_fingerprint:
        args.output.unlink(missing_ok=True)
        print("ERROR: scorer-semantic fingerprint changed; output removed")
        return 2

    before_bytes = args.input.stat().st_size
    after_bytes = args.output.stat().st_size
    reduction = (
        100.0 * (1 - after_bytes / before_bytes)
        if before_bytes
        else 0.0
    )
    print(f"PASS semantic fingerprint {after_fingerprint}")
    print(
        f"{before_bytes:,} -> {after_bytes:,} bytes "
        f"({reduction:.1f}% reduction)"
    )
    kept = "X, var_names"
    if plan.keep_spatial:
        kept += ", spatial_3D[:,:3]"
    print(f"Kept: {kept}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
