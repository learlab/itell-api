import huggingface_hub
import spacy

huggingface_hub.hf_hub_download(
    repo_id='tiedaar/longformer-content-global',
    filename='pytorch_model.bin'
    )

huggingface_hub.hf_hub_download(
    repo_id='tiedaar/longformer-wording-global',
    filename='pytorch_model.bin'
    )

spacy.cli.download('en_core_web_sm')
