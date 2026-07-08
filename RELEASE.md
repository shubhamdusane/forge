# Release Checklist — forge

## 1. Prep

```bash
cd D:/dream-project/forge
pip install -e .[dev]
pytest -q
ruff check .
forge demo  # smoke test without API key
```

## 2. Bump version

- `pyproject.toml` → `version = "X.Y.Z"`
- `forge/__init__.py` → `__version__ = "X.Y.Z"`

## 3. Build

```bash
rm -rf dist build *.egg-info
python -m build
twine check dist/*
```

## 4. Tag & push

```bash
git add -A
git commit -m "release: forge-rwa vX.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

## 5. Publish PyPI

```bash
twine upload dist/*
```

Verify: <https://pypi.org/project/forge-rwa/X.Y.Z/>

## 6. GitHub Release

```bash
gh release create vX.Y.Z --generate-notes dist/*
```

## 7. Announce

- LinkedIn Day 6 launch post (`content/linkedin-7day.md`)
- Update `D:/Shubham/KANBAN.md` + `KNOWLEDGE_GRAPH.md`
- Cross-post to r/ethereum, r/defi

## Post-release

- 48h PyPI / GitHub star monitoring
- Triage issues within 24h
- Update compliance matrix if new jurisdiction requested

## Safety gate (mainnet-facing)

Before scaffold output is deployed to **mainnet**, confirm:

- [ ] Independent securities-law opinion letter obtained
- [ ] Smart-contract audit completed (firm + report hash in RELEASE.md of child project)
- [ ] Multisig ownership configured
- [ ] Pause mechanism tested
- [ ] Incident-response runbook published
