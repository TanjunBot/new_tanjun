# Deployment

This guide covers deploying Tanjun in a production environment.

## Docker Deployment (Recommended)

### Prerequisites

- Docker and Docker Compose
- MySQL or MariaDB server (the production Compose file does not provision a database)
- Discord Bot Token and Application ID

### Quick Start

1. Clone the repository:

   ```bash
   git clone https://github.com/TanjunBot/new_tanjun.git
   cd new_tanjun
   ```

2. Configure environment variables:

   ```bash
   cp .env.example .env
   # Edit .env with your production values
   ```

3. Start the bot:

   ```bash
   docker compose up -d
   ```

   On container start, the entrypoint waits for the database, synchronizes schema via Alembic (`upgrade head` when needed, or `stamp head` when the database already matches the code but was never tracked), then starts `main.py`. You do not need to run migrations manually for normal Docker deploys.

4. Verify the bot is running:

   ```bash
   docker compose logs -f
   ```

### Production Considerations

#### Environment Variables

See [Environment Variables](./environment.md) for the full list.

#### Database

Use a managed MySQL/MariaDB instance, or provide a separately managed database
service. The bot container connects to the host named by `database_ip`; the
Compose file only runs the bot and the optional botstatus API.

Configure your `.env` (use the database service's internal hostname when
running in a platform such as Coolify):

```ini
database_ip=db
database_port=3306
database_user=root
database_password=your_secure_password
database_schema=tanjun
```

#### Health Checks

The Docker healthcheck uses `http://127.0.0.1:8001/health` (the metrics
server). Configure external monitoring against that endpoint when port 8001 is
exposed; port 8080 is used by the Discord Activities server when enabled.

## Manual Deployment

1. Set up a Python 3.12 environment:

   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

2. Run with a process manager like `systemd` or `supervisor`:

   ```bash
   python main.py
   ```

### systemd Service Example

```ini
[Unit]
Description=Tanjun Discord Bot
After=network.target mysql.service

[Service]
Type=simple
User=tanjun
WorkingDirectory=/opt/tanjun
ExecStart=/opt/tanjun/venv/bin/python main.py
Restart=on-failure
RestartSec=10
EnvironmentFile=/opt/tanjun/.env

[Install]
WantedBy=multi-user.target
```

## Updating

### Docker

```bash
docker compose down
git pull
docker compose up -d --build
```

### Manual

```bash
git pull
source venv/bin/activate
pip install -e .
# Restart the bot
```

> **Important:** Always check the [CHANGELOG.md](https://github.com/TanjunBot/new_tanjun/blob/development/CHANGELOG.md) before updating for any breaking changes or migration steps.
