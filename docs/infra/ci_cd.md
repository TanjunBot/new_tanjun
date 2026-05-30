# CI/CD

Tanjun uses GitHub Actions for continuous integration and deployment. This page documents the available workflows and what they do.

## Workflows

### CI — Tests

**File:** `.github/workflows/ci.yml`

Triggers on every push and pull request to `development`.

- Runs the full pytest test suite
- Generates a JUnit XML report
- Posts test results as a comment on PRs

```bash
pytest --junitxml=test-results.xml
```

### Ruff Lint & Format

**File:** `.github/workflows/ruff_linter.yml`

Triggers on every push and pull request to `development`.

- Runs `ruff check --fix` to auto-fix lint issues
- Runs `ruff format` to format code
- Auto-commits any fixes back to the branch

### Type Checking

**File:** `.github/workflows/type_checking.yml`

Triggers on every push and pull request to `development`.

- Runs mypy with strict settings
- Creates/updates a tracking issue for any type errors found
- Auto-closes the tracking issue when all errors are resolved

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
# Tests
pytest

# Linting
ruff check .

# Formatting check
ruff format . --check

# Type checking
mypy .
```

## Adding a New Workflow

1. Create a `.yml` file in `.github/workflows/`
2. Define the trigger, jobs, and steps
3. Test by pushing to a feature branch

> **Tip:** For custom workflows that need a self-hosted runner, check the runner labels in existing workflows before adding new ones.
