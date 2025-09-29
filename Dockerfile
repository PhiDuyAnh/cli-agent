FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    TERM=xterm-256color \
    PIXELTABLE_HOME=/root/.pixeltable

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
WORKDIR /app
RUN uv sync --frozen --no-cache

CMD ["/app/.venv/bin/python", "src/cli_agent/cli.py"]