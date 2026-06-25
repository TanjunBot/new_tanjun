# Command test coverage matrix

Tracks how thoroughly slash commands are tested across layers and dimensions (permissions, parameters, locales, assertion depth).

## Layers

| Layer | Typical source | Depth |
|-------|----------------|-------|
| `behavior_spec` | `tests/integration/commands/*/test_*_behavior_specs.py` | defer + handler invoked |
| `integration` | `tests/integration/commands/*/test_*_matrix.py` | defer + command dispatch |
| `unit_logic` | `tests/unit/commands/*/test_*_matrix.py` | embed / response content |
| `unit_extension` | extension defer/dispatch tests | deferred |
| `e2e_live` | `tests/e2e_live/**/test_*_commands_live.py` | real Discord embed |

## CLI

```bash
python scripts/report_command_coverage.py --all
python scripts/report_command_coverage.py --group funcmd_name --verbose
python scripts/report_command_coverage.py --all --fail-under-config coverage/thresholds.yaml
```

Formats: `--format text|json|html`, optional `--output path`.

## Configuration

- [`coverage/overrides.yaml`](../../coverage/overrides.yaml) — expected matrix cells per group (classifier-driven + fun reference)
- [`coverage/command_handlers.json`](../../coverage/command_handlers.json) — manifest path → `commands.*` handler map
- [`coverage/thresholds.yaml`](../../coverage/thresholds.yaml) — CI minimum percentages per group/layer

Regenerate after manifest or handler changes:

```bash
python scripts/bootstrap_command_handlers.py
python scripts/build_matrix_overrides.py
python scripts/generate_domain_matrix_tests.py
```

## Matrix framework

| Module | Role |
|--------|------|
| `tests/helpers/command_matrix/resolver.py` | Resolve `commands.*` handlers from static map + AST |
| `tests/helpers/command_matrix/dimensions.py` | Shared dimension → kwargs / live option mapping |
| `tests/helpers/command_matrix/patches.py` | Per-domain DB/API mocks |
| `tests/helpers/domain_assertions/` | Per-group embed assertion rules |

Coverage **expected** cells come from YAML; **executed** cells from pytest matrix parametrization collectors.

## Fun reference

| Layer | Cases |
|-------|------:|
| `unit_logic` | 360 |
| `integration` | 9 |
| `behavior_spec` | 9 |
| `e2e_live` | 72 |

## CI

The `unit-and-mock` job runs pytest with `-n auto` and the matrix gate after unit/integration tests.
