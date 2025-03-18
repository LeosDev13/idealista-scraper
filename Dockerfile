FROM python:3.13-slim AS Builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ADD . /app

RUN uv sync --frozen

CMD ["uv", "run", "main.py"]

