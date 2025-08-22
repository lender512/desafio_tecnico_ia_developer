FROM python:3.11-slim

# Install dependencies for PDF generation
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libharfbuzz0b \
    libfreetype6 \
    fontconfig \
    libgdk-pixbuf-2.0-0 \
    fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set work directory
WORKDIR /app

# Copy uv configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# Copy application code
COPY app/ ./app/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (using ARG to allow build-time customization)
ARG PORT=8000
EXPOSE $PORT

# Run the application using uv with environment variables
CMD ["sh", "-c", "uv run uvicorn app.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-8000}"]
