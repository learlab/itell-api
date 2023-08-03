import huggingface_hub
import spacy
from transformers.util.hub import move_cache

huggingface_hub.hf_hub_download(
    repo_id='tiedaar/longformer-content-global',
    filename='pytorch_model.bin'
    )

huggingface_hub.hf_hub_download(
    repo_id='tiedaar/longformer-wording-global',
    filename='pytorch_model.bin'
    )

move_cache()

spacy.cli.download('en_core_web_sm')
