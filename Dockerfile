# FROM nvcr.io/nvidia/pytorch:22.12-py3
FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
        git \
        python3 \
        python3-pip

# Do requirements first so we can cache them
# This layer only changes when requirements are updated.
COPY requirements.txt /usr/src/

WORKDIR /usr/src/

RUN pip install -r requirements.txt

COPY download_models.py /usr/src/

# Installing as root seems to confuse these libraries
# Specify where we want them to cache downloads
RUN mkdir /usr/local/nltk_data

ENV HF_HOME=/usr/local/huggingface \
    NLTK_DATA=/usr/local/nltk_data

# download big models with Docker cache
RUN \
    --mount=type=cache,target=/usr/local/huggingface \
    python3 ./download_models.py

COPY . /usr/src/

CMD ["python3", "-m", "src.main"]
