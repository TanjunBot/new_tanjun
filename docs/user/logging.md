# Logging

Tanjun provides comprehensive event logging to help you keep track of what's happening in your server.

## Setting Up Logging

### Log Channels

Designate channels for different types of logs:

```
/logging config modlog #channel-name
/logging config joinlog #channel-name
/logging config leavelog #channel-name
/logging config messagelog #channel-name
/logging config voicelog #channel-name
```

Use the same command without a channel to disable that log type.

### Available Log Types

| Log Type | Events Tracked |
|----------|----------------|
| **modlog** | Bans, kicks, timeouts, warns, message purges |
| **joinlog** | Member joins, including account age |
| **leavelog** | Member leaves, including role count |
| **messagelog** | Message edits and deletions |
| **voicelog** | Voice channel joins, leaves, moves |

## Log Blacklisting

Prevent specific channels or roles from being logged:

```
/logging blacklist channel add #channel
/logging blacklist channel remove #channel
/logging blacklist role add @role
/logging blacklist role remove @role
```

Blacklisted items are excluded from message and voice logs.

## Log Format

Each log entry includes:
- **Timestamp** — When the event occurred
- **User** — Who triggered the event (with mention and ID)
- **Details** — Context-specific information
- **Channel** — Where it happened (where applicable)

> **Tip:** Use separate channels for different log types to keep things organized. A single modlog channel is sufficient for most servers.
