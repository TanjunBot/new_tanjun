# Database Schema

This document describes all database tables used by Tanjun. The database is MySQL/MariaDB with InnoDB engine for all tables.

---

## Overview

Tanjun uses approximately 40 tables organized by domain:

| Domain | Tables | Description |
|--------|--------|-------------|
| 🛡️ Moderation | `warnings`, `warn_config`, `reports`, `blockedReporters`, `reportchannel` | Warning and report system |
| 📈 Leveling | `level`, `levelConfig`, `levelRole`, `level_roles_group`, `blacklistedUser`, `blacklisted_role`, `blacklistedChannel`, `userXpBoost`, `roleXpBoost`, `channelXpBoost` | XP tracking, leveling, and role rewards |
| 🎁 Giveaways | `giveaway`, `giveaway_channelRequirement`, `giveawayParticipant`, `giveawayRoleRequirement`, `giveawayVoiceTime`, `giveawayNewMessage`, `giveawayBlacklistedRole`, `giveawayBlacklistedUser`, `giveaway_channelMessages` | Full giveaway system |
| 📊 Logging | `log_channel`, `log_channel_blacklist`, `logRoleBlacklist`, `logBlacklistChannel`, `logUserBlacklist`, `log_enables` | Event logging configuration |
| 🎮 Games | `counting`, `counting_challenge`, `counting_modes`, `wordchain` | Minigame state tracking |
| 🤖 AI | `aiToken`, `aiSituations` | AI token management and situation prompts |
| 💬 Communication | `scheduledMessages`, `triggerMessages`, `triggerMessagesChannel` | Message scheduling and triggers |
| 🎫 Tickets | `ticketMessages`, `tickets` | Ticket system |
| 👋 Welcome/Leave | `welcome_channel`, `leave_channel` | Welcome and leave messages |
| ✅ Misc | `afk_users`, `afkMessages`, `autopublish`, `feedbackBlocked`, `booster_channel`, `claimedBoosterChannel`, `boosterRole`, `claimedBoosterRole`, `channel_overwrites`, `dynamicslowmode`, `dynamicslowmode_messages`, `join_to_create_channel`, `mediaChannel`, `message_tracking_opt_out`, `twitchOnlineNotification`, `brawlstarsLinkedAccounts` | Various features |

---

## Domain-Specific Tables

### 🛡️ Moderation

#### `warnings`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT AUTO_INCREMENT PK | Warning identifier |
| `guild_id` | VARCHAR(20) NOT NULL | Discord guild ID |
| `user_id` | VARCHAR(20) NOT NULL | Warned user's Discord ID |
| `reason` | VARCHAR(255) | Reason for the warning |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | When the warning was issued |
| `expires_at` | TIMESTAMP NULL | Optional expiration date |
| `created_by` | VARCHAR(20) NOT NULL | Moderator who issued the warning |
| `escalation_level` | INT DEFAULT 0 | Escalation level for automatic action |

#### `warn_config`

| Column | Type | Description |
|--------|------|-------------|
| `guild_id` | VARCHAR(20) PK | Discord guild ID |
| `expiration_days` | INT DEFAULT 0 | Days until warning expires (0 = never) |
| `timeout_threshold` | INT DEFAULT 0 | Warnings before timeout |
| `timeout_duration` | INT DEFAULT 0 | Timeout duration in minutes |
| `kick_threshold` | INT DEFAULT 0 | Warnings before kick |
| `ban_threshold` | INT DEFAULT 0 | Warnings before ban |

#### `reports`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT AUTO_INCREMENT PK | Report identifier |
| `guild_id` | VARCHAR(20) | Discord guild ID |
| `user_id` | VARCHAR(20) | Reported user's Discord ID |
| `reporterId` | VARCHAR(20) | Reporter's Discord ID |
| `reason` | VARCHAR(1024) | Report reason |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Report creation time |
| `accepted` | TINYINT(1) DEFAULT 0 | Whether the report was accepted |
| `accepted_at` | TIMESTAMP NULL | When the report was accepted |
| `acceptedBy` | VARCHAR(20) | Moderator who accepted |
| `resolved` | TINYINT(1) DEFAULT 0 | Whether the report was resolved |
| `resolved_at` | TIMESTAMP NULL | When the report was resolved |
| `resolvedBy` | VARCHAR(20) | Moderator who resolved |

---

### 📈 Leveling

#### `level`

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | VARCHAR(20) NOT NULL | Discord user ID |
| `guild_id` | VARCHAR(20) NOT NULL | Discord guild ID |
| `xp` | INT UNSIGNED DEFAULT 0 | Total XP accumulated |
| `customBackground` | VARCHAR(255) | Custom rank card background URL |
| `last_xp_gain` | DATETIME DEFAULT NOW() | Last text XP gain timestamp |
| `last_voice_xp_gain` | DATETIME DEFAULT NOW() | Last voice XP gain timestamp |
| **PK** | `(user_id, guild_id)` | |

#### `levelConfig`

| Column | Type | Description |
|--------|------|-------------|
| `guild_id` | VARCHAR(20) PK | Discord guild ID |
| `difficulty` | ENUM('easy','medium','hard','extreme','custom') | XP difficulty curve |
| `customFormula` | VARCHAR(255) | Custom level formula |
| `level_up_messageActive` | TINYINT(1) DEFAULT 1 | Whether level-up messages are enabled |
| `level_up_message` | VARCHAR(1000) | Custom level-up message template |
| `level_up_channel_id` | VARCHAR(20) | Channel for level-up announcements |
| `active` | TINYINT(1) DEFAULT 1 | Whether leveling is enabled |
| `textCooldown` | INT DEFAULT 60 | Seconds between text XP gains |
| `voiceCooldown` | INT DEFAULT 60 | Seconds between voice XP gains |

#### `levelRole`

| Column | Type | Description |
|--------|------|-------------|
| `role_id` | VARCHAR(20) NOT NULL | Role to assign |
| `guild_id` | VARCHAR(20) NOT NULL | Discord guild ID |
| `level` | INT UNSIGNED DEFAULT 0 | Level required to earn this role |
| **PK** | `(role_id, guild_id)` | |

#### `userXpBoost` / `roleXpBoost` / `channelXpBoost`

These tables share the same structure:

| Column | Type | Description |
|--------|------|-------------|
| `user_id`/`role_id`/`channel_id` | VARCHAR(20) NOT NULL | Entity being boosted |
| `guild_id` | VARCHAR(20) NOT NULL | Discord guild ID |
| `boost` | DECIMAL(4,2) UNSIGNED DEFAULT 1 | XP multiplier |
| `additive` | TINYINT(1) DEFAULT 0 | Whether boost is additive |
| `boosted_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | When the boost was applied |
| **PK** | `(entity_id, guild_id)` | |

#### Blacklist Tables (`blacklistedUser`, `blacklisted_role`, `blacklistedChannel`)

| Column | Type | Description |
|--------|------|-------------|
| `entity_id` | VARCHAR(20) NOT NULL | Discord ID of the entity |
| `guild_id` | VARCHAR(20) NOT NULL | Discord guild ID |
| `reason` | VARCHAR(255) | Reason for blacklisting |
| `blacklisted_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | When blacklisted |
| **PK** | `(entity_id, guild_id)` | |

---

### 🎁 Giveaways

#### `giveaway`

| Column | Type | Description |
|--------|------|-------------|
| `giveaway_id` | INT UNSIGNED AUTO_INCREMENT PK | Giveaway identifier |
| `guild_id` | VARCHAR(20) NOT NULL | Discord guild ID |
| `title` | VARCHAR(128) NOT NULL | Giveaway title |
| `description` | VARCHAR(1024) | Giveaway description |
| `winners` | TINYINT(4) DEFAULT 1 | Number of winners |
| `withButton` | TINYINT(1) DEFAULT 1 | Whether to use button entry |
| `customName` | VARCHAR(32) | Custom entry button label |
| `sponsor` | VARCHAR(20) | Sponsor user ID |
| `price` | VARCHAR(64) | Prize description |
| `message` | VARCHAR(128) | Custom message |
| `endtime` | DATETIME NOT NULL | When the giveaway ends |
| `starttime` | DATETIME | When the giveaway started |
| `started` | TINYINT(1) DEFAULT 0 | Whether the giveaway has started |
| `ended` | TINYINT(1) DEFAULT 0 | Whether the giveaway has ended |
| `newMessageRequirement` | SMALLINT UNSIGNED | Minimum messages to enter |
| `dayRequirement` | SMALLINT UNSIGNED | Minimum account age (days) |
| `voiceRequirement` | SMALLINT UNSIGNED | Minimum voice minutes |
| `sendFailed` | TINYINT(1) DEFAULT 0 | Whether DM notification failed |
| `channel_id` | VARCHAR(20) | Channel where giveaway is posted |
| `messageId` | VARCHAR(20) DEFAULT "pending" | Discord message ID |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | When the giveaway was created |

#### Giveaway Relationship Tables

| Table | PK | Description |
|-------|----|-------------|
| `giveawayParticipant` | `(user_id, giveaway_id)` | Users who entered the giveaway |
| `giveaway_channelRequirement` | `(giveaway_id, channel_id)` | Required channels with minimum message counts |
| `giveawayRoleRequirement` | `(role_id, giveaway_id)` | Required roles to enter |
| `giveawayVoiceTime` | `(giveaway_id, user_id)` | Tracked voice minutes per user |
| `giveawayNewMessage` | `(giveaway_id, user_id)` | Tracked new messages per user |
| `giveaway_channelMessages` | `(giveaway_id, channel_id, user_id)` | Per-channel message counts for requirements |
| `giveawayBlacklistedUser` | `(user_id, guild_id)` | Users blocked from giveaways |
| `giveawayBlacklistedRole` | `role_id PK` | Roles blocked from giveaways |

---

### 📊 Logging

#### `log_enables`

| Column | Type | Description |
|--------|------|-------------|
| `guild_id` | VARCHAR(20) PK | Discord guild ID |
| `automodRuleCreate` | TINYINT(1) DEFAULT 1 | Log automod rule creation |
| `automodRuleUpdate` | TINYINT(1) DEFAULT 1 | Log automod rule updates |
| `automodRuleDelete` | TINYINT(1) DEFAULT 1 | Log automod rule deletion |
| `automodAction` | TINYINT(1) DEFAULT 0 | Log automod actions |
| `guild_channelDelete` | TINYINT(1) DEFAULT 1 | Log channel deletion |
| `guild_channelCreate` | TINYINT(1) DEFAULT 1 | Log channel creation |
| `guild_channelUpdate` | TINYINT(1) DEFAULT 1 | Log channel updates |
| `guildUpdate` | TINYINT(1) DEFAULT 1 | Log guild setting changes |
| `inviteCreate` | TINYINT(1) DEFAULT 1 | Log invite creation |
| `inviteDelete` | TINYINT(1) DEFAULT 0 | Log invite deletion |
| `memberJoin` | TINYINT(1) DEFAULT 1 | Log member joins |
| `memberLeave` | TINYINT(1) DEFAULT 1 | Log member leaves |
| `memberUpdate` | TINYINT(1) DEFAULT 1 | Log member profile updates |
| `userUpdate` | TINYINT(1) DEFAULT 1 | Log user profile updates |
| `memberBan` | TINYINT(1) DEFAULT 1 | Log member bans |
| `memberUnban` | TINYINT(1) DEFAULT 1 | Log member unbans |
| `presenceUpdate` | TINYINT(1) DEFAULT 1 | Log presence changes |
| `messageEdit` | TINYINT(1) DEFAULT 1 | Log message edits |
| `messageDelete` | TINYINT(1) DEFAULT 1 | Log message deletions |
| `reactionAdd` | TINYINT(1) DEFAULT 0 | Log reaction additions |
| `reactionRemove` | TINYINT(1) DEFAULT 0 | Log reaction removals |
| `guildRoleCreate` | TINYINT(1) DEFAULT 1 | Log role creation |
| `guildRoleDelete` | TINYINT(1) DEFAULT 1 | Log role deletion |
| `guildRoleUpdate` | TINYINT(1) DEFAULT 1 | Log role updates |

The following 4 tables share a simple `(guild_id, entity_id)` structure for log routing:

| Table | PK | Purpose |
|-------|----|---------|
| `log_channel` | `(guild_id, channel_id)` | Which channels receive logs |
| `log_channel_blacklist` | `(guild_id, channel_id)` | Channels excluded from logging |
| `logRoleBlacklist` | `(guild_id, role_id)` | Roles excluded from logging |
| `logBlacklistChannel` | `(guild_id, channel_id)` | Channels excluded from log content |
| `logUserBlacklist` | `(guild_id, user_id)` | Users excluded from logging |

---

### 🎮 Games

#### `counting`

| Column | Type | Description |
|--------|------|-------------|
| `channel_id` | VARCHAR(20) PK | Discord channel ID |
| `progress` | INT UNSIGNED DEFAULT 0 | Current count |
| `last_counter_id` | VARCHAR(20) | Last user who counted |
| `guild_id` | VARCHAR(20) | Discord guild ID |

#### `counting_challenge`

Same structure as `counting`, used for challenge mode counting.

#### `counting_modes`

| Column | Type | Description |
|--------|------|-------------|
| `channel_id` | VARCHAR(20) PK | Discord channel ID |
| `progress` | INT DEFAULT 0 | Current count |
| `mode` | TINYINT UNSIGNED DEFAULT 0 | Counting mode |
| `goal` | INT | Target number to reach |
| `last_counter_id` | VARCHAR(20) | Last user who counted |
| `guild_id` | VARCHAR(20) | Discord guild ID |

#### `wordchain`

| Column | Type | Description |
|--------|------|-------------|
| `channel_id` | VARCHAR(20) PK | Discord channel ID |
| `word` | VARCHAR(1028) | Last word in the chain |
| `last_user_id` | VARCHAR(20) | Last user who played |
| `guild_id` | VARCHAR(20) | Discord guild ID |

---

### 🤖 AI

#### `aiToken`

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | VARCHAR(20) PK | Discord user ID |
| `freeToken` | SMALLINT UNSIGNED DEFAULT 500 | Free token balance |
| `plusToken` | SMALLINT UNSIGNED DEFAULT 0 | Premium token balance |
| `paidToken` | INT UNSIGNED DEFAULT 0 | Purchased token balance |
| `usedToken` | INT UNSIGNED DEFAULT 0 | Total tokens used |

#### `aiSituations`

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | VARCHAR(20) PK | Discord user ID |
| `situation` | VARCHAR(4000) | Custom AI situation prompt |
| `name` | VARCHAR(15) | Situation name |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | When created |
| `temperature` | DECIMAL(3,2) DEFAULT 1 | AI temperature setting |
| `top_p` | DECIMAL(3,2) DEFAULT 1 | Top-p sampling value |
| `frequency_penalty` | DECIMAL(3,2) DEFAULT 0 | Frequency penalty |
| `presence_penalty` | DECIMAL(3,2) DEFAULT 0 | Presence penalty |
| `unlocked` | TINYINT(1) DEFAULT 0 | Whether advanced settings are unlocked |

---

### 💬 Communication

#### `scheduledMessages`

| Column | Type | Description |
|--------|------|-------------|
| `messageId` | BIGINT AUTO_INCREMENT PK | Message identifier |
| `guild_id` | VARCHAR(20) | Discord guild ID |
| `channel_id` | VARCHAR(20) | Target channel ID |
| `user_id` | VARCHAR(20) NOT NULL | Creator's user ID |
| `content` | VARCHAR(1024) NOT NULL | Message content |
| `send_time` | DATETIME NOT NULL | When to send the message |
| `repeatInterval` | MEDIUMINT UNSIGNED | Repeat interval in seconds |
| `repeatAmount` | MEDIUMINT UNSIGNED | Number of repeats (null = infinite) |
| `attachments` | TEXT | JSON-serialized attachment URLs |
| `discord_message_id` | VARCHAR(20) | Discord message ID (for deletion) |
| `created_at` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | Creation timestamp |
| **Indexes** | `idx_sendtime`, `idx_user`, `idx_guild`, `idx_discord_message` | |

#### `triggerMessages`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT AUTO_INCREMENT PK | Trigger identifier |
| `guild_id` | VARCHAR(20) | Discord guild ID |
| `trigger` | VARCHAR(128) | Trigger word/phrase |
| `response` | VARCHAR(1024) | Auto-response content |
| `case_sensitive` | TINYINT(1) DEFAULT 0 | Whether matching is case-sensitive |

#### `triggerMessagesChannel`

| Column | Type | Description |
|--------|------|-------------|
| `guild_id` | VARCHAR(20) | Discord guild ID |
| `channel_id` | VARCHAR(20) | Channel scoping |
| `triggerId` | INT | Foreign key to `triggerMessages.id` |
| **PK** | `(guild_id, channel_id, triggerId)` | |
| **FK** | `(guild_id, triggerId)` → `triggerMessages(guild_id, id)` ON DELETE CASCADE | |

---

### 🎫 Tickets

#### `ticketMessages`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT AUTO_INCREMENT PK | Ticket message config ID |
| `guild_id` | VARCHAR(20) | Discord guild ID |
| `channel_id` | VARCHAR(20) | Channel where ticket panel is posted |
| `introduction` | VARCHAR(1024) | Ticket opening message |
| `pingRole` | VARCHAR(20) | Role to ping on new tickets |
| `name` | VARCHAR(128) | Ticket type name |
| `description` | VARCHAR(1024) | Ticket panel description |
| `summaryChannelId` | VARCHAR(20) | Channel for ticket summaries |

#### `tickets`

| Column | Type | Description |
|--------|------|-------------|
| `guild_id` | VARCHAR(20) | Discord guild ID |
| `openerId` | VARCHAR(20) | User who opened the ticket |
| `openedAt` | TIMESTAMP DEFAULT CURRENT_TIMESTAMP | When opened |
| `closed` | TINYINT(1) DEFAULT 0 | Whether closed |
| `closedAt` | TIMESTAMP | When closed |
| `closedBy` | VARCHAR(20) | Who closed the ticket |
| `channel_id` | VARCHAR(20) | Ticket channel ID |
| `ticketMessageId` | INT | FK to `ticketMessages.id` |
| **PK** | `(guild_id, channel_id, ticketMessageId)` | |
| **FK** | `(guild_id, ticketMessageId)` → `ticketMessages(guild_id, id)` ON DELETE CASCADE | |

---

### Additional Tables

| Table | PK | Description |
|-------|----|-------------|
| `welcome_channel` | `(channel_id, guild_id)` | Welcome message channel and template |
| `leave_channel` | `(channel_id, guild_id)` | Leave message channel and template |
| `afk_users` | `user_id` | AFK status storage |
| `afkMessages` | `(user_id, messageId)` | AFK auto-response messages |
| `autopublish` | `channel_id` | Channels with auto-publish enabled |
| `booster_channel` | `(guild_id, channel_id)` | Booster-created voice channels |
| `claimedBoosterChannel` | `(user_id, channel_id)` | Channels claimed by boosters |
| `boosterRole` | `(guild_id, role_id)` | Booster-created roles |
| `claimedBoosterRole` | `(user_id, role_id)` | Roles claimed by boosters |
| `channel_overwrites` | `id AUTO_INCREMENT` | Channel permission overwrites |
| `dynamicslowmode` | `channel_id` | Dynamic slowmode configuration |
| `dynamicslowmode_messages` | `id AUTO_INCREMENT` | Message tracking for dynamic slowmode (FK → `dynamicslowmode`) |
| `join_to_create_channel` | `(guild_id, channel_id)` | Voice channels for join-to-create |
| `mediaChannel` | `channel_id` | Media-only channels |
| `message_tracking_opt_out` | `user_id` | Users who opted out of message tracking |
| `twitchOnlineNotification` | `id AUTO_INCREMENT` | Twitch stream online notifications |
| `brawlstarsLinkedAccounts` | `user_id` | Linked Brawl Stars accounts |
| `feedbackBlocked` | `user_id` | Users blocked from sending feedback |
| `reportchannel` | `(guild_id, channel_id)` | Report submission channels |

---

## Table Relationships

### Foreign Key Relationships

```
triggerMessagesChannel
  └─ (guild_id, triggerId) → triggerMessages(guild_id, id) [CASCADE DELETE]

tickets
  └─ (guild_id, ticketMessageId) → ticketMessages(guild_id, id) [CASCADE DELETE]

dynamicslowmode_messages
  └─ channel_id → dynamicslowmode(channel_id) [CASCADE DELETE]
```

### Logical Relationships (no explicit FK)

```
giveaway
  └─ giveaway_id → giveawayParticipant.giveaway_id
  └─ giveaway_id → giveaway_channelRequirement.giveaway_id
  └─ giveaway_id → giveawayRoleRequirement.giveaway_id
  └─ giveaway_id → giveawayVoiceTime.giveaway_id
  └─ giveaway_id → giveawayNewMessage.giveaway_id
  └─ giveaway_id → giveaway_channelMessages.giveaway_id

welcome_channel
  └─ guild_id → levelConfig.guild_id (shared guild scope)

log_channel
  └─ guild_id → log_enables.guild_id (shared guild scope)
```

---

## Entity-Relationship Diagram (Text)

```
┌─────────────────────────────────────────────┐
│                guild_id                      │
│   (shared across most tables)               │
├─────────────────────────────────────────────┤
│  warnings  warn_config  reports             │
│  level     levelConfig  levelRole           │
│  giveaway  log_enables  log_channel         │
│  tickets   ticketMessages  afk_users        │
│  ... (many more tables)                     │
└─────────────────────────────────────────────┘

┌─────────────┐     ┌──────────────────┐
│ giveaway     │────>│ giveawayParticipant │
│ (giveaway_id)│     │ (giveaway_id)    │
└─────────────┘     └──────────────────┘
       │
       ├────> giveaway_channelRequirement
       ├────> giveawayRoleRequirement
       ├────> giveawayVoiceTime
       ├────> giveawayNewMessage
       └────> giveaway_channelMessages

┌──────────────┐     ┌─────────────────────┐
│ triggerMessages│────>│ triggerMessagesChannel│
│ (id)          │     │ (triggerId)        │
└──────────────┘     └─────────────────────┘

┌────────────────┐     ┌─────────────────────────┐
│ ticketMessages  │────>│ tickets                  │
│ (id)            │     │ (ticketMessageId)       │
└────────────────┘     └─────────────────────────┘

┌─────────────────┐     ┌──────────────────────────┐
│ dynamicslowmode  │────>│ dynamicslowmode_messages  │
│ (channel_id)     │     │ (channel_id)             │
└─────────────────┘     └──────────────────────────┘
```

---

## Notes

- **Discord IDs**: All Discord IDs (users, guilds, channels, roles, messages) are stored as `VARCHAR(20)` with 17-20 digit numeric patterns.
- **Engine**: All tables use `ENGINE=InnoDB` for transaction support and foreign key enforcement.
- **Charset**: Tables default to `utf8mb4` with `utf8mb4_unicode_ci` collation where specified.
- **Indexes**: Frequently queried columns (guild_id, user_id, send_time, channel_id) are indexed for performance.
