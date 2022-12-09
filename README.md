# API for Textbook Summaries

This repository defines the api for our digital textbook project.

Currently, it scores section summaries using a finetuned language model.

# Development

1. Clone the repository and run `pipenv install` to install requirements from the pipfile.
2. Run `python .\download_models.py` to download required models from NLTK and Huggingface

# Deployment

The code defines a Docker image. Anytime a change is committed to `main`, Github Actions will issue a build command to Google Cloud. After the build is manually approved from the Google Cloud platform, it will automatically build AND deploy to a Google Cloud server.
