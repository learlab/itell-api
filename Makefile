IMAGENAME=itell-score-api

.PHONY: help dev build push run build-push

dev:
	python src/main.py

build:
	docker build . -t ${IMAGENAME}

push:
	docker push ${IMAGENAME}

run:
	docker run -p 8000:80 -d --rm textbook-summary-api

help:
	@echo "Makefile arguments:"
	@echo ""
	@echo ":IMAGENAME: = ${IMAGENAME} - Name of image to build"
	@echo ""
	@echo "Makefile commands:"
	@echo "build"
	@echo "dev"
	@echo "push"
	@echo "all"

.DEFAULT_GOAL := build-push

build-push: build push
