# API for Textbook Summaries

This repository defines the api for our digital textbook project. The iTELL API provides the frontend with GPU-accelerated natural language processing services. Its principal features are the following:

- Sumamry scoring
- Short answer scoring
- Intelligent tutor API

## Development

1. Clone the repository and run `pip install -r requirements.txt`
 - If you need to adjust the requirements, please install pip-tools: `pip install pip-tools`
 - Make changes to the `requirements.in` file
 - Rebuild the `requirements.txt` file with `pip-compile`

2. Run `python ./download_models.py` to download required models from SpaCy and Huggingface
3. Make sure to create a `.env` file in the application root directory like the following. It should contain all the textbook names defined in the `src/models/textbooks.py`:

```
MACRO_ECON_HOST=https://[SupaBase Database Sub-domain].supabase.co
MACRO_ECON_PASSWORD=[SupaBase Password]
CONTAINER_PORT=8001
```

5. Test `python -m src.test_main` to make sure everything is working.

### Using Dev Containers

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension for VSCode.
2. Open the repository in VSCode.
3. Click the green button in the bottom left corner of the window and select "Reopen in Container".
4. The container will build and VSCode will reload. You should now be able to run the code in the container.

## Deployment

The Makefile defines a build and push sequence to the localhost:32000 container registry.

### LEARlab Bare Metal Deployment

The image is hosted on our bare metal server using a Kubernetes manifest.yaml file. The manifest file defines a deployment and service for the image. The deployment is configured to pull the image from a local Docker registry (microk8s built-in registry).

The deployment relies on a Kubernetes secret. This was created using `microk8s kubectl create secret generic supabase-itell --from-env-file=.env`

To update the deployment with a new Docker image, use `microk8s kubectl rollout restart deployment/itell-api`.

To access the running container, find the pod's id using `microk8s kubectl get pods` then run `microk8s kubectl exec -i -t itell-api-[POD-ID-SEQUENCE] -- /bin/bash`

## Usage

The API endpoints are defined in `src/main.py`.

The request and response bodies are defined as pydantic objects in the `models` folder.
