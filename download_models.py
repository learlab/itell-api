from huggingface_hub import hf_hub_download
from spacy.cli import download

hf_hub_download(repo_id='tiedaar/longformer-content-global',
                filename='pytorch_model.bin')
hf_hub_download(repo_id='tiedaar/longformer-wording-global',
                filename='pytorch_model.bin')

download('en_core_web_sm')