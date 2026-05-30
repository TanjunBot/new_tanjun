# Architecture

This document describes the internal architecture of Tanjun, covering its module layout, design patterns, and key components.

---

## Project Structure

```
new_tanjun/
├── main.py                  # Bot entry point — creates and starts the bot
├── api.py                   # Database connection pool, table management, and DB operations
├── config.py                # Configuration loader (environment variables via pydantic-settings)
├── models.py                # Pydantic v2 data models for all database entities
├── utility.py               # Shared utility functions and helpers
├── localizer.py             # Localization system (i18n)
├── translator.py            # Discord translator integration
│
├── extensions/              # Cog-style extensions loaded by the bot
│   ├── admin.py             # Admin & moderation commands
│   ├── administration.py    # Server administration utilities
│   ├── ai.py                # AI/GPT chat integration
│   ├── channel.py           # Channel management
│   ├── error_handler.py     # Global error handling
│   ├── fun.py               # Fun commands
│   ├── games.py             # Game commands (Akinator, Connect 4, etc.)
│   ├── giveaway.py          # Giveaway system
│   ├── health_check.py      # Health check endpoint
│   ├── image.py             # Image manipulation commands
│   ├── level.py             # Leveling system
│   ├── listeners.py         # Event listeners (on_message, on_member_join, etc.)
│   ├── logs.py              # Logging system
│   ├── loops.py             # Background loop management
│   ├── math.py              # Math utility commands
│   ├── minigames.py         # Minigames (counting, word chain)
│   └── utility.py           # General utility commands
│
├── commands/                # Slash command implementations (separated by domain)
│   ├── admin/               # Moderation and administration
│   ├── ai/                  # AI-related commands
│   ├── channel/             # Channel management
│   ├── fun/                 # Fun commands
│   ├── games/               # Game commands
│   ├── giveaway/            # Giveaway commands
│   ├── image/               # Image manipulation
│   ├── level/               # Leveling system
│   ├── logs/                # Logging configuration
│   ├── math/                # Math utilities
│   ├── minigames/           # Minigames (counting, word chain)
│   └── utility/             # Utility commands
│
├── repositories/            # Repository pattern for database operations
│   ├── warning_repository.py
│   ├── level_config_repository.py
│   ├── level_role_repository.py
│   ├── log_blacklist_repository.py
│   ├── trigger_message_repository.py
│   ├── twitch_repository.py
│   └── xp_boost_repository.py
│
├── loops/                   # Background task loops
│   ├── alivemonitor.py      # Periodic health/liveness checks
│   ├── create_database_backup.py  # Scheduled DB backups
│   ├── giveaway.py          # Giveaway lifecycle management
│   ├── level.py             # XP decay and level processing
│   └── _voice_tracker.py    # Voice activity tracking for XP
│
├── health/                  # Health check framework
│   └── manager.py           # Central health check manager
│
├── locales/                 # Localization files
│   ├── en.json              # English translations
│   └── de.json              # German translations
│
├── assets/                  # Static assets
│   ├── images/              # Images for embeds and rank cards
│   └── fonts/               # Fonts for rank cards
│
├── tests/                   # Test suite (pytest)
│
├── compose.yaml             # Docker Compose configuration
├── Dockerfile               # Docker build file
├── pyproject.toml           # Python project configuration
├── .pre-commit-config.yaml  # Pre-commit hook configuration
└── .env.example             # Example environment configuration
```

---

## Design Patterns

### Extension/Cog Architecture

Tanjun uses discord.py's `commands.AutoShardedBot` with a hybrid architecture:

- **Extensions** (`extensions/`): Loaded as discord.py cogs, these define event listeners (on_ready, on_message, etc.) and register slash command groups.
- **Commands** (`commands/`): Individual slash command implementations, organized by domain. Each command group is registered by its corresponding extension.

This separation allows clean organization — extensions handle lifecycle and event wiring, while command files implement the actual slash command logic.

### Repository Pattern

Database operations are organized using the **Repository pattern** in `repositories/`. Each repository encapsulates all queries for a specific domain (warnings, level config, etc.), providing a clean API for the rest of the application.

### Dependency Injection

Services are wired through the `di` module (`di.py`), which provides centralized access to:

- Database connection pool
- Configuration
- Health check manager
- External API clients

### Pydantic Models

All data structures use **Pydantic v2** (`models.py`) for:

- Type validation and coercion (especially Discord ID strings)
- `from_row()` class methods for converting database rows to model instances
- `iter_rows()` async generators for streaming query results

---

## Key Components

### Bot Entry Point (`main.py`)

The main entry point:

1. Loads configuration from environment variables
2. Creates the `commands.AutoShardedBot` instance
3. Loads all extensions (cogs)
4. Creates database tables
5. Starts background loops
6. Launches the bot's web server (API)
7. Connects to Discord

### Database Layer (`api.py`)

The database layer provides:

- **Connection Pool**: Managed via asyncmy, with configurable pool size and timeouts
- **Table Management**: `create_tables()` creates all tables with dependency-aware ordering and schema migrations
- **Query Execution**: `execute_query()` and `execute_query_iter()` for parameterized queries
- **Table Definitions**: `get_table_definitions()` returns DDL for all 40+ tables

### Health Check System

The health monitoring system validates:

- Database connectivity
- External API health (OpenAI, Twitch, GIPHY, Brawl Stars, GitHub, ImgBB, bytebin)
- Background loop liveness
- Locale file integrity
- Docker health check endpoint

Health checks run:
1. On startup (before the bot is marked ready)
2. Periodically in the background (`alivemonitor.py`)
3. On demand via the `/status` command

### Configuration (`config.py`)

Configuration is loaded from environment variables using `pydantic-settings.BaseSettings`. Key groups:

| Group | Variables |
|-------|-----------|
| Discord | `token`, `applicationId`, `adminIds` |
| Database | `database_ip`, `database_port`, `database_user`, `database_password`, `database_schema` |
| External APIs | `giphyAPIKey`, `openAIKey`, `twitchId`/`twitchSecret`, `brawlstarsToken`, `ImgBBApiKey`, `GithubAuthToken`, `bytebin_url`/`bytebin_key` |
| Bot | `prefix` (default: `t.`), `owner_ids` |

### Localization System (`localizer.py`)

Tanjun supports i18n via:

- **Locale files**: JSON files in `locales/` (e.g., `en.json`, `de.json`)
- **Translator class**: Integrates with discord.py's translator system
- **Crowdin**: Community-driven translation platform for additional languages (planned)

### External API Clients

Tanjun integrates with several external services:

| API | Purpose |
|-----|---------|
| OpenAI | AI chat functionality |
| Twitch | Stream online notifications |
| GIPHY | GIF search and sharing |
| Brawl Stars | Player stats lookup |
| GitHub | Repository operations |
| ImgBB | Image hosting |
| bytebin | Pastebin-like text storage |

---

## Background Loops

Tanjun runs several periodic background tasks:

| Loop | Interval | Purpose |
|------|----------|---------|
| Alivemonitor | Every 5 min | Verify all health checks pass |
| Giveaway check | Every 30 sec | End giveaways and pick winners |
| Level processing | Every 60 sec | Process XP decay and level updates |
| Database backup | Configurable | Create periodic database backups |
| Voice tracker | Every 30 sec | Track voice channel activity for XP |

---

## Testing

Tests are located in `tests/` and use **pytest** with the following structure:

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test database operations with a real MySQL database
- **Mock config**: `tests/mock_config.py` provides test configuration without real environment variables

Run tests with:

```bash
pytest                       # All tests
pytest -v                    # Verbose output
pytest --cov=. --cov-report=term-missing  # With coverage
```
