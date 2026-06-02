# Monitoring

Tanjun includes built-in monitoring and observability features to help you keep the bot running smoothly.

## Health Checks

The bot exposes a health check endpoint at:

```
http://localhost:8080/health
```

This endpoint returns a JSON response with the status of various subsystems:

```json
{
  "status": "healthy",
  "uptime": 123456,
  "database": "connected",
  "discord": "connected",
  "version": "1.2.0",
  "checks": {
    "database": { "status": "ok", "latency_ms": 12 },
    "discord_gateway": { "status": "ok", "latency_ms": 85 },
    "openai": { "status": "ok" },
    "twitch": { "status": "ok" }
  }
}
```

### Custom Health Checks

The health check system is extensible. Custom checks are defined in the `health/` directory:

```python
class MyHealthCheck(HealthCheck):
    name = "my_service"
    
    async def check(self) -> HealthCheckResult:
        # Perform your check
        return HealthCheckResult(status=Status.OK, latency_ms=42)
```

## Prometheus Metrics

When enabled, Tanjun exposes Prometheus metrics at:

```
http://localhost:8080/metrics
```

### Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `commands_total` | Counter | Total commands executed |
| `commands_errors_total` | Counter | Total command errors |
| `messages_processed_total` | Counter | Total messages processed |
| `guild_count` | Gauge | Number of guilds the bot is in |
| `shard_count` | Gauge | Number of shards |
| `http_latency_seconds` | Histogram | Discord API latency |
| `database_pool_size` | Gauge | Database connection pool size |

### Grafana Dashboard

A pre-configured Grafana dashboard is available in the `grafana/` directory. Import it into your Grafana instance to get started quickly.

## Status Page (Uptime Kuma)

The bot's operational status is tracked at [status.tanjun.bot](https://status.tanjun.bot). Users can subscribe to incident notifications on that page (configured in Uptime Kuma, not in the bot).

### Uptime Kuma setup

1. In Uptime Kuma, create or edit a **Push** monitor for Tanjun (not HTTP polling).
2. Set the heartbeat interval to **60–90 seconds** (the bot pushes every 60 seconds).
3. Copy the push token from the monitor URL (`/api/push/<token>`).
4. Set `UPTIME_KUMA_PUSH_TOKEN` in the bot `.env`. Optionally override `UPTIME_KUMA_STATUS_URL` if the status page host differs.
5. In Uptime Kuma **Settings → Notifications**, configure Discord/email and send a test notification.

The bot sends a lightweight `GET` to `/api/push/<token>?status=up&msg=OK&ping=<latency_ms>` when the token is set. If `UPTIME_KUMA_PUSH_TOKEN` is empty, no push requests are made (useful for local dev).

The legacy `botstatus-api.tanjun.bot` relay is no longer used.

## Discord Alerts

- **Status page subscribers:** Uptime Kuma notification providers on [status.tanjun.bot](https://status.tanjun.bot).
- **Internal health failures:** set `HEALTH_ALERT_CHANNEL_ID` and `HEALTH_ALERT_USER_ID` so startup/periodic health check failures post to a Discord channel.

You can also monitor the bot `/health` endpoint from an external service if needed.
