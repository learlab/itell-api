FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip

# Do requirements first so we can cache them
# This layer only changes when requirements are updated.
COPY gpu-requirements.txt /usr/src/

WORKDIR /usr/src/

RUN pip install -r gpu-requirements.txt

# Specify where we want nltk and hf to cache downloads
RUN mkdir /usr/local/nltk_data

ENV HF_HOME=/usr/local/huggingface \
    NLTK_DATA=/usr/local/nltk_data

COPY . /usr/src/

CMD ["python3", "-m", "src.main"]
