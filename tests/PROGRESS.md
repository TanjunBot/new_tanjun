# Test Expansion Progress

| Batch | Status | Tests | Coverage (split run) | Notes |
|-------|--------|------:|------------------------|-------|
| 0 Infra | done | — | — | helpers, per-file gate script, CI jobs |
| 1 Unit core | done | ~900 | — | services, repos, models, utils, health |
| 2 Games/minigames | done | ~200 | — | hypothesis + pure logic |
| 3 api.py | done | ~570 | api ~91% | mocked + integration |
| 4 admin+level cmds | done | ~500 | partial | integration/commands |
| 5 giveaway+utility | done | ~350 | partial | brawlstars, schedule, etc. |
| 6 games+logs+mini | done | ~200 | partial | |
| 7 remaining cmds | in progress | ~150 | partial | math, image, channel, ai, fun |
| 8 extensions | done | ~800 | admin/logs 90%+ | comprehensive suites |
| 9 E2E mock | done | 176 | — | tests/e2e/ |
| 10 Live e2e | done | 2+ | — | tests/e2e_live/, skips without token |
| 11 Gap fill | in progress | +400 | **76% total**, ~100 files &lt;85% | continue gap-fill |
| 12 PR | in progress | — | — | branch `test/comprehensive-testing-expansion` |

**Collected tests:** ~3360 (local)

**Resume coverage measurement:**
```bash
rm -f .coverage coverage.json
pytest tests/unit -q --cov=. --cov-report= --cov-fail-under=0
pytest tests/integration/commands tests/integration/api -q --cov=. --cov-append --cov-report= --cov-fail-under=0
pytest tests/integration/extensions -q --cov=. --cov-append --cov-report= --cov-fail-under=0
pytest tests/e2e tests/e2e_live -q --cov=. --cov-append --cov-report= --cov-fail-under=0
coverage json -o coverage.json
coverage report --fail-under=85
python scripts/check_coverage_per_file.py --min 85
```

Last updated: gap-fill in progress (76% total, ~100 files below 85%)
