import subprocess
import sys

import anndata as ad
import numpy as np
import pandas as pd


def test_t2_cli_strips_baggage_and_preserves_scorer_content(tmp_path):
    rng = np.random.default_rng(9)
    source_path = tmp_path / "source.h5ad"
    output_path = tmp_path / "slim.h5ad"

    source = ad.AnnData(
        X=rng.normal(size=(80, 20)).astype(np.float64),
        obs=pd.DataFrame({"celltype": ["x"] * 80}),
        var=pd.DataFrame(index=[f"g{i}" for i in range(20)]),
    )
    source.layers["rawish"] = np.abs(
        rng.normal(size=(80, 20)).astype(np.float64)
    )
    source.obsm["spatial_3D"] = rng.normal(size=(80, 5)).astype(np.float64)
    source.obsm["X_umap"] = rng.normal(size=(80, 2))
    source.uns["large_metadata"] = {"notes": "x" * 5000}
    source.write_h5ad(source_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_slim.cli",
            str(source_path),
            str(output_path),
            "--task",
            "T2",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS semantic fingerprint" in result.stdout

    slim = ad.read_h5ad(output_path)
    assert slim.X.dtype == np.float32
    assert list(slim.var_names) == [f"g{i}" for i in range(20)]
    assert slim.obsm["spatial_3D"].shape == (80, 3)
    assert "X_umap" not in slim.obsm
    assert "rawish" not in slim.layers
    assert len(slim.uns) == 0
    assert "celltype" not in slim.obs.columns


def test_t2_missing_spatial_fails(tmp_path):
    source_path = tmp_path / "source.h5ad"
    output_path = tmp_path / "slim.h5ad"
    ad.AnnData(X=np.ones((10, 4), dtype=np.float32)).write_h5ad(source_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_slim.cli",
            str(source_path),
            str(output_path),
            "--task",
            "T2",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "missing" in (result.stdout + result.stderr).lower()



def test_t1_sparse_input_stays_sparse_and_drops_spatial_baggage(tmp_path):
    from scipy import sparse

    source_path = tmp_path / "source_t1.h5ad"
    output_path = tmp_path / "slim_t1.h5ad"
    rng = np.random.default_rng(10)
    matrix = sparse.csr_matrix(rng.poisson(1, size=(50, 30)).astype(np.float32))
    source = ad.AnnData(
        X=matrix,
        var=pd.DataFrame(index=[f"g{i}" for i in range(30)]),
    )
    source.obsm["X_umap"] = rng.normal(size=(50, 2))
    source.write_h5ad(source_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_slim.cli",
            str(source_path),
            str(output_path),
            "--task",
            "T1",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    slim = ad.read_h5ad(output_path)
    assert sparse.issparse(slim.X)
    assert slim.X.dtype == np.float32
    assert len(slim.obsm) == 0


def test_cli_refuses_in_place_overwrite(tmp_path):
    source_path = tmp_path / "source.h5ad"
    ad.AnnData(X=np.ones((10, 4), dtype=np.float32)).write_h5ad(source_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_slim.cli",
            str(source_path),
            str(source_path),
            "--task",
            "T1",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "different files" in result.stdout
