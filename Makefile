user=langdonholmes
image_name=itell-score-api

.PHONY: help download build push run build-push

download:
	python src/download_models.py

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
	@echo "dev"
	@echo "push"
	@echo "all"

.DEFAULT_GOAL := build-push

build-push: build push
