# Configuration

Tanjun offers extensive per-server configuration to tailor the bot to your community's needs.

## General Commands

### Help

```
/help
```

Displays an overview of all available commands.

### Ping

```
/ping
```

Check the bot's latency to Discord and the database.

### Info

```
/info
```

Shows bot version, uptime, and server statistics.

## Server Configuration

### Prefix

Although Tanjun primarily uses slash commands, a legacy message prefix can be configured:

```
/config prefix !
```

### Admin Roles

Designate roles that can use admin commands:

```
/config admin add @role
/config admin remove @role
/config admin list
```

### Language / Locale

Set the server's language (if translations are available):

```
/config language de
```

Available languages: `en` (English), `de` (German).

### Join-to-Create

Automatic voice channel creation when members join a designated VC:

```
/config jtc enable #voice-channel
/config jtc disable
```

When enabled, joining the designated channel creates a temporary voice channel for that member.

## Moderation Settings

### Warning System

| Command | Description |
|---------|-------------|
| `/warn @user <reason>` | Warn a member |
| `/warnings @user` | View a member's warnings |
| `/clearwarns @user` | Clear all warnings for a member |

### Auto-Moderation

```
/config automod enable
/config automod disable
/config automod config
```

Configure automatic moderation rules including spam detection, banned words, and mention limits.

### Embed Creation

Create custom embed messages for announcements or rules:

```
/embed create
```

Interactive builder with fields for title, description, color, fields, footer, and author.

> **Tip:** Use `/embed create` to make attractive announcements without needing a separate bot.
