# VEC Slim

`vec-slim` rewrites a VEC prediction into a **compact conservative AnnData representation that preserves what the current scorer reads**.

The official contract says the scorer uses `.X`, `var_names`, and for T2/T3 the first three columns of `obsm["spatial_3D"]`. Submitted cell-type labels are ignored. Experiment files often carry PCA/UMAP embeddings, layers, raw counts, large `uns`, extra `obs` metadata, and float64 arrays that add upload/storage cost without changing the score.

## Quick start

```bash
pip install -e .
vec-slim prediction.h5ad submission.h5ad --task T2
```

The tool:

- casts scorer-read expression to float32, matching scorer behavior;
- keeps the exact gene names/order;
- keeps only the first 3 spatial columns for T2/T3;
- drops layers, `raw`, extra `obsm`, `uns`, and ignored `obs` columns;
- writes gzip-compressed H5AD;
- computes scorer-semantic fingerprints before and after rewriting and refuses success if they differ;
- prints before/after bytes and reduction percentage.

This is not a validator. Run the official/local format checker after slimming too.

## Why useful

The Challenge caps a prediction file at 1200 MB, and Task 1 can be especially large. Slimming also makes final-artifact hashing, uploads, backups and reproducibility bundles cheaper.


## Safety notes

- Input and output must be different files; the CLI refuses to overwrite the source in place.
- The semantic fingerprint checks scorer-visible expression, ordered gene names, and the first three spatial columns for T2/T3 after float32 casting.
- Slimming does not prove that a prediction is valid for a particular board. Run the normal VEC validator afterward.
