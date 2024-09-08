FROM nvidia/cuda:12.6.0-devel-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV HF_HOME=/usr/local/huggingface
ENV PATH="/opt/miniconda3/bin:${PATH}"
ARG PATH="/opt/miniconda3/bin:${PATH}"
ARG MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"

RUN apt-get update \
    && apt-get install --no-install-recommends --assume-yes \
    # protobuf-compiler \
    # libprotobuf-dev \
    wget

# Install Miniconda on x86 or ARM platforms
RUN wget $MINICONDA_URL -O miniconda.sh && \
    mkdir -p /root/.conda && \
    bash miniconda.sh -b -p /opt/miniconda3 && \
    rm -f miniconda.sh && \
    conda init bash

COPY requirements/requirements.in /tmp/requirements.txt
RUN conda install -c conda-forge protobuf
RUN conda install --name base --yes -c pytorch -c nvidia faiss-gpu=1.8.0
RUN pip install --no-cache-dir -r /tmp/requirements.txt