import nltk
from huggingface_hub import hf_hub_download

# These downloads will go to locations that are specific to the current user
# Make sure not to run as root
nltk.download('punkt')
nltk.download('stopwords')
hf_hub_download(repo_id='tiedaar/summary-longformer-content', filename='pytorch_model.bin')
hf_hub_download(repo_id='tiedaar/summary-longformer-wording', filename='pytorch_model.bin')
