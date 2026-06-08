#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import sys

from tests.helpers.command_matrix.iterators import iter_e2e_live_cases
from tests.helpers.command_matrix.models import MatrixCase
from tests.helpers.domain_assertions.registry import assert_matrix_live_response
from tests.helpers.fun_matrix import FUN_ACTIONS, iter_fun_live_cases
from tests.helpers.live_discord.config import load_live_e2e_config
from tests.helpers.live_discord.fun_commands import FunLiveCase, assert_fun_embed
from tests.helpers.live_discord.session import LiveGuildSession
from tests.helpers.live_discord.token_capture import read_user_token_from_auth_state


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test live slash command via interactions API")
    parser.add_argument("--tree-path", default="", help="Manifest tree path, e.g. 'math_name math_calc_name'")
    parser.add_argument("--case-id", default="", help="Structured case id (tree_path with underscores)")
    parser.add_argument("--action", choices=FUN_ACTIONS, default="hug")
    parser.add_argument("--target", choices=("self", "bot"), default="self")
    parser.add_argument("--message-kind", choices=("none", "short", "unicode", "max"), default="short")
    parser.add_argument("--domain", default="", help="Filter matrix cases by domain/group prefix")
    return parser.parse_args()


def _iter_cases(args: argparse.Namespace):
    cases = iter_e2e_live_cases()
    if args.domain:
        cases = [c for c in cases if args.domain in c.group or args.domain in c.tree_path]
    return cases


def _resolve_matrix_case(args: argparse.Namespace) -> MatrixCase | None:
    if args.tree_path:
        for case in _iter_cases(args):
            if case.tree_path == args.tree_path:
                return case
        raise SystemExit(f"Unknown tree path: {args.tree_path!r}")
    if args.case_id:
        for case in _iter_cases(args):
            if case.id == args.case_id:
                return case
        raise SystemExit(f"Unknown case id: {args.case_id!r}")
    return None


async def _run() -> int:
    args = _parse_args()
    config = load_live_e2e_config()
    token = config.user_token or read_user_token_from_auth_state(config.auth_state_path)
    if not token:
        print("No user token. Run: python scripts/e2e_discord_login.py", file=sys.stderr)
        return 1

    if not config.reuse_guild_id or not config.reuse_channel_id:
        print(
            "Set TANJUN_E2E_GUILD_ID and TANJUN_E2E_CHANNEL_ID "
            "(recommended: TANJUN_E2E_BOOTSTRAP_MODE=api_only).",
            file=sys.stderr,
        )
        return 1

    session = await LiveGuildSession.create()
    matrix_case = _resolve_matrix_case(args)
    if matrix_case is not None:
        result = await session.run_matrix_case(matrix_case)
        assert_matrix_live_response(result, matrix_case, session=session)
        embed = result.get("embed") or {}
        print(f"OK {matrix_case.id}: title={embed.get('title', '')!r}")
    else:
        case = next(
            (
                c
                for c in iter_fun_live_cases()
                if c.action == args.action
                and c.message_kind == args.message_kind
                and c.target == args.target
            ),
            None,
        )
        if case is None:
            from tests.helpers.live_discord.fun_commands import FunLiveCase

            case = FunLiveCase(action=args.action, message_kind=args.message_kind, target=args.target)
        embed = await session.run_fun_case(case)
        actor = session.user_username
        target = session.bot_username if case.target == "bot" else session.user_username
        assert_fun_embed(embed, case, actor_name=actor, target_name=target)
        print(f"OK {case.id}: title={embed.get('title', '')!r}")
    await session.teardown()
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_run()))


if __name__ == "__main__":
    main()
