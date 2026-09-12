# CI/CD

Tanjun uses GitHub Actions for continuous integration and deployment. This page documents the workflows currently present in `.github/workflows/`.

## Workflows

### CI — Tests and quality gates

**File:** `.github/workflows/ci.yml`

Triggers on pushes (except `l10n*` branches), pull requests targeting
`development`, `master`, or `main`, and manual dispatch.

- Runs import/diagnostic smoke checks, Ruff, mypy, unit tests, integration
  tests, mock E2E tests, and the combined 85% coverage gate.
- Runs optional live Discord E2E checks on non-PR events when test secrets are
  configured; failures are non-blocking.
- Sends a Discord notification for selected release branches when configured.

```bash
pytest tests/unit -q
pytest tests/integration -m "not slow and not live_discord" -q
```

### Test — Legacy/branch test workflow

**File:** `.github/workflows/test.yml`

Runs on pushes to `main`/`development` and all pull requests. It runs unit,
integration, mock E2E, command coverage, and schema-revision checks.

### Docker image publishing

**File:** `.github/workflows/publish-ghcr.yml`

Pushes to `master` build and publish `ghcr.io/tanjunbot/new_tanjun:latest`
and a commit-SHA tag. Pushes to other branches do not publish images.

### Ruff, type checking, and maintenance

- `ruff_linter.yml` is manual-only and performs Ruff checks (it does not
  auto-fix or auto-commit).
- `type_checking.yml` runs on all pushes and pull requests, uploads reports,
  and manages a tracking issue for detected mypy errors.
- `stale.yml`, `crowdin.yml`, `versioning.yml`, `issues-discord-message.yml`,
  and `e2e-live-nightly.yml` provide scheduled or event-specific maintenance.

### Stale Issues & PRs

**File:** `.github/workflows/stale.yml`

- Marks inactive issues and PRs after 60 days
- Closes them after 90 days of inactivity
- Excludes issues with the `needs-triage` label
- Runs daily

### Crowdin Sync

**File:** `.github/workflows/crowdin.yml`

Triggers on pushes to `development` that change locale files.

- Uploads source strings to Crowdin
- Downloads translated files back to the repository
- Commits translation updates

## Running CI Locally

You can run the same checks that CI runs:

```bash
# Linting and formatting
ruff check .
ruff format . --check
# Type checking (same main CI invocation)
python -m mypy . --explicit-package-bases --no-error-summary --show-error-codes --soft-error-limit -1
# Unit tests
pytest tests/unit/ -q
```

## Adding a New Workflow

1. Create a `.yml` file in `.github/workflows/`
2. Define the trigger, jobs, and steps
3. Test by pushing to a feature branch

> **Tip:** For custom workflows that need a self-hosted runner, check the runner labels in existing workflows before adding new ones.
