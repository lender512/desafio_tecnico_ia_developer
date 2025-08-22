FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set work directory
WORKDIR /app

# Copy uv configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# Copy application code
COPY app.py ./
COPY src/ ./src/
COPY assets/ ./assets/

# Copy environment variables
COPY .env ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (using ARG to allow build-time customization)
ARG STREAMLIT_SERVER_PORT=8501
EXPOSE $STREAMLIT_SERVER_PORT

# Run the application using uv with environment variables
CMD ["sh", "-c", "uv run streamlit run app.py --server.port=${STREAMLIT_SERVER_PORT:-8501} --server.address=${STREAMLIT_SERVER_ADDRESS:-0.0.0.0} --server.headless=${STREAMLIT_SERVER_HEADLESS:-true} --browser.gatherUsageStats=${STREAMLIT_BROWSER_GATHER_USAGE_STATS:-false}"]
