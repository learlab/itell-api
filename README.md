# API for Textbook Summaries

This repository defines the api for our digital textbook project. The iTELL API provides the frontend with GPU-accelerated natural language processing services. Its principal features are the following:

- Summary scoring
- Short answer scoring
- Document embedding
- Chat bot with guardrails

## Development

This repository can run in three modes: development, gpu-development, and production.
`development` mode runs without a GPU. Chat is disabled.
`gpu-development` mode runs with a GPU and a smaller, quantized model for chat.
`production` mode runs with a GPU and the full chat model.
Please set ENV=development, ENV=gpu-development, or ENV=production in your .env file. If no ENV is set, the default is production, which will likely fail on your system.

1. Clone the repository and run `pip install -r requirements.txt` (use gpu-requirements.txt if you have a GPU)
 - If you need to adjust the requirements, please install pip-tools: `pip install pip-tools`
 - Make changes to the `requirements.in` file or the `gpu-requirements.in` file
 - Rebuild the `requirements.txt` file with `pip-compile requirements.in` and/or `pip-compile gpu-requirements.in`
2. Run `python -m spacy download en_core_web_sm` to download required model from SpaCy
3. Make sure to create a `.env` file in the application root directory like the following. It should contain all the textbook names defined in the `src/models/textbooks.py`:

```
MACRO_ECON_HOST=https://[SupaBase Database Sub-domain].supabase.co
MACRO_ECON_PASSWORD=[SupaBase Password]
CONTAINER_PORT=8001
```

4. Load the environment variables with `source .env` or by using the provided devcontainer.
5. Test `python -m src.test_main` to make sure everything is working.

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

To access the running container, find the pod's id using `microk8s kubectl get pods` then run `microk8s kubectl exec -i -t itell-api-[POD-ID] -- /bin/bash`

## Usage

The API endpoints are defined in `src/main.py`.

The request and response bodies are defined as pydantic objects in the `models` folder.
