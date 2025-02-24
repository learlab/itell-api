# user=langdonholmes
user=localhost:32000
image_name=itell-score-api
cuda_device=1

.PHONY: help build test push build-test-push

build:
	docker build --target base . -t ${user}/${image_name}

test:
	docker build --progress=plain --target test . -t test \
	&& docker run --rm --gpus '"device=${cuda_device}"' --env-file=.env -v /media/nvme2-3.7TiB/huggingface:/usr/local/huggingface test

push:
	docker push ${user}/${image_name}

deploy:
	microk8s kubectl -n jhub rollout restart deployment/itell-api

all: build test push deploy

help:
	@echo "Makefile arguments:"
	@echo ""
	@echo ":user: = ${user} - Name of DockerHub user"
	@echo ":image_name: = ${image_name} - Name of image to build"
	@echo ":cuda_device: = ${cuda_device} - Which GPU to use"
	@echo ""
	@echo "Makefile commands:"
	@echo "build - Builds the Docker image."
	@echo "test - Runs pytest. Make exits if this fails."
	@echo "push - Pushes the images to our local container registry."
	@echo "deploy - Triggers a rollout restart of the k8s deployment."
	@echo "all (default) - build, test, push, and deploy."

.DEFAULT_GOAL := all
