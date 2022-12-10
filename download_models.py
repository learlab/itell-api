import nltk
from huggingface_hub import hf_hub_download

nltk.download('punkt', download_dir='/usr/local/nltk_data')
nltk.download('stopwords', download_dir='/usr/local/nltk_data')
hf_hub_download(repo_id='tiedaar/summary-longformer-content', filename='pytorch_model.bin')
hf_hub_download(repo_id='tiedaar/summary-longformer-wording', filename='pytorch_model.bin')
