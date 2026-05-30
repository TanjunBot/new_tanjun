# Giveaways

Tanjun's giveaway system lets you create and manage giveaways directly from Discord.

## Creating a Giveaway

Use the `/giveaway create` command to start a new giveaway:

```
/giveaway create prize:"Nitro Classic" winners:1 duration:2h channel:#giveaways
```

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `prize` | The name of the prize | Required |
| `winners` | Number of winners to draw | 1 |
| `duration` | How long the giveaway runs (e.g., `2h`, `30m`, `7d`) | 24h |
| `channel` | Channel to post the giveaway in | Current channel |

## Giveaway Requirements

You can add entry requirements:

| Requirement | Description |
|-------------|-------------|
| **Role** | Members must have a specific role |
| **Level** | Members must be at least a certain level |
| **Account Age** | Discord account must be at least X days old |
| **Server Age** | Member must have been in the server for X days |

## Managing Giveaways

### End Early

Stop a giveaway and draw winners immediately:

```
/giveaway end <giveaway_id>
```

### Reroll Winners

If a winner didn't claim their prize:

```
/giveaway reroll <giveaway_id>
```

### Cancel

Cancel an active giveaway without drawing winners:

```
/giveaway cancel <giveaway_id>
```

### List Active Giveaways

View all running giveaways on the server:

```
/giveaway list
```

## Blacklist

Prevent specific roles or members from entering giveaways:

```
/giveaway blacklist add @role
/giveaway blacklist remove @role
/giveaway blacklist list
```

> **Note:** Giveaway entries are tracked per user. Each user can only enter once per giveaway regardless of how many times they click the enter button.
