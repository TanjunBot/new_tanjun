# Contributing to Tanjun

Thank you for considering contributing to Tanjun! This document provides guidelines and instructions to help you get started with development.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
  - [Clone the Repository](#clone-the-repository)
  - [Create a Virtual Environment](#create-a-virtual-environment)
  - [Install Dependencies](#install-dependencies)
  - [Environment Variables](#environment-variables)
  - [Install Pre-commit Hooks](#install-pre-commit-hooks)
- [Running the Bot](#running-the-bot)
  - [Running with Docker](#running-with-docker)
  - [Running Manually](#running-manually)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
  - [Ruff Linting and Formatting](#ruff-linting-and-formatting)
  - [Type Hints](#type-hints)
  - [Pre-commit Checks](#pre-commit-checks)
- [Pull Request Process](#pull-request-process)
- [Branch Naming Conventions](#branch-naming-conventions)
- [Commit Message Conventions](#commit-message-conventions)
- [Issue Tracking](#issue-tracking)

---

## Prerequisites

- **Python 3.12+** — The project targets Python 3.12. The CI environment uses Python 3.12.8 specifically.
- **MySQL or MariaDB** — A database server is required for data persistence.
- **Git** — For version control.
- **Docker (optional but recommended)** — For containerized development and deployment.

---

## Local Development Setup

### Clone the Repository

```bash
git clone https://github.com/TanjunBot/new_tanjun.git
cd new_tanjun
```

### Create a Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

> **Note:** The CI environment specifically uses Python 3.12.8. While any Python 3.12+ version should work for local development, using the closest match reduces the chance of environment-specific issues.

### Install Dependencies

The project uses `pyproject.toml` for dependency management. Install with pip:

```bash
# Install production dependencies
pip install .

# Install dev dependencies (includes testing tools, type stubs, etc.)
pip install -e ".[dev]"
```

> **Note:** There is no `requirements.txt` — all dependencies are managed through `pyproject.toml`.

### Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your configuration. Required variables:

| Variable | Description |
|----------|-------------|
| `token` | Discord bot token |
| `applicationId` | Discord application ID |
| `adminIds` | Comma-separated list of admin user IDs |
| `database_ip` | MySQL/MariaDB host |
| `database_port` | Database port (default: `3306`) |
| `database_user` | Database username |
| `database_password` | Database password |
| `database_schema` | Database name |

Optional variables (leave defaults if not using the feature) are documented in [`.env.example`](.env.example).

> **Note for testing:** A minimal `.env.test` file is included for the test suite. The test runner will use mock configuration for most tests.

### Install Pre-commit Hooks

Pre-commit hooks run automated checks (linting, formatting, type checking) before every commit:

```bash
pip install pre-commit
pre-commit install
```

The hooks run:
- **Ruff** — Linting and code formatting
- **Mypy** — Static type checking
- **Pre-commit default hooks** — Trailing whitespace, end-of-file fixes, YAML validation

Configuration is in [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

> **Note:** The pre-commit mypy configuration may be less strict than the CI mypy configuration. To ensure identical validation locally, update the mypy args in `.pre-commit-config.yaml` to match those in `.github/workflows/type_checking.yml`. See the [Mypy section](#type-hints) for the full list of flags.

---

## Running the Bot

### Running with Docker

The recommended way to run the bot for development:

```bash
docker compose up -d
```

This uses [`compose.yaml`](compose.yaml) and includes:
- Automatic restarts unless stopped
- Health checks every 30 seconds
- Timezone support

### Running Manually

With the virtual environment activated:

```bash
python main.py
```

---

## Running Tests

The test suite uses `pytest`. Tests are organized in tiers under [`tests/`](tests/):

| Tier | Path | Purpose |
|------|------|---------|
| Unit | `tests/unit/` | Pure logic, services, models, utils (mocked I/O) |
| Integration | `tests/integration/commands/`, `api/`, `extensions/` | Command handlers, `api.py`, extension cogs |
| E2E (mock) | `tests/e2e/` | Extension load, startup, listener flows (no live Discord) |
| E2E (live) | `tests/e2e_live/` | Optional real bot smoke tests |

### Run all tests

```bash
pytest
```

### Run by tier

```bash
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

CI runs unit tests, integration tests (excluding `slow` and `live_discord`), and mock E2E tests (`tests/e2e/`). Database integration tests run in a separate workflow job with Docker MariaDB.

### Coverage (85% total + per-file gate)

CI merges coverage from separate pytest runs. Locally:

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

### Database integration tests

API integration tests against MariaDB use `docker compose -f docker-compose.test.yml up -d` and:

| Variable | Default |
|----------|---------|
| `TANJUN_TEST_DB_HOST` | `127.0.0.1` |
| `TANJUN_TEST_DB_PORT` | `3307` |
| `TANJUN_TEST_DB_USER` | `test_user` |
| `TANJUN_TEST_DB_PASSWORD` | `test_password` |
| `TANJUN_TEST_DB_NAME` | `tanjun_test` |

Set `TANJUN_INTEGRATION=true` or leave DB unreachable to skip DB tests.

### Database schema changes

All tables are defined as `TableDef` models in `get_table_defs()` inside [`api.py`](api.py). Schema evolution is managed with [Alembic](https://alembic.sqlalchemy.org/) under [`migrations/versions/`](migrations/versions/).

When you change the database schema:

1. Update the `TableDef` in `get_table_defs()` (or [`table_def_models/extra_table_defs.py`](table_def_models/extra_table_defs.py)).
2. Add a new revision: `alembic revision -m "short description"` and implement `upgrade()` / `downgrade()`.
3. If the change repairs legacy production databases, add or update a fixture under [`tests/fixtures/schema_legacy/`](tests/fixtures/schema_legacy/) and cover it in [`tests/integration/api/test_schema_conformance.py`](tests/integration/api/test_schema_conformance.py).
4. Run migrations and conformance tests locally:

```bash
docker compose -f docker-compose.test.yml up -d --wait
export TANJUN_TEST_DB_HOST=127.0.0.1 TANJUN_TEST_DB_PORT=3307
export TANJUN_TEST_DB_USER=test_user TANJUN_TEST_DB_PASSWORD=test_password
export TANJUN_TEST_DB_NAME=tanjun_test
alembic upgrade head
pytest tests/integration/api/test_schema_conformance.py -v
```

Also update [`docs/database-schema.md`](docs/database-schema.md) when columns or tables change.

CI runs `scripts/check_schema_revision.py` so pull requests that touch schema definitions must include a new file under `migrations/versions/`.

Existing deployments: back up the database, then deploy. Docker and `create_tables()` call `ensure_database_schema()`, which runs `alembic upgrade head` when the schema is behind and **`alembic stamp head` automatically** when the live database already matches `TableDef` but `alembic_version` was never written (typical for databases created before Alembic). Manual `alembic stamp head` is only needed if you intentionally manage revisions outside the bot.

**Why TableDef + Alembic instead of a runtime ORM?** Tanjun’s data layer is built on asyncmy with explicit SQL in repositories and `api.py` (~65 tables, high query variety). SQLAlchemy is used only for migrations (sync PyMySQL). Moving runtime reads/writes to SQLAlchemy ORM would be a large, risky rewrite with little payoff for drift prevention—which `TableDef` (canonical schema) + Alembic (versioned upgrades) already solve. New work should extend `TableDef` and add Alembic revisions; a gradual ORM adoption per domain is possible later but is out of scope unless deliberately planned.

### Live Discord E2E (optional)

```bash
export TANJUN_TEST_BOT_TOKEN=...
export TANJUN_TEST_GUILD_ID=...
export TANJUN_TEST_CHANNEL_ID=...
pytest tests/e2e_live/ -m live_discord -v
```

Without `TANJUN_TEST_BOT_TOKEN`, live tests are skipped automatically.

### CI test configuration

GitHub Actions runs lint, unit tests, integration (split commands/api vs extensions), mock E2E, optional live E2E, then a coverage gate (`fail-under=85` + `scripts/check_coverage_per_file.py`).

> **Note:** The CI environment uses Python 3.12. Match locally with `pip install -e ".[dev]"`.

---

## Code Style

### Ruff Linting and Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting. Configuration is in [`pyproject.toml`](pyproject.toml) under the `[tool.ruff]` sections.

**Key settings:**
- Target version: Python 3.12
- Max line length: configured in `[tool.ruff.format]`
- Selected lint rules include: `E`, `W`, `F`, `I` (import sorting), `C901` (complexity), `UP` (pyupgrade), `A` (flake8-builtins), `B` (flake8-bugbear), `SIM` (simplify), `TID` (tidy imports), `N` (naming), `ANN` (flake8-annotations)

**Running Ruff manually:**

```bash
# Lint and auto-fix
ruff check . --fix

# Format
ruff format .

# Check for remaining issues (will exit non-zero if unfixable issues remain)
ruff check .
```

The CI workflow ([`.github/workflows/ruff_linter.yml`](.github/workflows/ruff_linter.yml)) runs `ruff check --fix` and `ruff format` on every push and PR, and auto-commits fixes.

### Type Hints

Mypy is used for static type checking. Configuration is in [`pyproject.toml`](pyproject.toml) under `[tool.mypy]` and in [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

**CI-level mypy flags** (from `.github/workflows/type_checking.yml`):

```bash
mypy . \
  --explicit-package-bases \
  --disallow-untyped-defs \
  --disallow-incomplete-defs \
  --no-implicit-optional \
  --warn-return-any \
  --warn-unused-ignores \
  --warn-redundant-casts \
  --warn-unreachable
```

**Guidelines:**
- All function signatures should include type annotations (parameters and return types).
- Use `from __future__ import annotations` where helpful for forward references.
- Prefer `| None` over `Optional[]` syntax (Python 3.10+ style, available in 3.12).
- Use `Any` sparingly and only when the type is truly dynamic.
- The CI creates/updates a tracking issue when mypy finds errors, and auto-closes it when all errors are resolved.

### Pre-commit Checks

The pre-commit hooks run automatically on `git commit`. They include:
1. **Ruff lint** — Auto-fixes issues where possible
2. **Ruff format** — Formats code
3. **Mypy** — Type checks
4. **Trailing whitespace** — Removes trailing whitespace
5. **End-of-file fixer** — Ensures files end with a newline
6. **YAML validation** — Validates YAML files
7. **Check added large files** — Warns about large files being added

To bypass hooks temporarily (e.g., for work-in-progress commits):

```bash
git commit --no-verify -m "message"
```

---

## Pull Request Process

1. **Find or create an issue** — All PRs should reference an existing issue. If no issue exists for your change, create one first.

2. **Create a branch** — Branch from `development` using the naming convention below.

3. **Make your changes** — Keep changes focused on the issue. Avoid unrelated refactoring.

4. **Run tests and linting locally** — Ensure nothing is broken:

   ```bash
   ruff check .
   ruff format . --check
   pytest
   ```

5. **Commit your changes** — Use conventional commit messages (see below).

6. **Push your branch**:

   ```bash
   git push origin your-branch-name
   ```

7. **Open a pull request** against the `development` branch.

8. **Request a review** — Add a comment to your PR:

   ```
   @coderabbitai review
   ```

   This will trigger [CodeRabbit](https://coderabbit.com) AI review. Address any review comments and re-request review as needed.

9. **Wait for CI checks** — The following workflows run automatically:
   - **CI** — Runs tests
   - **Ruff Lint & Format** — Linting and formatting
   - **Type Checking** — Mypy static analysis
   - **Stale issues/PRs** — Cleans up inactive items

10. **Squash-merge** — Once approved, the PR will be squash-merged into `development` and the branch deleted.

---

## Branch Naming Conventions

Use descriptive branch names that follow this pattern:

| Type | Format | Example |
|------|--------|---------|
| Bug fix | `fix/issue-{number}-{short-description}` | `fix/issue-42-fix-xp-calculation` |
| Feature | `feat/{short-description}` | `feat/add-role-rewards` |
| Refactor | `refactor/{short-description}` | `refactor/ticket-service` |
| Chore | `chore/{short-description}` | `chore/update-dependencies` |
| Localization | `l10n/*` | (reserved for Crowdin automation) |

- Use only lowercase letters, numbers, and hyphens.
- Include the issue number for bug fixes.
- Keep the description short (2–5 words).

---

## Commit Message Conventions

We follow conventional commit messages loosely:

```
type(scope): short description

Optional longer description explaining the _why_ and _what_.
```

**Types:**
- `fix:` — A bug fix
- `feat:` — A new feature
- `refactor:` — Code change that neither fixes a bug nor adds a feature
- `style:` — Formatting, linting, whitespace (no logic change)
- `test:` — Adding or updating tests
- `docs:` — Documentation only
- `chore:` — Maintenance, dependencies, build config
- `ci:` — CI/CD changes

**Scope** is optional but helpful. Examples:

```
fix(levels): correct XP calculation for voice channels

feat(admin): add bulk role assignment command

docs: update README with new configuration options
```

**Special markers:**
- `[ignore changelog]` — Add this to the commit message to skip Discord changelog notifications.

---

## Issue Tracking

- **Bug reports** — Use the issue tracker with labels `bug` and a clear description of steps to reproduce.
- **Feature requests** — Use the issue tracker with a description of the feature and its use case.
- **CI-generated issues** — The CI workflow automatically creates/updates issues for:
  - Automated test failures (label: `bug,failed-tests`)
  - Mypy typing errors (labels: `bug,mypy,typing-errors,automated-report`)

Work on issues tracked in the [milestones](https://github.com/TanjunBot/new_tanjun/milestones) for planned releases.

---

## Additional Resources

- [README.md](README.md) — Project overview and quick start
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Community guidelines
- [SECURITY.md](SECURITY.md) — Security vulnerability reporting
- [CHANGELOG.md](CHANGELOG.md) — Release history
- [Documentation](https://docs.tanjun.bot) — Full documentation
- [Support Server](https://discord.arion2000.xyz) — Community Discord

---

*Thank you for contributing to Tanjun! 🎉*
