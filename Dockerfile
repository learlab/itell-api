FROM python:3.10

WORKDIR /code

# Copy and install requirements first
# requirements.txt changes less frequently than /src
# so this layer can be cached
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Installing as root seems to confuse these libraries
# Specify where we want them to cache downloads
RUN mkdir /usr/local/nltk_data

ENV HF_HOME=/usr/local/huggingface \
    NLTK_DATA=/usr/local/nltk_data

    
# /code changes more often, so copy this last.
COPY . /code

# download big models so they are stored in container
RUN python /code/download_models.py

ENV PYTHONPATH=$PYTHONPATH:/code

CMD ["python", "src/main.py"]
