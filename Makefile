user=langdonholmes
image_name=itell-score-api

.PHONY: help build push run build-push

build:
	docker build . -t ${user}/${image_name}

push:
	docker push ${user}/${image_name}

help:
	@echo "Makefile arguments:"
	@echo ""
	@echo ":user: = ${user} - Name of DockerHub user"
	@echo ":image_name: = ${image_name} - Name of image to build"
	@echo ""
	@echo "Makefile commands:"
	@echo "build"
	@echo "push"
	@echo "build-push"

.DEFAULT_GOAL := build-push

build-push: build push
