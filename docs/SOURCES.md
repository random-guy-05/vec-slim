# VEC source snapshot

Verified **2026-10-01**. The official Challenge website is authoritative and may change.

- Data and board contracts: https://virtualembryo.ai/challenge/data
- Submission contract and metrics: https://virtualembryo.ai/challenge/evaluation
- Rules and submission limits: https://virtualembryo.ai/challenge/rules
- Reference baselines: https://virtualembryo.ai/challenge/baselines
- Community Contribution Award: https://virtualembryo.ai/challenge/community
- Official local scorer: https://github.com/aristoteleo/veckit

Current validation-board contracts:

| Board | genes | cells | spatial |
|---|---:|---:|---|
| `T1:val` | 32,285 | 1,000-5,118 | no |
| `T2:embryo:val_interp` | 498 | 583-5,000 | yes |
| `T2:heart:val_extrap` | 500 | 1,000-25,179 | yes |
| `T2:heart:val_interp` | 500 | 1,000-17,616 | yes |
| `T3:gata4` | 500 | 1,000-7,449 | yes |

Important public facts used by these tools:

- `.X` must be finite, non-negative, and already log-normalised; raw counts can pass structural validation and still be scored incorrectly.
- T2/T3 require `obsm["spatial_3D"]`; only the first three columns are read.
- Cell count is a sample size, not itself scored. The heaviest metrics subsample at roughly 1,500-2,000 cells.
- P3 permits two official submissions per board for the whole phase.
- One prediction file may not exceed 1200 MB.
