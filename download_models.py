import huggingface_hub
import spacy

huggingface_hub.snapshot_download(
    repo_id='tiedaar/longformer-content-global',
    # filename='pytorch_model.bin'
    )

huggingface_hub.snapshot_download(
    repo_id='tiedaar/longformer-wording-global',
    # filename='pytorch_model.bin'
    )

huggingface_hub.snapshot_download(
    repo_id='facehugger92/POE_QA_mpnetbase',
    )

spacy.cli.download('en_core_web_sm')
