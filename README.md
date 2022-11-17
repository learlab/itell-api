# API for Textbook Summaries

This repository defines the api for our digital textbook project.

Currently, it scores section summaries using a finetuned language model.

## commands for gcloud
```
gcloud builds submit --tag gcr.io/textbook-demo/textbook-summary-api
gcloud run deploy --image gcr.io/textbook-demo/textbook-summary-api --platform managed
```
