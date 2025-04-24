FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY uv.lock .
COPY pyproject.toml .

# Install dependencies using pip
RUN uv sync --locked

# Copy the rest of the application
COPY . .

# Run the application
CMD ["uv", "run", "app.py"] 