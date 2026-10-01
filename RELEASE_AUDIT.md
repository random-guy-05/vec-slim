# Release audit

Release: **v1.0.0**  
Audit date: **2026-10-01**

## Release gate

The public GitHub Actions workflow runs on Python **3.10, 3.11, and 3.12** and requires all of the following:

- package installation from the repository metadata;
- the complete pytest suite;
- Ruff static/lint checks;
- bytecode compilation of `src` and `tests`.

## Integration coverage

Synthetic AnnData CLI integration verifies T2 slimming, metadata removal, float32 casting, spatial-column trimming, and semantic fingerprint preservation.

All repository fixtures are synthetic or generated during tests. No restricted or withheld Virtual Embryo Challenge data is bundled.

## Source contract

Challenge-specific statements are tied to `docs/SOURCES.md`. The official Virtual Embryo Challenge website and public scorer remain authoritative if the competition changes after the snapshot date.

## Release standard

A release is considered green only when the complete GitHub Actions matrix succeeds. README examples, package entry points, tests, license, contribution text, and source snapshot are included in the repository.
