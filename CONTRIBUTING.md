# Contributing

Bug reports and focused pull requests are welcome. Use synthetic or otherwise shareable data in tests; never commit restricted Challenge data.

Before opening a PR:

```bash
PYTHONPATH=src pytest -q
python -m compileall -q src tests
```

Official Challenge documentation remains authoritative if a rule changes after the source snapshot in `docs/SOURCES.md`.
