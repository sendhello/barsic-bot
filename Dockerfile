FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# pip
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100
# Poetry no venv
ENV POETRY_VIRTUALENVS_CREATE=false
# do not ask any interactive question
ENV POETRY_NO_INTERACTION=1

ENV DEBIAN_FRONTEND=noninteractive
ENV APP_PATH="/opt/app"

WORKDIR $APP_PATH

# RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev

COPY poetry.lock pyproject.toml ./
RUN pip install poetry && poetry install
COPY . .

ENTRYPOINT sh barsic_bot.sh
