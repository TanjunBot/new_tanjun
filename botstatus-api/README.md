# Tanjun Botstatus API

A lightweight, high-performance microservice to ingest heartbeat pings from Tanjun Bot and expose real-time status, health, Prometheus metrics, and Shields.io badges.

Deployed at `https://botstatus-api.tanjun.bot`.

---

## Features

- **Heartbeat Ingest (`POST /` & `POST /api/status` & `POST /status`):** Accepts `{ "id": "...", "status": "alive", "latency": "0.042" }`.
- **Status Dashboard API (`GET /` & `GET /status`):** Returns online/offline status, latency in ms, uptime, and last ping time.
- **Bot Details (`GET /status/{bot_id}`):** Query status for a specific bot instance.
- **Health Check (`GET /health` & `GET /livez` & `GET /readyz`):** Liveness endpoint for Docker, Coolify, Traefik, or Uptime Kuma.
- **Shields.io Badge API (`GET /badge`):** Returns dynamic JSON for Shields.io endpoint badges (`online (35ms)` / `offline`).
- **Prometheus Exporter (`GET /metrics`):** Exposes `bot_online`, `bot_latency_ms`, and `bot_seconds_since_last_ping`.
- **Uptime Kuma Forwarding:** Optionally forward heartbeats to an Uptime Kuma push monitor URL.
- **State Persistence:** Automatically preserves bot states across container restarts in `data/state.json`.

---

## Configuration (Environment Variables)

| Variable | Default | Description |
|---|---|---|
| `BOTSTATUS_HOST` | `0.0.0.0` | Bind host |
| `BOTSTATUS_PORT` | `8000` | Bind port |
| `BOTSTATUS_TIMEOUT_SECONDS` | `90` | Time after which a missing ping marks the bot as offline |
| `BOTSTATUS_DEFAULT_BOT_ID` | `832297321793323028` | Primary bot ID |
| `BOTSTATUS_API_KEY` | *(empty)* | Optional secret key for POST authentication (`Bearer <key>`) |
| `BOTSTATUS_STATE_FILE` | `data/state.json` | Path to persistent state file |
| `BOTSTATUS_UPTIME_KUMA_PUSH_URL` | *(empty)* | Optional Uptime Kuma push monitor URL to bridge heartbeats |

---

## Deployment with Docker / Coolify

### 1. Standalone Docker Run
```bash
docker build -t botstatus-api ./botstatus-api
docker run -d \
  --name botstatus-api \
  -p 8000:8000 \
  -v botstatus-data:/app/data \
  --restart unless-stopped \
  botstatus-api
```

### 2. Docker Compose
```bash
docker compose -f botstatus-api/docker-compose.yml up -d
```

### 3. In Coolify
1. Create a new service from the Git repository with Dockerfile path `botstatus-api/Dockerfile` (or build context `botstatus-api`).
2. Set Port to `8000`.
3. Set Domain to `https://botstatus-api.tanjun.bot`.

---

## API Reference

### Ingest Heartbeat
`POST /api/status` or `POST /`
```json
{
  "id": "832297321793323028",
  "status": "alive",
  "latency": 0.035,
  "guild_count": 150
}
```

### Query Status
`GET /status` or `GET /`
```json
{
  "status": "online",
  "primary_bot": {
    "id": "832297321793323028",
    "status": "online",
    "latency_ms": 35,
    "guild_count": 150,
    "last_ping": "2026-09-01T08:15:30.123456+00:00",
    "seconds_since_last_ping": 5
  },
  "bots": [...],
  "total_bots": 1,
  "online_bots": 1
}
```
