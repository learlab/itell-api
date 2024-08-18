FROM nvidia/cuda:12.6.0-devel-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --no-install-recommends --assume-yes \
    protobuf-compiler \
    libprotobuf-dev \
    python3-venv

# Specify where we want hf to cache downloads
ENV HF_HOME=/usr/local/huggingface

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip \
    && pip install --no-cache-dir \
    pytest \
    asgi-lifespan

COPY requirements/requirements.in /tmp/requirements.txt