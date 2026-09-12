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

| Variable | Description | Default |
|----------|-------------|---------|
| `log_level` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |
| `METRICS_PORT` | Port for Prometheus metrics and `/health` endpoint | `8001` |
| `sentry_dsn` | Sentry DSN for error tracking | (empty) |
| `UPTIME_KUMA_PUSH_TOKEN` | Uptime Kuma push monitor token (omit to disable heartbeats) | (empty) |
| `UPTIME_KUMA_STATUS_URL` | Uptime Kuma base URL | `https://status.tanjun.bot` |
| `HEALTH_ALERT_CHANNEL_ID` | Discord channel ID for internal health-check failure alerts | (unset) |
| `HEALTH_ALERT_USER_ID` | Discord user ID to ping with health-check failure alerts | (unset) |

### Bot Behavior

| Variable | Description | Default |
|----------|-------------|---------|
| `prefix` | Legacy command prefix | (required) |
| `activity` | Bot status/activity template | `Tanjun {version}` |
| `SYNC_COMMANDS_ON_STARTUP` | Synchronize application commands at startup | `true` |
| `ACTIVITY_SERVER_PORT` | Discord Activities server port | `8080` |
| `ACTIVITY_SERVER_HOST` | Discord Activities bind host | `0.0.0.0` |
| `ACTIVITY_PUBLIC_URL` | Public Discord Activities URL | `https://activity.entcheneric.com` |

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
METRICS_PORT=8001
UPTIME_KUMA_PUSH_TOKEN=your_push_token_from_uptime_kuma
# UPTIME_KUMA_STATUS_URL=https://status.tanjun.bot
```

> See [.env.example](https://github.com/TanjunBot/new_tanjun/blob/development/.env.example) in the repository for the latest template.

The bundled `botstatus-api` service has separate settings documented in
[`botstatus-api/README.md`](../../botstatus-api/README.md). Its
`BOTSTATUS_API_KEY` is required when that service is deployed and must match
the bearer token sent by the bot via `BOTSTATUS_API_TOKEN`.
