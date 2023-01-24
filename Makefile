.PHONY: dev build run

dev:
	python src/main.py

build:
	docker build . -t textbook-summary-api


run:
	docker run -p 8000:80 -d --rm textbook-summary-api

# commands for gcloud
# gcloud builds submit --tag gcr.io/textbook-demo/textbook-summary-api
# gcloud run deploy --image gcr.io/textbook-demo/textbook-summary-api --platform managed