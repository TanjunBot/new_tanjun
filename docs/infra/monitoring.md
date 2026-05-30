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

## Status Page

The bot's operational status is tracked at [status.tanjun.bot](https://status.tanjun.bot). You can subscribe to updates there.

## Discord Alerts

Configure alerting by monitoring the health endpoint from your preferred monitoring service (e.g., Uptime Robot, Better Uptime, Grafana OnCall).

> **Tip:** Set up a dedicated Discord channel for bot health alerts so the team gets notified if something goes wrong.
