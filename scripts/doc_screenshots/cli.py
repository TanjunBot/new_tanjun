from __future__ import annotations

import argparse
from dataclasses import replace

from doc_screenshots.config import load_config, load_login_config
from doc_screenshots.manifest import load_manifest
from doc_screenshots.playwright_runner import login_interactive, run_manifest


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Capture Discord doc screenshots via Playwright (user account required).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "login",
        help="Open Discord login in a browser and save session for later runs.",
    )

    gen = sub.add_parser("generate", help="Run slash commands and save screenshots.")
    gen.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="ID",
        help="Capture only these manifest shot ids (repeatable).",
    )
    gen.add_argument(
        "--headed",
        action="store_true",
        help="Show the browser window (overrides DOC_SCREENSHOT_HEADLESS).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "login":
        auth = load_login_config()
        login_interactive(auth.auth_state_path, headless=False)
        return 0

    if args.command == "generate":
        config = load_config()
        manifest = load_manifest(config.manifest_path)
        shots = manifest.shots
        if args.only:
            allowed = set(args.only)
            shots = [s for s in shots if s.id in allowed]
            missing = allowed - {s.id for s in shots}
            if missing:
                raise SystemExit(f"Unknown shot ids in --only: {', '.join(sorted(missing))}")
        if manifest.default_wait_ms is not None:
            config = replace(config, default_wait_ms=manifest.default_wait_ms)

        if args.headed:
            config = replace(config, headless=False)

        run_manifest(config, shots, auth_state_path=config.auth_state_path)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
