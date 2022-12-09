FROM python:3.10

WORKDIR /code
COPY . /code
RUN pip install -r ./requirements.txt
RUN python ./download_models.py
RUN export PYTHONPATH=$PYTHONPATH:/code
CMD ["python", "src/main.py"]
