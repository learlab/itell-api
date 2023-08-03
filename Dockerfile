FROM nvcr.io/nvidia/pytorch:23.07-py3

# Do requirements first so we can cache them
# This layer only changes when requirements are updated.
COPY requirements.txt /usr/src/

WORKDIR /usr/src/

RUN python3 -m pip install -r requirements.txt

COPY . /usr/src/


# Installing as root seems to confuse these libraries
# Specify where we want them to cache downloads
RUN mkdir /usr/local/nltk_data

ENV HF_HOME=/usr/local/huggingface \
    NLTK_DATA=/usr/local/nltk_data

# download big models so they are stored in container
RUN python3 ./download_models.py

CMD ["python3", "src/main.py"]
