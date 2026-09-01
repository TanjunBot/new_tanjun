"""Pytest configuration and fixtures for Tanjun bot tests."""

import sys
import types
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

import tests.mock_config as mock_config

pytest_plugins = ["tests.helpers.wizard_flow"]

# Apply mock config before any test imports
mock_config.patch_config_module()

# Create a proper mock for discord that allows utility.py to import successfully
_discord_mock = MagicMock()
_discord_mock.User = MagicMock()
_discord_mock.Message = MagicMock()
_discord_mock.AllowedMentions = MagicMock()
_discord_mock.File = MagicMock()
from tests.helpers.discord_exceptions import (
    DiscordServerError,
    FakeEmbed,
    Forbidden,
    HTTPException,
    NotFound,
)

_discord_mock.Embed = FakeEmbed

_discord_mock.Forbidden = Forbidden
_discord_mock.HTTPException = HTTPException
_discord_mock.DiscordServerError = DiscordServerError
_discord_mock.NotFound = NotFound
_discord_mock.Entitlement = MagicMock()
_discord_mock.abc = MagicMock()
_discord_mock.abc.Messageable = MagicMock()
_discord_mock.ext = MagicMock()
_discord_mock.ext.commands = MagicMock()


class _FakeCog:
    @classmethod
    def listener(cls, *args, **kwargs):
        def decorator(func):
            return func

        return decorator


_discord_mock.ext.commands.Cog = _FakeCog
_discord_mock.ext.commands.Context = MagicMock()
_discord_mock.ext.commands.Bot = MagicMock()
_discord_mock.ext.commands.AutoShardedBot = MagicMock()
_discord_mock.ext.commands.command = lambda *a, **kw: lambda f: f
_discord_mock.ext.commands.hybrid_command = lambda *a, **kw: lambda f: f
_discord_mock.ext.commands.is_owner = lambda f: f
_discord_mock.ext.commands.cooldown = lambda *a, **kw: lambda f: f
_discord_mock.ext.commands.Command = type("Command", (), {})
class _FakeAppGroup:
    def __init__(self, *args, **kwargs) -> None:
        if args and "name" not in kwargs:
            self.name = args[0]
            self.description = args[1] if len(args) > 1 else ""
        else:
            self.name = kwargs.get("name", "")
            self.description = kwargs.get("description", "")
        self.commands: list = []
        for attr_name, member in type(self).__dict__.items():
            if attr_name.startswith("_"):
                continue
            if callable(member) and hasattr(member, "__discord_app_command_name__"):
                cmd = MagicMock()
                cmd.name = member.__discord_app_command_name__
                cmd.callback = member
                self.commands.append(cmd)

    def add_command(self, command) -> None:
        self.commands.append(command)


def _app_command(*args, **kwargs):
    def decorator(func):
        name = kwargs.get("name")
        if name is None and args:
            name = args[0]
        func.__discord_app_command_name__ = name
        return func

    return decorator


class _FakeAppCommandRange:
    @classmethod
    def __class_getitem__(cls, item: object) -> type:
        return cls


class _FakeAppCommandsModule:
    Group = _FakeAppGroup
    Command = type("AppCommand", (), {})
    AppCommandChannel = type("AppCommandChannel", (), {})
    AppCommandThread = type("AppCommandThread", (), {})
    command = staticmethod(_app_command)
    autocomplete = staticmethod(lambda *a, **k: lambda f: f)
    locale_str = staticmethod(lambda s: s)
    describe = staticmethod(lambda **kw: lambda f: f)
    choices = staticmethod(lambda *a, **kw: lambda f: f)
    Range = _FakeAppCommandRange
    Choice = staticmethod(lambda **kw: type("Choice", (), kw))

    def __getattr__(self, name: str) -> MagicMock:
        return MagicMock()


_discord_mock.app_commands = _FakeAppCommandsModule()
_discord_mock.Interaction = MagicMock()


class _FakeMember:
    def __init__(self, user_id: int = 111111111, name: str = "TestUser") -> None:
        self.id = user_id
        self.name = name
        self.display_name = name
        self.mention = f"<@{user_id}>"
        self.top_role = MagicMock(position=1)
        self.guild_permissions = MagicMock()
        self.ban = AsyncMock()
        self.kick = AsyncMock()
        self.edit = AsyncMock()
        self.add_roles = AsyncMock()
        self.remove_roles = AsyncMock()
        self.timeout = AsyncMock()
        self.bot = False
        self.display_avatar = MagicMock(url="https://cdn.discordapp.com/embed/avatars/0.png")
        self.guild_avatar = None
        self.avatar = None
        self.banner = None


class _FakeGuildChannel:
    pass


class _FakeTextChannel(_FakeGuildChannel):
    def __init__(self, channel_id: int = 444444444, guild: MagicMock | None = None) -> None:
        self.id = channel_id
        self.name = "test-channel"
        self.guild = guild or MagicMock()
        self.send = AsyncMock()
        self.permissions_for = MagicMock(return_value=MagicMock())


_discord_mock.Member = _FakeMember
_discord_mock.User = _FakeMember
_discord_mock.abc.GuildChannel = _FakeGuildChannel
_discord_mock.TextChannel = _FakeTextChannel
_discord_mock.VoiceState = MagicMock()
_discord_mock.Guild = MagicMock()
_discord_mock.CategoryChannel = MagicMock()
_discord_mock.VoiceChannel = MagicMock()
_discord_mock.StageChannel = MagicMock()
_discord_mock.TextChannel = MagicMock()
_discord_mock.Thread = MagicMock()


_discord_mock.Colour = type("Colour", (), {"__init__": lambda self, value=0: setattr(self, "value", value)})
_discord_mock.Color = _discord_mock.Colour
_discord_mock.Attachment = MagicMock()
_discord_mock.Object = MagicMock()
_discord_mock.PartialMessageable = MagicMock()
_discord_mock.Locale = type(
    "Locale",
    (),
    {"en_US": type("en_US", (), {"value": "en-US"})(), "de": type("de", (), {"value": "de"})()},
)

_discord_mock.ui = MagicMock()


class _FakeUIButton:
    def __init__(self, *args, **kwargs) -> None:
        pass

    @classmethod
    def __class_getitem__(cls, item):
        return cls


class _FakeView:
    def __init__(self, *args, **kwargs) -> None:
        self.timeout = kwargs.get("timeout")
        self.children: list = []
        self.message = None

    def add_item(self, item) -> None:
        self.children.append(item)

    async def wait(self) -> bool:
        return True

    def stop(self) -> None:
        pass


class _FakeSelect:
    def __init__(self, *args, **kwargs) -> None:
        self.options = kwargs.get("options", [])
        self.values: list = []
        self.placeholder = kwargs.get("placeholder", "")
        self.disabled = False

    @classmethod
    def __class_getitem__(cls, item):
        return cls


_discord_mock.ui.Modal = type("Modal", (), {"__init__": lambda self, *a, **k: None})
_discord_mock.ui.Select = _FakeSelect
_discord_mock.ui.TextInput = type("TextInput", (), {"__init__": lambda self, *a, **k: None})
_discord_mock.ui.View = _FakeView
_discord_mock.ui.Button = _FakeUIButton
_discord_mock.TextStyle = MagicMock()
_discord_mock.TextStyle.paragraph = "paragraph"
_discord_mock.TextStyle.short = "short"
_discord_mock.Role = MagicMock()


def _tasks_loop(*args, **kwargs):
    def decorator(func):
        task = MagicMock()
        task.start = MagicMock()
        task.is_running = MagicMock(return_value=False)
        task.cancel = MagicMock()
        return task

    return decorator


_discord_mock.ext.tasks = MagicMock()
_discord_mock.ext.tasks.loop = _tasks_loop

# Store original discord for tests that need it
_original_discord = sys.modules.get("discord", None)
sys.modules["discord"] = _discord_mock
sys.modules["discord.ext"] = _discord_mock.ext
sys.modules["discord.ext.commands"] = _discord_mock.ext.commands
sys.modules["discord.ext.tasks"] = _discord_mock.ext.tasks
sys.modules["discord.ui"] = _discord_mock.ui

from tests.helpers.discord import _ensure_discord_types

_ensure_discord_types()


@pytest.fixture
def mock_db_pool() -> MagicMock:
    """Create a mock database connection pool."""
    pool = MagicMock()
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__aenter__.return_value = cursor
    pool.acquire.return_value.__aenter__.return_value = conn
    return pool


@pytest.fixture
def mock_bot(mock_db_pool: MagicMock) -> MagicMock:
    """Create a mock bot instance with a database pool."""
    bot = MagicMock()
    bot._pool = mock_db_pool
    return bot


@pytest.fixture
def mock_bot_with_pool(mock_db_pool: MagicMock) -> MagicMock:
    bot = MagicMock()
    bot._pool = mock_db_pool
    bot._pool_ready = AsyncMock()
    bot.tree = MagicMock()
    bot.tree.add_command = MagicMock()
    bot.tree.get_commands = MagicMock(return_value=[])
    bot.load_extension = AsyncMock()
    bot.get_cog = MagicMock(return_value=None)
    bot.user = MagicMock()
    bot.user.id = 999999999
    return bot


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "e2e: end-to-end tests")
    config.addinivalue_line("markers", "live_discord: live Discord tests")
    config.addinivalue_line("markers", "slow: slow tests")


@pytest.fixture(autouse=True)
def _restore_discord_app_command_mocks() -> None:
    _ensure_discord_types()
    import discord

    discord.app_commands.Group = _FakeAppGroup
    discord.app_commands.command = _app_command
    discord.app_commands.autocomplete = lambda *a, **k: lambda f: f
    discord.app_commands.describe = lambda **kw: lambda f: f
    discord.app_commands.choices = lambda *a, **kw: lambda f: f
    discord.app_commands.locale_str = lambda s: s
    discord.app_commands.Range = _FakeAppCommandRange
    discord.app_commands.Choice = lambda **kw: type("Choice", (), kw)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo) -> None:
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.passed:
        return
    if not hasattr(item, "callspec"):
        return
    params = item.callspec.params
    from tests.helpers.command_coverage.collectors.pytest_registry import register_coverage_cell
    from tests.helpers.command_coverage.models import AssertionDepth, CoverageCell, LayerKind

    if "case" in params:
        case = params["case"]
        register_coverage_cell(
            CoverageCell(
                tree_path=case.tree_path,
                layer=case.layer,
                dimensions=dict(case.dimensions),
                assertion_depth=AssertionDepth.OUTPUT,
                source="pytest:passed",
            )
        )
    elif "spec" in params:
        spec = params["spec"]
        if getattr(spec, "tree_path", None):
            register_coverage_cell(
                CoverageCell(
                    tree_path=spec.tree_path,
                    layer=LayerKind.BEHAVIOR_SPEC,
                    dimensions={},
                    assertion_depth=AssertionDepth.OUTCOME,
                    source="pytest:passed",
                )
            )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        path = str(item.fspath)
        if "/tests/unit/" in path:
            item.add_marker(pytest.mark.unit)
        elif "/tests/integration/" in path:
            item.add_marker(pytest.mark.integration)
        elif "/tests/e2e_live/" in path:
            item.add_marker(pytest.mark.live_discord)
            item.add_marker(pytest.mark.e2e)
        elif "/tests/e2e/" in path:
            item.add_marker(pytest.mark.e2e)


@pytest.fixture
def mock_command_info():
    from tests.helpers.discord import make_command_info

    return make_command_info()


# --- Integration test fixtures (requires test database container) ---


@pytest.fixture(scope="session")
def integration_mode() -> str:
    """
    Return the integration test mode.

    Set TANJUN_INTEGRATION=true in environment to enable real database tests.
    Tests default to 'skip' to avoid requiring a running test DB.
    """
    import os

    return os.environ.get("TANJUN_INTEGRATION", "false").lower()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def integration_db_pool():
    """
    Create a real database connection pool pointing at the test database.

    Requires the test database to be running (e.g. via docker-compose.test.yml):
        docker compose -f docker-compose.test.yml up -d

    Yields the pool and drops + recreates all tables on teardown so each
    test session starts with a clean schema.
    """
    import asyncio
    import os

    import asyncmy

    host = os.environ.get("TANJUN_TEST_DB_HOST", "localhost")
    port = int(os.environ.get("TANJUN_TEST_DB_PORT", "3307"))
    user = os.environ.get("TANJUN_TEST_DB_USER", "test_user")
    password = os.environ.get("TANJUN_TEST_DB_PASSWORD", "test_password")
    db = os.environ.get("TANJUN_TEST_DB_NAME", "tanjun_test")

    os.environ.setdefault("TANJUN_TEST_DB_HOST", host)
    os.environ.setdefault("TANJUN_TEST_DB_PORT", str(port))
    os.environ.setdefault("TANJUN_TEST_DB_USER", user)
    os.environ.setdefault("TANJUN_TEST_DB_PASSWORD", password)
    os.environ.setdefault("TANJUN_TEST_DB_NAME", db)

    from alembic import command
    from utils.db_migration import _alembic_config
    from utils.schema_conformance import load_schema_drift_errors

    cfg = _alembic_config()
    command.upgrade(cfg, "head")
    if load_schema_drift_errors():
        command.downgrade(cfg, "base")
        command.upgrade(cfg, "head")

    try:
        pool = await asyncmy.create_pool(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            minsize=2,
            maxsize=16,
        )
    except Exception as exc:
        pytest.fail(f"Test database not available: {exc}")

    # Set the global pool so api._get_pool() resolves
    import api
    from api import set_bot

    _fake_bot = MagicMock()
    _fake_bot._pool = pool
    original_bot = api._bot
    set_bot(_fake_bot)

    yield pool

    pool.close()
    try:
        await asyncio.wait_for(pool.wait_closed(), timeout=5.0)
    except TimeoutError:
        pass

    set_bot(original_bot)
