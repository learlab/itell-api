FROM python:3.10

WORKDIR /code
COPY . /code
ENV PYTHONPATH=$PYTHONPATH:/code
RUN pip install -r ./requirements.txt
ENV HF_HOME=/usr/local/huggingface
RUN python ./download_models.py
CMD ["python", "src/main.py"]
