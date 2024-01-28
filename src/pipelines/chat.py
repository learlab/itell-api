import json
import os
from typing import AsyncGenerator

from vllm.sampling_params import SamplingParams
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.utils import random_uuid

# For local development on an RTX 3060 with 12GiB of VRAM
if os.environ.get("ENV") == "gpu-development":
    engine_args = AsyncEngineArgs(
        model="gpt2",
        download_dir="/usr/local/huggingface/hub",
        gpu_memory_utilization=0.80,
    )
else:
    # For deployment an an RTX A6000 with 48GiB of VRAM
    engine_args = AsyncEngineArgs(
        model="microsoft/Orca-2-13b",
        download_dir="/usr/local/huggingface/hub",
        gpu_memory_utilization=0.80,  # this leaves room for batching and other models
    )


engine = AsyncLLMEngine.from_engine_args(engine_args)


async def ChatPipeline(
    prompt: str, sampling_params: SamplingParams, **kwargs
) -> AsyncGenerator[bytes, None]:
    """Generate completion for the request.
    - prompt: the prompt to use for the generation.
    - sampling_params: the sampling parameters (See `SamplingParams` for details).
    """
    request_id = random_uuid()

    results_generator = engine.generate(prompt, sampling_params, request_id)

    async def stream_results() -> AsyncGenerator[bytes, None]:
        async for request_output in results_generator:  # type: ignore
            ret = {
                "request_id": request_id,
                "text": request_output.outputs[0].text,
            }
            # Add any additional kwargs to the response
            # Used for returning the chunk_slug in the SERT response
            if kwargs:
                ret.update(kwargs)
            yield (json.dumps(ret) + "\0").encode("utf-8")

    return stream_results()
