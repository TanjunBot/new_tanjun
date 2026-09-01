# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-09-01

### Added

- **Botstatus API microservice**: Standalone high-performance service in `botstatus-api/` for status ingestion, health checks, Prometheus metrics, and Shields.io dynamic badges with Docker & Coolify support (#1140).
- **Twitch service resilience**: Automatic OAuth app token refresh on HTTP 401, chunked batching for >100 user IDs, and robust fallback Discord channel lookup with per-guild error isolation.
- **Heartbeat & status monitoring**: Tanjun bot heartbeat ping support to both Uptime Kuma and `botstatus-api` endpoints.

### Fixed

- **Audit log lookup error handling**: Prevent `DiscordServerError` (503/500) and transient HTTP failures from crashing log event listeners and suppressing log embeds (#3352).
- **MySQL connection recovery**: Handle and retry `OperationalError` (lost connection / 2013 / 2006) and `IncompleteReadError` on database connection drops with automatic pool purging (#3346).
- **Localization key alignment**: Synchronized `logs.inviteCreate.targetTypeLocales` keys across all 22 locale files with the discord.py `InviteTarget` enum (#3347).
- **Localization merge fixes**: Resolved missing and conflicted strings for bypass slowmode and pin messages across all languages (#3280, #3281).
- **UI & interaction fixes**: Fixed channel mention id mapping in `/twitch list`, confirm view message attribute resolution (#3282), and infinite latency display overflow (#3284).
- **Booster setup & test harness**: Resolved select menu conflicts and achieved zero skips in test suite.
- **Mypy module naming**: Resolved duplicate module name conflict for `botstatus-api` (#3354).

### Changed

- **Dependency updates**: Upgraded `pydantic` to 2.13.5, `pydantic-settings` to 2.15.0, `platformdirs` to 4.11.6, `openai` to 3.6.0, `mysql-connector-python` to 26.7.0.
- **Translations**: Updated Crowdin translations for all supported languages.

## [1.2.0] - 2026-06-03

### Added

- **Premium subscription system**: Full Patreon/Stripe integration for subscription management
  - Premium database schema with subscription and feature entitlement tables
  - PremiumService with database-backed validation replacing stub checks
  - Discord Entitlements integration
  - Premium management commands: grant, revoke, check, list
  - Pro tier: gate 15 existing features behind guild-level subscription
  - Plus tier: gate and enhance user-level features for individual subscribers
  - Free tier guarantee to ensure the bot remains excellent for non-subscribers
  - Premium-exclusive features for Pro and Plus subscribers
  - Premium localization and configuration: translatable premium strings and tier configuration
  - Premium upsell and trial system with upgrade prompts and premium info
  - External payment integration via Patreon/Stripe webhook receiver
  - Feature entitlement matrix defining free vs Pro vs Plus feature split (#1417–1430)
- **Health check framework**: Base system for startup validation and periodic health monitoring (#1409)
  - Discord API gateway health check for connection latency and intents (#1411)
  - OpenAI API health check for API key and basic completion capability (#1413)
  - Database connectivity health check (#1399)
  - Background loop health check to verify all task loops are running (#1416, #1469)
  - Twitch API health check
  - Locale file health check for integrity verification of locale files (#1460)
- Startup validation and caching for all guild-level configs to avoid cold-start latency (#1377)
- Async iterator protocol (`iter_rows`) to all models (#1479)
- Pagination to leaderboard command to avoid loading all rows at once (#1484)
- Pre-computation and caching of level thresholds per guild to avoid O(n) XP lookups (#1487)
- `py.typed` marker file for PEP 561 compliance (#1395)
- `.editorconfig` for consistent editor settings across contributors (#1400)
- `.dockerignore` to reduce Docker image size (#1382)
- `concurrent.futures` thread pool for sync I/O and external API calls
- Full project documentation replacing placeholder README (#1380)
- `asyncio.gather` for concurrent Discord API calls in minigame handlers (#1441)

### Changed

- Migrated AI integration from OpenAI to OpenRouter with `deepseek-v4-flash:free` as default (#1431, #1462)
- Replaced `print()` statements with proper logging throughout the codebase (#1384, #1470)
- Consolidated duplicate dependency management: removed `requirements.txt`, using `pyproject.toml` as single source of truth (#1387, #1467)
- Consolidated 9 fun commands into one parameterized command
- Consolidated 8 image filter commands into shared function
- Consolidated voice user tracking and XP calculation
- Consolidated counting duplication, fixed mypy config and audit log filters
- Replaced DB-based message tracking with in-memory tracking in dynamic slowmode
- Replaced `LogEnableModel` @dataclass with Pydantic BaseModel (#1476)
- Optimized Twitch API polling: reduced interval to 60s with batch notifications (#1489)
- Optimized counting minigame hot path: combined DB queries with early skip (#1456)
- Consolidated voice state update handlers into single dispatcher (#1370)
- Refined voice tracking: used `set` of `(user_id, guild_id)` tuples instead of `list[discord.Member]` (#1485)
- Upgraded test infrastructure and CI workflows
- Translated `stale.yml` workflow from German to English (#1394)
- Enhanced `healthcheck.py` to verify database connectivity, not just file existence (#1399)

### Fixed

- Resolved 13 critical runtime bugs from milestone 1.2
- Fixed various tech debt issues (3 batches) from milestone 1.2
- Fixed `execute_action` / `execute_query` mixup
- Fixed `interaction.reply` → `interaction.response.send_message` calls
- Fixed ticket creation bugs (params mixed up, reversed `opted_out` message)
- Fixed ticket not opening and tickets not closing
- Fixed giveaway ID not showing in giveaway footer
- Fixed `playerinfo` not working when not in a clan
- Fixed all logs being disabled
- Fixed autopublish not working
- Fixed Twitch online notification not working
- Fixed dynamic slowmode formula making no sense
- Fixed `joinToCreate` not working
- Fixed some categories not working in help command
- Various import error fixes and type annotation improvements

### Removed

- Removed `requirements.txt` in favor of `pyproject.toml` (#1387)
- Removed test-only `MockInteraction` from production `utility.py` (#1383)
- Removed `brawlstats` references and related functionality
- Removed Tenor GIF support (#1208)
- Removed new repo notice from `SECURITY.md`
- Removed `tmp.py` and fixed notifiedUsers memory leak

### Security

- Dependencies updated to latest versions, including security patches across the dependency tree

## [1.1.4] - 2026-01-01

### Changed

- Various dependency updates and maintenance

## [1.0.3] - 2025-01-02

### Fixed

- Fixed dynamic slowmode formula making no sense

## [1.0.2] - 2025-01-02

### Fixed

- Fixed `joinToCreate` not working

## [1.0.1] - 2025-01-02

### Fixed

- Fixed some categories not working in help command

## [1.0.0] - 2025-01-01

### Added

- Initial stable release of Tanjun Discord bot
- Moderation commands: kick, ban, timeout, purge, nickname, slowmode, lock, unlock, warn, viewwarns
- Utility commands: nuke, say, embedcreator, createEmoji, calc, randomnumber, num2word, plot
- Role management commands: createrole, deleterole
- Localization support for slash commands
- Embed creator with button and modal localization
- Tenor GIF integration
- Numeric string parser for calculations
- MySQL database integration
- CI/CD pipeline with GitHub Actions
- GitHub Issue forms (bug report, feature idea, security)
- Stale issue management workflow
- Dependabot and Renovate dependency management
- Python dependency management via requirements.txt
- Twitch online notification system
- Ticket system
- Dynamic slowmode
- Level/XP system
- Giveaway system
- Counting minigame
- Leaderboard

[1.2.0]: https://github.com/TanjunBot/new_tanjun/compare/ver/1.1.4...development
[1.1.4]: https://github.com/TanjunBot/new_tanjun/compare/ver/1.0.3...ver/1.1.4
[1.0.3]: https://github.com/TanjunBot/new_tanjun/compare/ver/1.0.2...ver/1.0.3
[1.0.2]: https://github.com/TanjunBot/new_tanjun/compare/ver/1.0.1...ver/1.0.2
[1.0.1]: https://github.com/TanjunBot/new_tanjun/compare/ver/1.0.0...ver/1.0.1
[1.0.0]: https://github.com/TanjunBot/new_tanjun/releases/tag/ver/1.0.0
