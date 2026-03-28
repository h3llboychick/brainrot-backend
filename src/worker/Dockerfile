FROM python:3.11-alpine

RUN apk add --no-cache \
    build-base \
    linux-headers \
    python3-dev \
    postgresql-dev \
    libffi-dev \
    freetype-dev \
    fontconfig \
    ttf-dejavu \
    imagemagick \
    ffmpeg

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /deps
COPY requirements.txt /deps/requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install -r /deps/requirements.txt

RUN fc-cache -f -v && fc-list | grep -i "proxima" || true

WORKDIR /app
ENV PYTHONPATH=/app
