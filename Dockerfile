FROM python:3.12

WORKDIR /usr/local/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    default-mysql-client && \
    rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m appuser && \
    mkdir -p /usr/local/app && \
    chown appuser:appuser /usr/local/app

# Install Python dependencies
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy the entire application
COPY --chown=appuser:appuser . /usr/local/app/

RUN chmod +x /usr/local/app/scripts/docker_entrypoint.py

USER appuser

ENV PYTHONPATH=/usr/local/app
ENV TANJUN_APP_ROOT=/usr/local/app

# Health check: .bot_startup during migrations/boot, .bot_ready when Discord is up
HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=10 \
  CMD ["python", "/usr/local/app/healthcheck.py"]

EXPOSE 8001
ENTRYPOINT ["python", "/usr/local/app/scripts/docker_entrypoint.py"]
CMD []