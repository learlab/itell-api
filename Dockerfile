FROM nvidia/cuda:12.1.1-devel-ubuntu22.04 as base
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip

# Do requirements first so we can cache them
COPY requirements/gpu.txt /usr/src/requirements/
WORKDIR /usr/src/
RUN pip install -r requirements/gpu.txt

RUN mkdir /usr/local/nltk_data
ENV HF_HOME=/usr/local/huggingface \
    NLTK_DATA=/usr/local/nltk_data

COPY assets src /usr/src/
CMD ["python3", "-m", "src.main"]

FROM base as test
COPY tests pyproject.toml /usr/src/
RUN pip install pytest
CMD ["pytest"]
