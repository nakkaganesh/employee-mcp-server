FROM python:3.14-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files first for better Docker caching
COPY pyproject.toml uv.lock README.md ./

# Copy package source because uv_build expects it
COPY src ./src

# Install locked dependencies
RUN uv sync --locked --no-dev

# Copy application code
COPY client.py server.py database.py ./

CMD ["uv", "run", "client.py"]