FROM python:3.10

WORKDIR /code
COPY . /code
ENV PYTHONPATH=$PYTHONPATH:/code \
    HOME="/home"
RUN pip install -r ./requirements.txt
RUN python ./download_models.py
CMD ["python", "src/main.py"]
