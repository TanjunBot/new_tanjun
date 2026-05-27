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
USER appuser

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . /usr/local/app/

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD ["python", "/usr/local/app/healthcheck.py"]

EXPOSE 8080
CMD ["python", "main.py"]