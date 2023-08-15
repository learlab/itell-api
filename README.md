# API for Textbook Summaries

This repository defines the api for our digital textbook project. It scores section summaries using a finetuned language model.

## Development

1. Clone the repository and run `pip install -r requirements.txt` to install requirements from the pipfile.
2. Run `python .\download_models.py` to download required models from SpaCy and Huggingface.

### Using Dev Containers

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension for VSCode.
2. Open the repository in VSCode.
3. Click the green button in the bottom left corner of the window and select "Reopen in Container".
4. The container will build and VSCode will reload. You should now be able to run the code in the container.

## Deployment

The code defines a Docker image. Anytime a change is committed to `main`, Github Actions will issue a build command to Google Cloud. After the build is manually approved from the Google Cloud platform, it will automatically build AND deploy to Google Cloud Run.

### LEARlab Bare Metal Deployment

The Makefile defines a build and push sequence to DockerHub.

The image is hosted on our bare metal server using a Kubernetes manifest.yaml file. The manifest file defines a deployment and service for the image. The deployment is configured to pull the image from DockerHub.

To update the deployment with a new Docker image, use `microk8s kubectl rollout restart deployment/itell-api`.

## Usage

The API request is a POST request to the `/score` endpoint. The request body should be a JSON object with fields defined in /models/summary.py.

The response is a JSON object with fields defined in /models/summary.py
