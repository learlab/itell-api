FROM nvidia/cuda:12.6.0-devel-ubuntu24.04 as base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    protobuf-compiler \
    libprotobuf-dev

# Do requirements first so we can cache them
RUN mkdir /usr/src/itell-ai && \
    mkdir /usr/src/itell-ai/assets && \
    mkdir /usr/src/itell-ai/src && \
    mkdir /usr/src/itell-ai/templates
WORKDIR /usr/src/itell-ai
COPY requirements/requirements.txt /usr/src/itell-ai/requirements.txt

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

ENV HF_HOME=/usr/local/huggingface

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
