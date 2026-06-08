# Live Discord E2E tests

Real end-to-end checks against Discord via the interactions API. Matrix cases from `coverage/overrides.yaml` drive all live tests.

## Requirements

See environment variables in [`.env.example`](../../.env.example). Use a permanent test guild with `TANJUN_E2E_BOOTSTRAP_MODE=api_only` for reliability.

## Run

```bash
pytest tests/e2e_live/test_commands_smoke_live.py -m live_discord -v
pytest tests/e2e_live/math -m live_discord -v
```

Filter by domain or case:

```bash
TANJUN_E2E_DOMAIN_FILTER=math_name pytest tests/e2e_live -m live_discord -v
TANJUN_E2E_CASE_FILTER=math_name pytest tests/e2e_live -m live_discord -v
```

Smoke a single matrix case:

```bash
python scripts/e2e_invoke_slash.py --tree-path "math_name math_calc_name"
python scripts/e2e_invoke_slash.py --case-id math_name_math_calc_name-command=calc-permission=admin
```

## Nightly sharded CI

[`.github/workflows/e2e-live-nightly.yml`](../../.github/workflows/e2e-live-nightly.yml) runs 13 parallel domain shards (~90–120 min each) with `TANJUN_E2E_DOMAIN_FILTER`.

## Setup/teardown hooks

Registered in [`tests/helpers/live_e2e/cleanup.py`](../../tests/helpers/live_e2e/cleanup.py):

| Hook | Purpose |
|------|---------|
| `moderation.ban` / `moderation.unban` | Ban/kick cleanup |
| `admin.create_temp_role` / `admin.delete_temp_role` | Role option placeholders |
| `giveaway.start` / `giveaway.end` | Giveaway lifecycle |
| `level.enable_with_xp` / `level.disable` | Level system |
| `channel.*` | Welcome/farewell/media/dead chat round-trips |
| `minigames.*` | Counting/wordchain channels |
| `utility.clear_afk` | AFK teardown |

Payload placeholders: `__owner__`, `__secondary__`, `__bot__`, `__role__`, `__attachment__`, `__disposable__`.

## Fun deep matrix

`funcmd_name` has 72 live cases (message variants × targets). Fun-specific live tests remain in `tests/e2e_live/fun/`; smoke suite uses the same matrix payload builder.

## Interactive commands

[`tests/helpers/live_discord/playwright_components.py`](../../tests/helpers/live_discord/playwright_components.py) clicks wizard/game buttons for `games_name` and `setup_name` follow-up interactions.
