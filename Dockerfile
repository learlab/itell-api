FROM nvidia/cuda:12.6.0-devel-ubuntu24.04 as base
ENV DEBIAN_FRONTEND=noninteractive
ENV HF_HOME=/usr/local/huggingface
ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
ARG MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    wget

# Install Miniconda for FAISS installation
RUN wget $MINICONDA_URL -O miniconda.sh && \
    mkdir -p /root/.conda && \
    bash miniconda.sh -b -p /opt/miniconda3 && \
    rm -f miniconda.sh && \
    conda init bash

# Protobuf required by gcld3
RUN conda install -c conda-forge protobuf
RUN conda install --yes -c pytorch -c nvidia faiss-gpu=1.8.0

# Do requirements first so we can cache them
RUN mkdir /usr/src/itell-ai && \
    mkdir /usr/src/itell-ai/assets && \
    mkdir /usr/src/itell-ai/src && \
    mkdir /usr/src/itell-ai/templates
WORKDIR /usr/src/itell-ai

COPY requirements/requirements.txt /usr/src/itell-ai/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy freqently changed files last to avoid cache busting
COPY assets /usr/src/itell-ai/assets/
COPY src /usr/src/itell-ai/src/
COPY templates /usr/src/itell-ai/templates/

CMD ["python", "-m", "src.app"]

FROM base as test

COPY pyproject.toml /usr/src/itell-ai/
RUN mkdir /usr/src/itell-ai/tests
COPY tests /usr/src/itell-ai/tests/
RUN pip install pytest asgi-lifespan
CMD ITELL_AI_LOG_TO_DB=FALSE pytest -s
