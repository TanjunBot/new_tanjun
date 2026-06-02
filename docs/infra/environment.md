# Environment Variables

Tanjun is configured through environment variables defined in a `.env` file. This page documents all available variables.

## Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `token` | Discord bot token | `MTIzNDU2Nzg5...` |
| `applicationId` | Discord application ID | `123456789012345678` |
| `adminIds` | Comma-separated list of admin user IDs | `123456789,987654321` |
| `database_ip` | MySQL/MariaDB hostname | `localhost` or `db` |
| `database_port` | Database port (default: 3306) | `3306` |
| `database_user` | Database username | `tanjun` |
| `database_password` | Database password | `your_secure_password` |
| `database_schema` | Database name | `tanjun` |

> **Important:** Never commit the `.env` file to version control. The `.env.example` file is a template without real secrets.

## Optional Variables

### AI / OpenAI

| Variable | Description |
|----------|-------------|
| `openai_api_key` | OpenAI API key for AI chat features |
| `openai_tokens` | Daily token limit per user (default: `10000`) |
| `openai_situation` | Default situation prompt for AI |

### External APIs

| Variable | Description |
|----------|-------------|
| `giphy_api_key` | Giphy API key for GIF commands |
| `imgbb_api_key` | ImgBB API key for image uploads |
| `github_token` | GitHub personal access token |
| `bytebin_url` | Bytebin instance URL |
| `twitch_client_id` | Twitch API client ID |
| `twitch_client_secret` | Twitch API client secret |

### Logging & Monitoring

| Variable | Description |
|----------|-------------|
| `log_level` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `prometheus_port` | Port for Prometheus metrics endpoint (default: `9090`) |
| `healthcheck_port` | Port for health check endpoint (default: `8080`) |
| `sentry_dsn` | Sentry DSN for error tracking |
| `UPTIME_KUMA_PUSH_TOKEN` | Uptime Kuma push monitor token (optional; omit to disable heartbeats) |
| `UPTIME_KUMA_STATUS_URL` | Uptime Kuma base URL (default: `https://status.tanjun.bot`) |
| `HEALTH_ALERT_CHANNEL_ID` | Discord channel ID for internal health-check failure alerts |
| `HEALTH_ALERT_USER_ID` | Discord user ID to ping with health-check failure alerts |

### Bot Behavior

| Variable | Description | Default |
|----------|-------------|---------|
| `default_prefix` | Legacy command prefix | `t!` |
| `default_language` | Default locale | `en` |
| `activity_type` | Bot status activity type | `playing` |
| `activity_text` | Bot status activity text | `Tanjun v1.2` |
| `shard_count` | Number of shards for large bots | `1` |
| `shard_ids` | Comma-separated shard IDs | (auto) |

### Database

| Variable | Description | Default |
|----------|-------------|---------|
| `database_pool_size` | Connection pool size | `10` |
| `database_pool_recycle` | Connection recycle time (seconds) | `3600` |
| `database_echo` | Log SQL queries (debug) | `False` |

## Example

```ini
# Required
token=MTIzNDU2Nzg5...
applicationId=123456789012345678
adminIds=123456789,987654321
database_ip=localhost
database_port=3306
database_user=tanjun
database_password=secret
database_schema=tanjun

# Optional: AI
openai_api_key=sk-...
openai_tokens=10000

# Optional: Monitoring
log_level=INFO
prometheus_port=9090
healthcheck_port=8080
UPTIME_KUMA_PUSH_TOKEN=your_push_token_from_uptime_kuma
# UPTIME_KUMA_STATUS_URL=https://status.tanjun.bot
```

> See [.env.example](https://github.com/TanjunBot/new_tanjun/blob/development/.env.example) in the repository for the latest template.
