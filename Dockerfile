FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install harness CLI
RUN pip install --no-cache-dir -e . 2>/dev/null || true

# Default command
CMD ["harness", "scan", ".", "--help"]
