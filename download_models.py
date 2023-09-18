import huggingface_hub
import spacy

huggingface_hub.snapshot_download(
    repo_id='tiedaar/longformer-content-global',
    )

huggingface_hub.snapshot_download(
    repo_id='tiedaar/longformer-wording-global',
    )

huggingface_hub.snapshot_download(
    repo_id='facehugger92/POE_QA_mpnetbase',
    )

huggingface_hub.snapshot_download(
    repo_id='lmsys/vicuna-13b-v1.5',
    )

huggingface_hub.snapshot_download(
    repo_id='sentence-transformers/all-MiniLM-L6-v2',
    )

spacy.cli.download('en_core_web_sm')  # type: ignore
