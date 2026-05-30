# Deployment

This guide covers deploying Tanjun in a production environment.

## Docker Deployment (Recommended)

### Prerequisites

- Docker and Docker Compose
- MySQL or MariaDB server (or use the database service in the compose file)
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

4. Verify the bot is running:

   ```bash
   docker compose logs -f
   ```

### Production Considerations

#### Environment Variables

See [Environment Variables](./environment.md) for the full list.

#### Database

For production, use a managed MySQL/MariaDB instance:

```yaml
# compose.yaml excerpt
services:
  db:
    image: mariadb:11
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${database_schema}
    volumes:
      - db_data:/var/lib/mysql
    restart: unless-stopped
```

Configure your `.env`:

```ini
database_ip=db
database_port=3306
database_user=root
database_password=your_secure_password
database_schema=tanjun
```

#### Health Checks

The bot includes built-in health checks accessible at:

```
http://localhost:8080/health
```

Configure monitoring to check this endpoint regularly.

## Manual Deployment

1. Set up a Python 3.12 environment:

   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -e ".[dev]"
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
pip install -e ".[dev]"
# Restart the bot
```

> **Important:** Always check the [CHANGELOG.md](https://github.com/TanjunBot/new_tanjun/blob/development/CHANGELOG.md) before updating for any breaking changes or migration steps.
