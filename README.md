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

The Makefile defines a build and push sequence to DockerHub. Make sure to create a `.env` file in the application root directory like the following. It should contain all the textbook names defined in the src/models/textbooks.py.

```
MACRO_ECON_HOST=https://[SupaBase Database Sub-domain].supabase.co
MACRO_ECON_PASSWORD=[SupaBase Password]
CONTAINER_PORT=8001
```

### LEARlab Bare Metal Deployment

The image is hosted on our bare metal server using a Kubernetes manifest.yaml file. The manifest file defines a deployment and service for the image. The deployment is configured to pull the image from DockerHub.

The deployment relies on a Kubernetes secret. This was created using `microk8s kubectl create secret generic supabase-itell --from-env-file=.env`

To update the deployment with a new Docker image, use `microk8s kubectl rollout restart deployment/itell-api`.

## Usage

The main API request is a POST request to the `/score/summary` endpoint. The request body should be a JSON object with fields defined in /models/summary.py.

The response is a JSON object with fields defined in /models/summary.py
