FROM python:3.10

WORKDIR /code
COPY . /code
RUN pip install -r ./src/requirements.txt
RUN python -c "import nltk; nltk.download('punkt')"
RUN export PYTHONPATH=$PYTHONPATH:/code
CMD ["python", "main.py"]
