FROM python:3.12

WORKDIR /usr/local/app

LABEL org.opencontainers.image.source="https://github.com/TanjunBot/new_tanjun" \
      org.opencontainers.image.authors="TanjunBot Team" \
      org.opencontainers.image.description="Tanjun is our versatile, customizable and multifunctional bot — fully available in multiple languages!"

# System requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Install system requirements
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install application requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire source code
COPY --chown=appuser:appuser . /usr/local/app/

RUN useradd -m appuser
USER appuser

EXPOSE 8080
CMD ["python", "main.py"]
