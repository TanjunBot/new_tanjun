#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export TANJUN_TEST_DB_HOST="${TANJUN_TEST_DB_HOST:-127.0.0.1}"
export TANJUN_TEST_DB_PORT="${TANJUN_TEST_DB_PORT:-3307}"
export TANJUN_TEST_DB_USER="${TANJUN_TEST_DB_USER:-test_user}"
export TANJUN_TEST_DB_PASSWORD="${TANJUN_TEST_DB_PASSWORD:-test_password}"
export TANJUN_TEST_DB_NAME="${TANJUN_TEST_DB_NAME:-tanjun_test}"
export TANJUN_INTEGRATION="${TANJUN_INTEGRATION:-true}"

if [[ -f .env.test ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env.test
  set +a
fi

echo "==> ruff check"
ruff check .

echo "==> ruff format --check"
ruff format . --check

echo "==> lint_tests"
python3 scripts/lint_tests.py

echo "==> mypy"
mypy . --explicit-package-bases --no-error-summary --show-error-codes --soft-error-limit -1

echo "==> unit tests"
pytest tests/unit/ -n auto --cov=. --cov-report= --cov-fail-under=0 -q

echo "==> integration tests"
pytest tests/integration/commands tests/integration/api -n 4 --cov=. --cov-append --cov-report= --cov-fail-under=0 -q
pytest tests/integration/extensions -n 4 --cov=. --cov-append --cov-report= --cov-fail-under=0 -q

echo "==> e2e tests"
pytest tests/e2e/ --cov=. --cov-append --cov-report= --cov-fail-under=0 -q

echo "==> coverage gate"
coverage json -o coverage.json
coverage report --fail-under=85
python3 scripts/check_coverage_per_file.py --min 85 --coverage-json coverage.json

echo "CI local: all checks passed"
