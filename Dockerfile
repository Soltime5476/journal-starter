FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/
ENV PYTHONPATH="/app"

RUN groupadd -r app && useradd -r -g app app
WORKDIR "/home/app"
RUN chown app:app /home/app
COPY . /home/app
RUN uv sync

# need additional config to run with database locally
USER app
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
