# Leveling System

Tanjun includes a comprehensive leveling system to reward active members on your server.

## How It Works

Members earn XP for participating in your server:

- **Text messages** — XP per message (configurable cooldown prevents spam farming)
- **Voice activity** — XP for time spent in voice channels
- **Special events** — Bonus XP can be awarded for specific activities

## Setup

### Enable Leveling

By default, leveling is enabled once the bot has the necessary permissions. You can configure it per-server using the `/level` commands.

### Commands

| Command | Description |
|---------|-------------|
| `/rank` | View your current level and XP |
| `/leaderboard` | View the top members on this server |
| `/level config` | Configure leveling settings |
| `/level rewards` | Manage role rewards for reaching levels |

## Role Rewards

You can set up automatic role assignments when members reach certain levels:

1. Use `/level rewards add @role <level>` to assign a role at a specific level
2. Members will automatically receive the role when they reach that level
3. Use `/level rewards remove @role` to remove a reward

> **Note:** The bot needs the `Manage Roles` permission to assign role rewards.

## XP Scaling

By default, XP requirements increase per level:

- **Simple scaling** — Each level requires more XP than the last
- **Configurable** — Admins can adjust the XP rate and cooldown settings

## XP Boosts

Temporarily boost XP gains for specific roles or channels:

- `/level boost add @role <multiplier>` — Boost XP for a role
- `/level boost add #channel <multiplier>` — Boost XP in a channel
- `/level boost remove @role` — Remove a boost
- `/level boost list` — View active boosts

## Disabling Leveling

To disable XP tracking entirely, use `/level config disable`. To re-enable, use `/level config enable`.
