FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (includes Cairo/Pango/GObject for WeasyPrint)
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
        ca-certificates \
        # WeasyPrint runtime
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        libffi-dev \
        shared-mime-info \
        fonts-noto-core \
        fonts-noto-cjk \
        fonts-indic \
        fonts-noto-extra \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package installation
RUN pip install --no-cache-dir uv

# Copy project metadata
COPY pyproject.toml ./

# Install Python dependencies (including dev for development image)
RUN uv pip install --system --no-cache -e ".[dev]"

# Copy application code (will be overridden by volume mount in dev)
COPY . .

# Run as non-root for security
RUN useradd --create-home --shell /bin/bash --uid 1001 app \
    && chown -R app:app /app
USER app

# Expose FastAPI port
EXPOSE 8000

# Healthcheck used by docker-compose / orchestrators
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

# Default command (overridden by docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
