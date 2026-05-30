# Tanjun Documentation

Welcome to the Tanjun documentation! Tanjun is a powerful, feature-rich Discord bot built with [discord.py](https://github.com/Rapptz/discord.py) — moderation, levels, giveaways, minigames, AI integration, and much more.

## Quick Links

- [Getting Started](user-manual.md#getting-started)
- [Architecture Overview](architecture.md)
- [Database Schema](database-schema.md)
- [Contributing Guide](https://github.com/TanjunBot/new_tanjun/blob/development/CONTRIBUTING.md)

## Project Overview

Tanjun is an all-in-one Discord bot designed for server management and community engagement. It includes:

| Category | Description |
|----------|-------------|
| 🛡️ Moderation | Ban, kick, timeout, warn, purge, nuke, slowmode |
| 📈 Leveling | XP tracking, rank cards, role rewards, leaderboards |
| 🎁 Giveaways | Start, edit, end, reroll giveaways with requirements |
| 🤖 AI | GPT-powered chat with custom situation prompts |
| 🎮 Games | Counting, Akinator, Connect 4, Hangman, Wordle, and more |
| 🖼️ Image | Resize, rescale, mirror, compress, background removal |
| 📊 Logging | Configurable event logging with blacklist support |
| 🌍 Localization | Multi-language support (English, German) |

## Technology Stack

- **Runtime:** Python 3.12+
- **Framework:** discord.py 2.7.1 (AutoShardedBot)
- **Database:** MySQL/MariaDB with asyncmy
- **Validation:** Pydantic v2
- **AI:** OpenAI API (GPT)
- **Containerization:** Docker with health checks

## Documentation Sections

- [**Architecture**](architecture.md) — Internal structure, modules, and design patterns
- [**Database Schema**](database-schema.md) — Complete table definitions and relationships
- [**User Manual**](user-manual.md) — Guide for server owners and administrators
- [**Contributing**](https://github.com/TanjunBot/new_tanjun/blob/development/CONTRIBUTING.md) — Development setup, coding standards, PR process

## Links

- [GitHub Repository](https://github.com/TanjunBot/new_tanjun)
- [Issue Tracker](https://github.com/TanjunBot/new_tanjun/issues)
- [Support Server](https://discord.arion2000.xyz)
- [Status Page](https://status.tanjun.bot)
