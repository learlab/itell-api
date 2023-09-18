import torch
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

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


def get_vicuna():
    """Loads the Vicuna 13B LLM."""
    repo_id = "lmsys/vicuna-13b-v1.5"

    model_params = {
        "device_map": "auto",
        "quantization_config": BitsAndBytesConfig(
            load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
        ),
        "low_cpu_mem_usage": True,
        "do_sample": True,
    }

    pipeline_params = {"max_new_tokens": 128, "do_sample": True, "temperature": 0.2}

    model = AutoModelForCausalLM.from_pretrained(repo_id, **model_params)
    tokenizer = AutoTokenizer.from_pretrained(repo_id, use_fast=False)

    pipe = pipeline(
        "text-generation", model=model, tokenizer=tokenizer, **pipeline_params
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
    HFPipelineVicuna = get_llm_instance_wrapper(
        llm_instance=get_vicuna(), llm_type="hf_pipeline_vicuna"
    )

    register_llm_provider("hf_pipeline_vicuna", HFPipelineVicuna)


def init(llm_rails: LLMRails):
    db = get_client(TextbookNames.THINK_PYTHON)
    llm_rails.register_action_param("db", db)
    # Initialize the models
    init_main_llm()

    llm_rails.register_action(
        action=retrieve_relevant_chunks, name="retrieve_relevant_chunks"
    )
