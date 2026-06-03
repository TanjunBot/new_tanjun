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
| 11 Gap fill | done | +1450 | **~93% total**, **0 files** &lt;85% | batch 19: giveaway gaps, calculator, plot_function, listscheduled |
| 12 PR | in progress | — | — | branch `test/comprehensive-testing-expansion` |
| 20 UI/command depth | done | +~90 | logs wizard | view_state helpers, setup/logs UI deep, domain *_ui_deep.py |

**Collected tests:** run `pytest --collect-only -q` after batch 20

**Batch 20 conventions (first-page / pagination):**
1. Assert initial `reply` / `edit_message` embed content (not only `view is not None`).
2. Assert page index 0 markers (`Page 1/N`, `➤`, or field list).
3. Exercise prev/next at boundaries and API call args for the active page.
4. Helpers: `tests/helpers/view_state.py`, `tests/helpers/wizard_flow.py`.

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

Last updated: batch 20 — UI regression suite for logs setup wizard, configure_logs, blacklist lists, wizards, paginated commands
