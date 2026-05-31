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

USER appuser

# Health check for container orchestration (Discord ready can take 2+ minutes on cold start)
HEALTHCHECK --interval=30s --timeout=10s --start-period=180s --retries=5 \
  CMD ["python", "/usr/local/app/healthcheck.py"]

EXPOSE 8001
CMD ["python", "main.py"]