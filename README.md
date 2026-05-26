# Tanjun [![Tanjun CI](https://github.com/TanjunBot/new_tanjun/actions/workflows/ci.yml/badge.svg?branch=development)](https://github.com/TanjunBot/new_tanjun/actions/workflows/ci.yml) [![Tanjun Status](https://status.tanjun.bot/api/badge/8/status)](https://status.tanjun.bot) [![Tanjun Uptime](https://status.tanjun.bot/api/badge/8/uptime)](https://status.tanjun.bot) [![License](https://img.shields.io/github/license/TanjunBot/new_tanjun)](LICENSE.txt)

![Tanjun Banner](https://github.com/TanjunBot/new_tanjun/assets/91985694/a3fdde70-b402-4a9c-89f3-35083942837e)

A powerful, feature-rich Discord bot built with [discord.py](https://github.com/Rapptz/discord.py) — moderation, levels, giveaways, minigames, AI integration, and much more.

> **Documentation:** [docs.tanjun.bot](https://docs.tanjun.bot)  
> **Support Server:** [Discord](https://discord.arion2000.xyz)  
> **Status Page:** [status.tanjun.bot](https://status.tanjun.bot)

---

## Features

### 🛡️ Moderation & Administration

- Ban, kick, timeout, warn with configurable warnings
- Purge messages, nuke channels, slowmode management
- Role management (add, remove, create, delete, copy, move)
- Lock/unlock channels, voice channel management
- Custom embed creator and message scheduling
- Ticket system and join-to-create voice channels
- Auto-moderation with triggered messages

### 📈 Leveling System

- XP tracking with configurable scaling and cooldowns
- Level-up messages with customizable channel and message
- Rank cards with role rewards
- Leaderboards and XP boosts
- Level blacklist for channels/roles/users

### 🎁 Giveaways

- Start, edit, end, and reroll giveaways
- Blacklist management (users and roles)
- Multiple winners support

### 🤖 AI Integration

- GPT-powered chat with custom situation prompts
- Token management system

### 🎮 Games & Minigames

- Counting (with configurable modes, challenges, and word chain)
- Akinator, Connect 4, Hangman, Tic-Tac-Toe, Wordle
- Rock Paper Scissors, Flag Quiz
- Country flags game

### 🖼️ Image Manipulation

- Resize, rescale, mirror, compress images
- Background removal and filter effects

### 📊 Logging

- Configurable log channels for various events
- Channel/role/user-specific blacklist for logs

### 🌍 Localization

- Multi-language support (English, German)
- Crowdin integration for community translations

### 🔄 Utility

- AFK status, avatar/banner display
- Boosted channel and role management
- Scheduled messages, Twitch integration
- Brawl Stars stats lookup
- Math tools (calculator, plot function, random numbers)
- Auto-publish announcements
- Feedback and reporting

### 🩺 Health Monitoring

- Startup validation and periodic health checks
- Database connectivity verification
- External API health checks (OpenAI, Twitch, GIPHY, Brawl Stars, GitHub, ImgBB, bytebin)
- Background loop health monitoring
- Docker healthcheck integration

---

## Quick Start

### Prerequisites

- Python 3.12+
- MySQL/MariaDB database
- Discord bot token and application ID

### Running with Docker (Recommended)

1. Clone the repository:

   ```bash
   git clone https://github.com/TanjunBot/new_tanjun.git
   cd new_tanjun
   ```

2. Copy the environment file and configure it:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start with Docker Compose:

   ```bash
   docker compose up -d
   ```

### Manual Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/TanjunBot/new_tanjun.git
   cd new_tanjun
   ```

2. Create a virtual environment:

   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy and configure the environment file:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run the bot:

   ```bash
   python main.py
   ```

---

## Configuration

The bot is configured via environment variables in a `.env` file. See [`.env.example`](.env.example) for all available options:

| Variable | Description |
|----------|-------------|
| `token` | Discord bot token |
| `applicationId` | Discord application ID |
| `adminIds` | Comma-separated list of admin user IDs |
| `database_*` | MySQL/MariaDB connection settings |
| `giphyAPIKey` | GIPHY API key |
| `openAIKey` | OpenAI API key |
| `twitchId` / `twitchSecret` | Twitch API credentials |
| `brawlstarsToken` | Brawl Stars API token |
| `ImgBBApiKey` | ImgBB API key |
| `bytebin_*` | bytebin pastebin credentials |
| `GithubAuthToken` | GitHub personal access token |
| `prefix` | Command prefix (default: `t.`) |

---

## Deployment

### Docker Compose

The included [`compose.yaml`](compose.yaml) provides:
- Automatic restarts unless stopped
- Health checks every 30 seconds
- Timezone support (default: Europe/Berlin)

```bash
docker compose up -d
```

### Updating

Update scripts for Linux (`update.sh`) and Windows (`update.bat`) are included in the repository. The Docker image is automatically built and published to `ghcr.io/tanjunbot/new_tanjun:latest` on pushes to the `master` branch.

---

## Project Structure

```text
├── ai/               # AI integration (GPT, token management)
├── assets/           # Static assets (images, fonts)
├── commands/         # Slash command implementations
│   ├── admin/        # Moderation and administration
│   ├── ai/           # AI-related commands
│   ├── channel/      # Channel management
│   ├── fun/          # Fun commands
│   ├── games/        # Game commands
│   ├── giveaway/     # Giveaway commands
│   ├── image/        # Image manipulation
│   ├── level/        # Leveling system
│   ├── logs/         # Logging configuration
│   ├── math/         # Math utilities
│   ├── minigames/    # Minigames (counting, word chain)
│   └── utility/      # Utility commands
├── extensions/       # Bot extension/cog modules
├── locales/          # Localization files (en.json, de.json)
├── loops/            # Background task loops
├── minigames/        # Minigame logic
├── tests/            # Test suite
├── main.py           # Bot entry point
├── api.py            # API server
├── config.py         # Configuration loader
├── models.py         # Database models
├── utility.py        # Shared utilities
├── localizer.py      # Localization system
├── compose.yaml      # Docker Compose configuration
└── Dockerfile        # Docker build file
```

---

## Contributing

We welcome contributions! Please check the [issue tracker](https://github.com/TanjunBot/new_tanjun/issues) for open issues or feature requests.

For setup instructions and guidelines, see CONTRIBUTING.md (coming soon).

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

---

## Security

See [`SECURITY.md`](SECURITY.md) for supported versions and vulnerability reporting instructions.

---

## Links

- **Documentation:** [docs.tanjun.bot](https://docs.tanjun.bot)
- **Support Server:** [discord.arion2000.xyz](https://discord.arion2000.xyz)
- **Status Page:** [status.tanjun.bot](https://status.tanjun.bot)
- **GitHub:** [TanjunBot/new_tanjun](https://github.com/TanjunBot/new_tanjun)

---

## License

This project is licensed under the terms specified in [`LICENSE.txt`](LICENSE.txt).

---

*Built with ❤️ by [EntchenEric](https://github.com/EntchenEric) and [Arion2000](https://github.com/2000Arion)*
