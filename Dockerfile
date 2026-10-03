FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first for Docker layer caching
COPY pyproject.toml uv.lock README.md ./

# Copy package source required by uv_build
COPY src ./src

# Install production dependencies
RUN uv sync --locked --no-dev

# Copy backend application files
COPY client.py server.py database.py web_app.py ./

# Copy frontend
COPY static ./static

# Default command for production web deployment
CMD ["sh", "-c", "uv run uvicorn web_app:app --host 0.0.0.0 --port ${PORT:-8000}"]