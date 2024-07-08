# iTELL AI API

Welcome to iTELL AI, a REST API for intelligent textbooks. iTELL AI provides the following principal features:

- Summary scoring
- Constructed response item scoring
- Structured dialogues with conversational AI

iTELL AI also provides some utility endpoints that are used by the content management system. 
 - Generating transcripts from YouTube videos
 - Creating chunk embeddings and managing a vector store.

## Usage

The API documention is hosted at the [/redoc](https://itell-api.learlab.vanderbilt.edu/redoc) location.
 - The app is defined in `src/app.py`.
 - The endpoints are defined in `src/routers/`.
 - The Pydantic models are defined in `src/schemas/`.
 - External connections are defined in `src/dependencies/`.
 - NLP and AI pipelines are defined in `src/pipelines/`.
 - Service logic is defined in `src/services/`.

## Development

Development requires a GPU with ~50GiB of VRAM.

1. If not using the provided dev container, install `protobuf-compiler` on your system. This is a requirement to build `gcld3`.
2. Clone the repository and run `pip install -r requirements/requirements.in`
3. Make sure to create a `.env` file in the application root directory like `.env.example`
   - Ask a team member for the values to use in the `.env` file.
   - If you are on Mac, you will need to add `export ` before each line in the `.env` file.
   - Load the environment variables with `source .env` or by using the provided [devcontainer](#using-dev-containers).
4. If not using the provided dev container, install development dependencies: `pip install pip-tools pytest asgi-lifespan`
5. Run `pytest` from the root directory to run the test suite.
   - Please write tests for any new endpoints.
   - Please run tests **using `pytest`** before requesting a code review.

### Modifying Requirements

1. Make changes to `requirements/requirements.in`
2. Run `pip-compile requirements/requirements.in` with a GPU.

### Using Dev Containers

This devcontainer only works on machines with an NVidia GPU.

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension for VSCode.
2. Open the repository in VSCode.
3. Click the green button in the bottom left corner of the window and select "Reopen in Container".
4. The container will build and VSCode will reload. You should now be able to run the code in the container.

## Deployment

The Makefile defines a build and push sequence to the localhost:32000 container registry.

### LEARlab Bare Metal Deployment

The image is hosted on LEAR Lab Development Server #1.

 - `kubernetes/manifest.yaml` defines a deployment and service for the image.
 - The deployment is configured to pull the image from a local Docker registry (microk8s built-in registry).
 - The repository is located at `/srv/repos/itell-api` on the lab server. 
 
 You should only need the following commands to deploy an update. Run these from within the repository directory:
1. `git fetch`  
2. `git pull`  
3. `make cuda_device=X` (Where X is 0, 1, or 2 depending on which GPU is available)

If you need to make any quick fixes to get the deployment working, please do not forget to push those changes directly to main:  
1. Make your changes to the files
2. `git add .`
3. `git commit -m [commit message]`
4. `git push`

## Updating Production Environment Variables

If you make any changes to the required environment variables, these must be udpated using a kubernetes secret.

1. Manually update the .env file on the production server. This is not version controlled.
2. `microk8s kubectl delete secret itell-ai`
3. `microk8s kubectl create secret generic itell-ai --from-env-file=.env`

## Access the Running Container

1. Find the pod's id using `microk8s kubectl get pods`.
2. Run `microk8s kubectl exec -i -t itell-api-[POD-ID] -- /bin/bash`

## Access the Running Container's Logs

`microk8s kubectl logs itell-api-[tab-to-complete]`
