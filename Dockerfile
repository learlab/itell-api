FROM nvcr.io/nvidia/pytorch:23.07-py3

# Copy pipfile and pipfile.lock
COPY . /usr/src/

WORKDIR /usr/src/

RUN python3 -m pip install -r requirements.txt

# Installing as root seems to confuse these libraries
# Specify where we want them to cache downloads
RUN mkdir /usr/local/nltk_data

ENV HF_HOME=/usr/local/huggingface \
    NLTK_DATA=/usr/local/nltk_data

# download big models so they are stored in container
RUN python3 ./download_models.py

# EXPOSE 8001

CMD ["python3", "src/main.py"]
