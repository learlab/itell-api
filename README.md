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
 - The Pydantic models are defined in `models/`.

## Development

This repository can run in three modes: development, gpu-development, and production.

 - `development` mode runs without a GPU. Chat is disabled.
 - `gpu-development` mode runs with a GPU and a smaller, quantized model for chat.
 - `production` mode runs with a GPU and the full chat model.

Please set ENV=development, ENV=gpu-development, or ENV=production in your .env file.
 **If no ENV is set, the default is production, which will likely fail on your system.**

1. Clone the repository and run `pip install -r requirements.txt` (use gpu-requirements.txt if you have a GPU)
2. Run `python -m spacy download en_core_web_sm` to download required model from SpaCy
3. Make sure to create a `.env` file in the application root directory like the following.
   - If you are testing or working with legacy content databases, be sure to include the appropriate database credentials.
   - If you are only working with Strapi-based deployments, you need only the Strapi credentials and the Vector-store credentials.
   - Load the environment variables with `source .env` or by using the provided devcontainer.
4. Install pytest: `pip install pytest`
5. Run `pytest` from the root directory to run the test suite.
   - Please write tests for any new endpoints.
   - Please run tests **using `pytest`** before requesting a code review.

### Modifying Requirements

1. Install pip-tools: `pip install pip-tools`
2. Make changes to `requirements.in` or `gpu-requirements.in`
   - Only modify `gpu-requirments.in` if you have a GPU for compilation and testing.
3. Rebuild `requirements.txt` with `pip-compile requirements.in`
4. If you have a GPU, run `pip-compile gpu-requirements.in`

### Using Dev Containers

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
4. `microk8s kubectl rollout restart deployment/itell-api`  

If you need to make any quick fixes to get the deployment working, please do not forget to push those changes directly to main:  
1. Make your changes to the files
2. `git add .`
3. `git commit -m [commit message]`
4. `git push`

The deployment relies on a Kubernetes secret. This was created using `microk8s kubectl create secret generic supabase-itell --from-env-file=.env`. You will need to run this command from within the repository directory whenever environment variables are updated. Since the `.env` file is not pushed to Github, you will also need to manually update this file on the server before running the `create secret` command.

To access the running container, find the pod's id using `microk8s kubectl get pods`. Then, run `microk8s kubectl exec -i -t itell-api-[POD-ID] -- /bin/bash`
