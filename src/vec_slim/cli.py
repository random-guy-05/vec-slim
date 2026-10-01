from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from .core import plan_for_task, semantic_fingerprint


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='Scorer-aware VEC H5AD slimmer.')
    p.add_argument('input', type=Path)
    p.add_argument('output', type=Path)
    p.add_argument('--task', required=True, choices=['T1', 'T2', 'T3'])
    args = p.parse_args(argv)
    import anndata as ad
    from scipy import sparse

    src = ad.read_h5ad(args.input)
    plan = plan_for_task(args.task)
    spatial = src.obsm['spatial_3D'] if plan.keep_spatial and 'spatial_3D' in src.obsm else None
    before_fp = semantic_fingerprint(src.X, src.var_names, args.task, spatial)
    x = src.X.astype(np.float32)
    if sparse.issparse(x):
        x = x.copy()
    out = ad.AnnData(X=x, var=pd.DataFrame(index=src.var_names.astype(str)))
    if plan.keep_spatial:
        if spatial is None:
            raise SystemExit('ERROR: T2/T3 input is missing obsm["spatial_3D"]')
        out.obsm['spatial_3D'] = np.asarray(spatial, dtype=np.float32)[:, :3]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.write_h5ad(args.output, compression='gzip')
    check = ad.read_h5ad(args.output, backed='r')
    after_spatial = check.obsm['spatial_3D'] if plan.keep_spatial else None
    after_fp = semantic_fingerprint(check.X, check.var_names, args.task, after_spatial)
    try:
        check.file.close()
    except Exception:
        pass
    if before_fp != after_fp:
        args.output.unlink(missing_ok=True)
        print('ERROR: scorer-semantic fingerprint changed; output removed')
        return 2
    before = args.input.stat().st_size
    after = args.output.stat().st_size
    reduction = 100.0 * (1 - after / before) if before else 0.0
    print(f'PASS semantic fingerprint {after_fp}')
    print(f'{before:,} -> {after:,} bytes ({reduction:.1f}% reduction)')
    print('Kept: X, var_names' + (', spatial_3D[:,:3]' if plan.keep_spatial else ''))
    return 0
