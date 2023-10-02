"""
This file can be used to download models from HuggingFace Hub and Spacy.
We have set up a persistent volume for model storage on our deployment server,
so this file is no longer needed for deployment.
"""

import huggingface_hub
import spacy

hf_models = [
    "tiedaar/longformer-content-global",
    "tiedaar/longformer-wording-global",
    "tiedaar/short-answer-classification",
    "vaiibhavgupta/finetuned-bleurt-large",
    "sentence-transformers/all-MiniLM-L6-v2",
    "Open-Orca/OpenOrcaxOpenChat-Preview2-13B",
]

for repo_name in hf_models:
    huggingface_hub.snapshot_download(repo_id=repo_name)

spacy.cli.download("en_core_web_sm")  # type: ignore
