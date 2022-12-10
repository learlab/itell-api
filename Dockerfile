FROM python:3.10

WORKDIR /code

# Copy and install requirements first
# requirements.txt changes less frequently than /src
# so we may be able to cache this layer more often
# if we install requirements first
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Installing as root seems to confuse these libraries
# Specify where we want them to cache downloads
ENV HF_HOME=/usr/local/huggingface \
    NLTK_DATA=/usr/local/nltk_data
COPY ./download_models.py /code/download_models.py
RUN python /code/download_models.py

# /code changes often, so copy this last.
COPY ./src /code/src
ENV PYTHONPATH=$PYTHONPATH:/code

CMD ["python", "src/main.py"]
