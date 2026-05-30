# Tanjun User Manual

A guide for Discord server owners and administrators.

---

## Getting Started

### Inviting Tanjun to Your Server

1. Visit the [Tanjun website](https://docs.tanjun.bot) and click the invite link
2. Select the Discord server you manage
3. Authorize the required permissions
4. The bot will join your server and be ready to use

### Command Prefix

The default command prefix is `t.`. All slash commands are also available — use `/` in Discord to see them.

### First Steps

After inviting Tanjun:

1. **Set up logging** — `/logs setup` to configure log channels
2. **Configure moderation** — Use the warn config commands to set thresholds
3. **Enable leveling** — Levels are enabled by default; customize with `/level config`
4. **Explore commands** — Use `/help` to see available commands

---

## 🛡️ Moderation & Administration

### Warning System

Warn users with automatic escalation:

- `/warn add @user [reason]` — Issue a warning
- `/warn remove @user <id>` — Remove a specific warning
- `/warn list @user` — View a user's warnings
- `/warn config` — Configure warning thresholds

**Threshold actions** (configured per guild):
- After N warnings: automatic timeout
- After M warnings: automatic kick
- After P warnings: automatic ban

### Moderation Commands

| Command | Description |
|---------|-------------|
| `/ban @user [reason]` | Ban a user |
| `/kick @user [reason]` | Kick a user |
| `/timeout @user <duration>` | Timeout a user |
| `/purge <count>` | Delete multiple messages |
| `/nuke` | Clone and delete a channel |
| `/slowmode <seconds>` | Set channel slowmode |
| `/lock` / `/unlock` | Lock/unlock a channel |

### Role Management

- `/role add @user @role` — Add a role
- `/role remove @user @role` — Remove a role
- `/role create <name>` — Create a new role
- `/role delete @role` — Delete a role
- `/role copy @role` — Copy a role and its permissions
- `/role move @role <position>` — Move a role in the hierarchy

### Embed Creator

- `/embed create` — Interactive embed creation wizard
- `/embed edit <message_id>` — Edit an existing embed
- `/embed delete <message_id>` — Delete an embed

---

## 📈 Leveling System

### How XP Works

Users earn XP by sending messages and being in voice channels:

- **Text XP**: Earned per message (configurable cooldown)
- **Voice XP**: Earned per time in voice channels (configurable cooldown)
- **XP Scaling**: Difficulty curve determines XP needed per level

### Commands

| Command | Description |
|---------|-------------|
| `/rank [@user]` | View rank card |
| `/leaderboard` | View server leaderboard |
| `/level config` | Configure leveling settings |
| `/level rewards` | Configure role rewards for levels |
| `/xp add @user <amount>` | Manually add XP (admin) |
| `/xp remove @user <amount>` | Remove XP (admin) |
| `/xp set @user <amount>` | Set XP (admin) |
| `/xp boost` | Configure XP boost multipliers |

### Configuration Options

- **Difficulty**: easy, medium, hard, extreme, custom
- **Level-up messages**: Customizable message and channel
- **Cooldowns**: Separate text and voice XP cooldowns
- **Blacklists**: Exclude channels, roles, or users from XP
- **Role Rewards**: Auto-assign roles at specific levels
- **Boosts**: Per-user, per-role, or per-channel XP multipliers

---

## 🎁 Giveaways

### Running a Giveaway

1. Use `/giveaway start <time> <winners> <prize>`
2. Set optional requirements (messages, account age, voice time)
3. Users click a button or use a command to enter
4. Winners are automatically chosen when the giveaway ends

### Commands

| Command | Description |
|---------|-------------|
| `/giveaway start` | Start a new giveaway |
| `/giveaway edit <id>` | Edit an existing giveaway |
| `/giveaway end <id>` | End a giveaway early |
| `/giveaway reroll <id>` | Pick new winners |
| `/giveaway blacklist` | Manage giveaway blacklist |

### Requirements

Giveaways can require:
- Minimum messages sent
- Minimum account age (days)
- Minimum voice channel time
- Specific channels with message counts
- Specific roles

---

## 🤖 AI Integration

### AI Chat

Tanjun includes GPT-powered AI chat functionality:

- `/ai chat <message>` — Chat with the AI
- `/ai situation [prompt]` — Set a custom situation prompt
- `/ai tokens` — Check your token balance
- `/ai reset` — Reset your conversation

### Token System

Each user has:
- **Free tokens**: Default allocation (renewable)
- **Plus tokens**: For premium users
- **Paid tokens**: Purchasable token packs

---

## 🎮 Games & Minigames

### Counting

A collaborative counting game where users take turns counting:

- `/counting set <channel>` — Set up counting in a channel
- `/counting mode` — Set counting mode (normal, challenge, etc.)
- `/counting goal` — Set a target number to reach

### Other Games

| Command | Description |
|---------|-------------|
| `/akinator` | Play Akinator |
| `/connect4 @opponent` | Play Connect 4 |
| `/hangman` | Play Hangman |
| `/wordle` | Play Wordle |
| `/rps @opponent` | Rock Paper Scissors |
| `/flagquiz` | Flag quiz game |
| `/wordchain` | Word chain game |

---

## 🖼️ Image Manipulation

| Command | Description |
|---------|-------------|
| `/image resize <url> <width> <height>` | Resize an image |
| `/image rescale <url> <scale>` | Scale an image by percentage |
| `/image mirror <url>` | Mirror/flip an image |
| `/image compress <url>` | Compress an image |
| `/image removebg <url>` | Remove image background |
| `/image filter <url> <filter>` | Apply image filters |

---

## 📊 Logging

### Setting Up Logs

1. Use `/logs setup <channel>` to set a log channel
2. Use `/logs enable/disable` to configure which events to log
3. Use `/logs blacklist` to exclude channels/roles/users

### Logged Events

| Category | Events |
|----------|--------|
| Members | Join, leave, ban, unban, nickname/role changes |
| Messages | Edit, delete |
| Channels | Create, delete, update |
| Roles | Create, delete, update |
| Invites | Create, delete |
| Moderation | Automod rules (create, update, delete), automod actions |
| Voice | Presence updates |
| Reactions | Add, remove |

---

## 🌍 Localization

Tanjun supports multiple languages:

| Language | Code | Status |
|----------|------|--------|
| English | en | Full |
| German | de | Full |

The bot automatically detects server language settings. Contributing translations is done through [Crowdin](https://crowdin.com).

---

## 🔄 Utility Commands

| Command | Description |
|---------|-------------|
| `/afk [reason]` | Set AFK status |
| `/avatar [@user]` | View user avatar |
| `/banner [@user]` | View user banner |
| `/help [command]` | Show help for commands |
| `/ping` | Check bot latency |
| `/status` | View bot health status |
| `/feedback <message>` | Send feedback |
| `/report @user <reason>` | Report a user |
| `/suggest <suggestion>` | Submit a suggestion |
| `/schedule <time> <message>` | Schedule a message |
| `/timer <duration>` | Set a timer |
| `/math calculate <expression>` | Calculate a math expression |
| `/math plot <formula>` | Plot a math function |
| `/math random <min> <max>` | Generate random number |
| `/brawl <tag>` | Look up Brawl Stars stats |
| `/twitch add <channel>` | Add Twitch notifications |
| `/boost` | Manage booster features |

---

## Docker Deployment

### Quick Start with Docker Compose

```bash
# Clone and configure
git clone https://github.com/TanjunBot/new_tanjun.git
cd new_tanjun
cp .env.example .env
# Edit .env with your configuration

# Start the bot
docker compose up -d
```

### Updating

```bash
# Linux
./update.sh

# Windows
./update.bat

# Or manually:
docker compose pull
docker compose up -d
```

---

## Troubleshooting

### Common Issues

**Bot doesn't respond to commands**
- Verify the bot has the required permissions
- Check if the bot is online on the Discord members list
- Ensure the prefix is correct (default: `t.`)

**Leveling not working**
- Check if leveling is enabled in the server
- Verify the user is not blacklisted
- Check text/voice cooldown settings

**Giveaways not starting**
- Ensure the bot has "Send Messages" and "Embed Links" permissions
- Check that the prize description is within limits
- Verify the giveaway duration is valid

### Support

- **Documentation**: [docs.tanjun.bot](https://docs.tanjun.bot)
- **Support Server**: [discord.arion2000.xyz](https://discord.arion2000.xyz)
- **Status Page**: [status.tanjun.bot](https://status.tanjun.bot)
- **GitHub Issues**: [TanjunBot/new_tanjun/issues](https://github.com/TanjunBot/new_tanjun/issues)
