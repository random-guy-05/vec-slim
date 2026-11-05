import os
from pathlib import Path

import anndata as ad
import numpy as np
import pytest

from vec_slim import cli


@pytest.fixture
def source_path(tmp_path):
    path = tmp_path / "source.h5ad"
    source = ad.AnnData(X=np.arange(12, dtype=np.float64).reshape(3, 4))
    source.layers["raw_counts"] = source.X.copy()
    source.uns["notes"] = "Preserve source metadata"
    source.write_h5ad(path)
    return path


@pytest.mark.parametrize("alias_kind", ["hardlink", "symlink"])
def test_cli_rejects_source_alias_without_changing_source(source_path, alias_kind):
    output_path = source_path.with_name("alias.h5ad")
    if alias_kind == "hardlink":
        os.link(source_path, output_path)
    else:
        output_path.symlink_to(source_path)
    before = source_path.read_bytes()

    assert cli.main([str(source_path), str(output_path), "--task", "T1"]) == 2
    assert source_path.read_bytes() == before
    assert output_path.samefile(source_path)


@pytest.mark.parametrize("existing_output", [False, True])
def test_fingerprint_failure_preserves_destination(
    source_path, monkeypatch, existing_output
):
    output_path = source_path.with_name("output.h5ad")
    original_output = b"existing destination content"
    if existing_output:
        output_path.write_bytes(original_output)
    original_source = source_path.read_bytes()
    fingerprints = iter(["before", "changed"])
    monkeypatch.setattr(cli, "semantic_fingerprint", lambda *args: next(fingerprints))

    assert cli.main([str(source_path), str(output_path), "--task", "T1"]) == 2
    assert source_path.read_bytes() == original_source
    if existing_output:
        assert output_path.read_bytes() == original_output
    else:
        assert not output_path.exists()
    assert sorted(p.name for p in source_path.parent.iterdir()) == (
        ["output.h5ad", "source.h5ad"] if existing_output else ["source.h5ad"]
    )


@pytest.mark.parametrize("failure_stage", ["write", "read", "replace"])
def test_io_failure_preserves_files_and_cleans_candidate(
    source_path, monkeypatch, failure_stage
):
    output_path = source_path.with_name("output.h5ad")
    original_output = b"existing destination content"
    output_path.write_bytes(original_output)
    original_source = source_path.read_bytes()

    if failure_stage == "write":
        def fail_write(self, filename, **kwargs):
            Path(filename).write_bytes(b"partial candidate")
            raise OSError("injected write failure")

        monkeypatch.setattr(ad.AnnData, "write_h5ad", fail_write)
    elif failure_stage == "read":
        read_h5ad = ad.read_h5ad

        def fail_read(filename, *args, **kwargs):
            if kwargs.get("backed") == "r":
                raise OSError("injected read failure")
            return read_h5ad(filename, *args, **kwargs)

        monkeypatch.setattr(ad, "read_h5ad", fail_read)
    else:
        def fail_replace(*args):
            raise OSError("injected replace failure")

        monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(OSError, match=f"injected {failure_stage} failure"):
        cli.main([str(source_path), str(output_path), "--task", "T1"])

    assert source_path.read_bytes() == original_source
    assert output_path.read_bytes() == original_output
    assert sorted(p.name for p in source_path.parent.iterdir()) == [
        "output.h5ad", "source.h5ad"
    ]


def test_verified_candidate_replaces_existing_destination(source_path, monkeypatch):
    output_path = source_path.with_name("output.h5ad")
    original_output = b"existing destination content"
    output_path.write_bytes(original_output)
    original_source = source_path.read_bytes()
    replace = os.replace
    replaced = []

    def verify_then_replace(candidate, destination):
        candidate = Path(candidate)
        assert candidate.parent == output_path.parent
        assert candidate != output_path
        assert output_path.read_bytes() == original_output
        check = ad.read_h5ad(candidate, backed="r")
        try:
            assert check.X.dtype == np.float32
            assert cli.semantic_fingerprint(check.X, check.var_names, "T1") == (
                cli.semantic_fingerprint(
                    np.arange(12, dtype=np.float64).reshape(3, 4),
                    ["0", "1", "2", "3"],
                    "T1",
                )
            )
        finally:
            check.file.close()
        replaced.append(candidate)
        replace(candidate, destination)

    monkeypatch.setattr(os, "replace", verify_then_replace)

    assert cli.main([str(source_path), str(output_path), "--task", "T1"]) == 0
    assert len(replaced) == 1
    assert not replaced[0].exists()
    assert source_path.read_bytes() == original_source
    slim = ad.read_h5ad(output_path)
    np.testing.assert_array_equal(slim.X, np.arange(12).reshape(3, 4))
    assert slim.X.dtype == np.float32
    assert "raw_counts" not in slim.layers
    assert len(slim.uns) == 0
    assert sorted(p.name for p in source_path.parent.iterdir()) == [
        "output.h5ad", "source.h5ad"
    ]
