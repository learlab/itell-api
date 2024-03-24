FROM nvidia/cuda:12.1.1-devel-ubuntu22.04 as base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        protobuf-compiler \
        libprotobuf-dev

# Do requirements first so we can cache them
RUN mkdir /usr/src/itell-ai && \
    mkdir /usr/src/itell-ai/assets && \
    mkdir /usr/src/itell-ai/src && \
    mkdir /usr/src/itell-ai/templates
WORKDIR /usr/src/itell-ai
COPY requirements/gpu.txt /usr/src/itell-ai/requirements.txt
RUN pip install -r requirements.txt

ENV HF_HOME=/usr/local/huggingface

COPY assets /usr/src/itell-ai/assets/
COPY src /usr/src/itell-ai/src/
COPY templates /usr/src/itell-ai/templates/

CMD ["python3", "-m", "src.main"]

FROM base as test
COPY pyproject.toml /usr/src/itell-ai/
RUN mkdir /usr/src/itell-ai/tests

COPY tests /usr/src/itell-ai/tests/
RUN pip install pytest
CMD ["pytest", "-s"]
