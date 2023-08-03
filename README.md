# API for Textbook Summaries

This repository defines the api for our digital textbook project.

Currently, it scores section summaries using a finetuned language model.

## Development

1. Clone the repository and run `pipenv install` to install requirements from the pipfile.
2. Run `python .\download_models.py` to download required models from SpaCy and Huggingface.

## Deployment

The code defines a Docker image. Anytime a change is committed to `main`, Github Actions will issue a build command to Google Cloud. After the build is manually approved from the Google Cloud platform, it will automatically build AND deploy to Google Cloud Run.

## Usage

The API request is a POST request to the `/score` endpoint. The request body should be a JSON object with fields defined in /models/summary.py.

The response is a JSON object with fields defined in /models/summary.py
