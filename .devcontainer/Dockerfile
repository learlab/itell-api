FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install --no-install-recommends --assume-yes \
    protobuf-compiler \
    libprotobuf-dev

# Specify where we want hf to cache downloads
ENV HF_HOME=/usr/local/huggingface

COPY requirements/requirements.in /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt