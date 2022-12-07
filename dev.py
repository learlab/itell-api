from nltk import download as nltk_download
from huggingface_hub import hf_hub_download

nltk_download('punkt')
hf_hub_download(repo_id='tiedaar/summary-longformer-content', filename='pytorch_model.bin')
hf_hub_download(repo_id='tiedaar/summary-longformer-wording', filename='pytorch_model.bin')