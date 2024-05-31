import os
from typing import AsyncGenerator

from vllm.sampling_params import SamplingParams
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.utils import random_uuid

from ..models.chat import ChatResponse

# For local development on an RTX 3060 with 12GiB of VRAM
if os.environ.get("ENV") == "gpu-development":
    engine_args = AsyncEngineArgs(
        model="gpt2",
        download_dir="/usr/local/huggingface/hub",
        gpu_memory_utilization=0.80,
    )
else:
    # For deployment on an RTX A6000 with 48GiB of VRAM
    engine_args = AsyncEngineArgs(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        download_dir="/usr/local/huggingface/hub",
        gpu_memory_utilization=0.80,  # this leaves room for batching and other models
    )


engine = AsyncLLMEngine.from_engine_args(engine_args)


async def chat_pipeline(
    prompt: str, sampling_params: SamplingParams, preface_text: str = "", **kwargs
) -> AsyncGenerator[bytes, None]:
    """Generate completion for the request.
    - prompt: the prompt to use for the generation.
    - sampling_params: the sampling parameters (See `SamplingParams` for details).
    """
    request_id = random_uuid()

    results_generator = engine.generate(prompt, sampling_params, request_id)

    async def stream_results() -> AsyncGenerator[bytes, None]:
        async for request_output in results_generator:  # type: ignore
            generated_text = request_output.outputs[0].text

            # Check if the last part of the output is the USER token
            # If it is, remove this and any preceding whitespace
            # before sending the final response.
            if request_output.finished:
                generated_text = generated_text.removesuffix("USER").rstrip()

            out_text = preface_text + generated_text

            chat_output = ChatResponse(request_id=request_id, text=out_text, **kwargs)

            yield f"event: completion\ndata: {chat_output.model_dump_json()}\n\n"

    return stream_results()
