# Community Contribution submission text

## Title
VEC Slim — safely strip non-scoring AnnData baggage from submissions

## Description
VEC Slim rewrites a prediction H5AD to contain only content the current VEC scorer reads: `.X`, ordered `var_names`, and for T2/T3 the first three `spatial_3D` columns. It casts expression/coordinates to float32 to match scorer semantics, removes unused layers/embeddings/metadata, compresses the result, and verifies a scorer-semantic fingerprint before and after writing. It reports the byte reduction and fails if scorer-relevant content changed. This reduces upload/storage friction and helps entrants stay below the 1200 MB submission limit without guessing which AnnData fields are safe to remove.
