from transformers import (
    pipeline,
    AutoTokenizer,
)
from auto_gptq import AutoGPTQForCausalLM

from langchain import HuggingFacePipeline
from langchain.llms.base import BaseLLM

from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.actions import action
from nemoguardrails.actions.actions import ActionResult
from nemoguardrails.llm.helpers import get_llm_instance_wrapper
from nemoguardrails.llm.providers import register_llm_provider

from src.generate_embeddings import retrieve_chunks
from src.database import get_client
from models.textbook import TextbookNames

from typing import Optional
from supabase.client import Client


def get_model_config(config: RailsConfig, type: str):
    """Quick helper to return the config for a specific model type."""
    for model_config in config.models:
        if model_config.type == type:
            return model_config


def get_model():
    """Loads the Open-Orca LLM."""
    repo_id = "TheBloke/OpenOrcaxOpenChat-Preview2-13B-GPTQ"

    model_params = {
        "device": "cuda:0",
        "use_safetensors": True,
        "use_triton": False,
        "quantize_config": None,
    }

    pipeline_params = {"max_new_tokens": 128, "do_sample": True, "temperature": 0.2}

    model = AutoGPTQForCausalLM.from_quantized(repo_id, **model_params)
    tokenizer = AutoTokenizer.from_pretrained(repo_id, use_fast=False)

    pipe = pipeline(
        "text-generation",
        model=model,  # type: ignore
        tokenizer=tokenizer,
        **pipeline_params
    )

    llm = HuggingFacePipeline(pipeline=pipe, model_kwargs=pipeline_params)

    return llm


@action(is_system_action=True)
async def retrieve_relevant_chunks(
    context: dict[str, str],
    db: Client,
    llm: Optional[BaseLLM] = None,
):
    """Retrieve relevant chunks from the knowledge base and add them to the context."""
    user_message = context["last_user_message"]

    result = retrieve_chunks(user_message, db, match_count=1)

    if not result:
        return ActionResult(return_value="No relevant chunks found.")

    else:
        result = result[0]
        context_updates = {
            "relevant_chunks": (
                f"Question: {user_message}\n"
                f"Citing: {result['clean_text']}\n"
                f"Source: {result['heading']}"
            )
        }

        return ActionResult(
            return_value=context_updates["relevant_chunks"],
            context_updates=context_updates,
        )


def init_main_llm():
    HFPipeline = get_llm_instance_wrapper(
        llm_instance=get_model(), llm_type="hf_pipeline"
    )

    register_llm_provider("hf_pipeline", HFPipeline)


def init(llm_rails: LLMRails):
    db = get_client(TextbookNames.THINK_PYTHON)
    llm_rails.register_action_param("db", db)
    # Initialize the models
    init_main_llm()

    llm_rails.register_action(
        action=retrieve_relevant_chunks, name="retrieve_relevant_chunks"
    )
