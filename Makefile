# user=langdonholmes
user=localhost:32000
image_name=itell-score-api

.PHONY: help build test push build-test-push

build:
	docker build --target base . -t ${user}/${image_name}

test:
	docker build --progress=plain --target test . -t test \
	&& docker run --rm --gpus 1 --env-file=.env -v /srv/repos/itell-api/huggingface:/usr/local/huggingface test

push:
	docker push ${user}/${image_name}

build-push: build push

help:
	@echo "Makefile arguments:"
	@echo ""
	@echo ":user: = ${user} - Name of DockerHub user"
	@echo ":image_name: = ${image_name} - Name of image to build"
	@echo ""
	@echo "Makefile commands:"
	@echo "build"
	@echo "test"

.DEFAULT_GOAL := build-push
