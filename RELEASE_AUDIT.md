# Release audit

Release: **v1.0.0**  
Audit date: **2026-09-30**

- Local unit tests: **5/5 passing**
- `python -m compileall -q src tests`: **passing**
- CLI `--help`: **passing**
- Required release files (README, licence, contribution text, changelog, CI, source snapshot): **present**
- Uses only synthetic/unit-test inputs in the repository. No Challenge data is bundled.

## Scope of local verification

The execution environment used for this release has NumPy/SciPy/pytest/psutil but does not have `anndata` or `veckit`, and outbound package installation is unavailable. Code that depends on those packages imports them lazily; its pure logic and adapters are unit-tested here, and GitHub Actions is configured to install declared dependencies in a normal public CI environment. Dependency-free CLIs were additionally exercised end-to-end.

This limitation is recorded rather than hidden: the repository is release-ready, but a publisher should still let the included CI matrix run after putting it on GitHub.
