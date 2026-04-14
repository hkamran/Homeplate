FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

RUN useradd --create-home appuser
USER appuser

EXPOSE 5000

CMD ["uv", "run", "flask", "run", "--host=0.0.0.0", "--port=5000"]
