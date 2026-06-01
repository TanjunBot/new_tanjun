from __future__ import annotations

import asyncio
from typing import Any

from diagnostics.discovery import discover_all_specs
from diagnostics.harness import invoke_interaction_command
from diagnostics.kwargs_defaults import build_kwargs_for_handler
from diagnostics.models import CheckOutcome, CommandBehaviorSpec
from diagnostics.patches import extension_patches

_specs_cache: list[CommandBehaviorSpec] | None = None


def _load_spec_modules() -> None:
    from diagnostics.specs import load_all as _load

    _load()


def all_specs() -> list[CommandBehaviorSpec]:
    global _specs_cache
    if _specs_cache is None:
        _load_spec_modules()
        _specs_cache = discover_all_specs()
    return _specs_cache


def _resolve_kwargs(spec: CommandBehaviorSpec, handler: Any) -> dict[str, Any]:
    extra = spec.extra_kwargs
    if callable(extra):
        return extra()
    if extra is not None:
        return dict(extra)
    return build_kwargs_for_handler(handler)


async def run_spec(spec: CommandBehaviorSpec, bot: Any) -> CheckOutcome:
    if spec.skip_reason:
        return CheckOutcome(spec.id, True, spec.skip_reason, skipped=True)

    from diagnostics.discovery import _instantiate_group

    group = _instantiate_group(spec.group_cls)
    if group is None:
        return CheckOutcome(spec.id, False, "Could not instantiate command group")
    handler = getattr(group, spec.method_name, None)
    if handler is None:
        return CheckOutcome(spec.id, False, f"Handler {spec.method_name!r} not found on group")
    extra_kwargs = _resolve_kwargs(spec, handler)

    try:
        with extension_patches(spec.extension, spec.patch_targets) as mocks:
            interaction = await asyncio.wait_for(
                invoke_interaction_command(handler, owner=group, extra_kwargs=extra_kwargs),
                timeout=30.0,
            )
            if spec.assertions:
                await spec.assertions(interaction, mocks)
    except TimeoutError:
        return CheckOutcome(spec.id, False, "Handler timed out after 30s")
    except Exception as exc:
        return CheckOutcome(spec.id, False, str(exc))
    return CheckOutcome(spec.id, True, "OK")
