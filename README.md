# iTELL AI API

Welcome to iTELL AI, a REST API for intelligent textbooks. iTELL AI provides the following principal features:

- Summary scoring
- Constructed response item scoring
- Structured dialogues with conversational AI

iTELL AI also provides some utility endpoints that are used by the content management system. 
 - Generating transcripts from YouTube videos
 - Creating chunk embeddings and managing a vector store.

## Usage

The API endpoints are hosted at the [/docs](https://itell-api.learlab.vanderbilt.edu/docs) location.
 - The endpoints are defined in `src/main.py`.
 - The Pydantic models are defined in `src/models/`.

## Development

This repository can run in three modes: development, gpu-development, and production.

 - `development` mode runs without a GPU. Chat is disabled.
 - `gpu-development` mode runs with a GPU and a smaller model for testing chat.
 - `production` mode runs with a GPU and the full chat model.

Please set ENV=development, ENV=gpu-development, or ENV=production in your .env file and make sure these environment variables are loaded in the shell session where you run the API.
 **If no ENV is set, the default is production, which will likely fail on your system.**

1. Install `protobuf-compiler` on your system. This is a requirement to build `gcld3`.
2. Clone the repository and run `pip install -r requirements/dev.in` or `pip install -r requirements/gpu.in` depending on your environment.
3. Make sure to create a `.env` file in the application root directory like `.env.example`
   - Ask a team member for the values to use in the `.env` file.
   - If you are on Mac, you will need to add `export ` before each line in the `.env` file.
   - Load the environment variables with `source .env` or by using the provided [devcontainer](#using-dev-containers).
4. Install development dependencies: `pip install pip-tools pytest rich`
5. Run `pytest` from the root directory to run the test suite.
   - Please write tests for any new endpoints.
   - Please run tests **using `pytest`** before requesting a code review.
   - Pytest will run the tests appropriate to your environment.

### Modifying Requirements
An NVidia GPU is required to pin dependencies for our production environment. If you do not have a GPU and you have changed the dependencies, ask a team member to rebuild the requirements file before deploying. There is no need to compile `requirements/base.in`.

1. Make changes to `requirements/base.in` and/or `requirements/gpu.in`
2. Run `pip-compile requirements/gpu.in` with a GPU.

### Using Dev Containers
This devcontainer only works on machines with an NVidia GPU.

1. Install the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension for VSCode.
2. Open the repository in VSCode.
3. Click the green button in the bottom left corner of the window and select "Reopen in Container".
4. The container will build and VSCode will reload. You should now be able to run the code in the container.

## Deployment

The Makefile defines a build and push sequence to the localhost:32000 container registry.

### LEARlab Bare Metal Deployment

The image is hosted on our bare metal server. `kubernetes/manifest.yaml` defines a deployment and service for the image. The deployment is configured to pull the image from a local Docker registry (microk8s built-in registry).

The repository is located at `/srv/repos/itell-api` on the lab server. You should only need the following commands to deploy an update. Run these from within the repository directory:

1. `git fetch`  
2. `git pull`  
3. `make`  

If you need to make any quick fixes to get the deployment working, please do not forget to push those changes directly to main:  
1. Make your changes to the files
2. `git add .`
3. `git commit -m [commit message]`
4. `git push`

The deployment relies on a Kubernetes secret. This was created using `microk8s kubectl create secret generic supabase-itell --from-env-file=.env`. You will need to run this command from within the repository directory whenever environment variables are updated. Since the `.env` file is not pushed to Github, you will also need to manually update this file on the server before running the `create secret` command.

To access the running container, find the pod's id using `microk8s kubectl get pods`. Then, run `microk8s kubectl exec -i -t itell-api-[POD-ID] -- /bin/bash`
