from __future__ import annotations

import pytest

from diagnostics.registry import all_specs
from tests.helpers.command_coverage.inventory import root_group_for_path
from tests.helpers.command_matrix.test_runners import run_behavior_spec_test

pytestmark = [pytest.mark.integration, pytest.mark.asyncio]

_GROUPS = ['admin_channels_name', 'admin_emoji_name', 'admin_jointocreate_name', 'admin_localegroup_name', 'admin_messaging_name', 'admin_moderation_name', 'admin_purgegroup_name', 'admin_report_name', 'admin_role_name', 'admin_rolemanage_name', 'admin_setup_name', 'admin_triggermessages_name', 'admin_warn_name']


def _specs():
    return [
        s
        for s in all_specs()
        if s.tree_path and root_group_for_path(s.tree_path) in _GROUPS and not s.skip_reason
    ]


@pytest.mark.parametrize("spec", _specs(), ids=lambda s: s.id)
async def test_admin_behavior_spec(spec) -> None:
    await run_behavior_spec_test(spec)
