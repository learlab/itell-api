from typing import AsyncGenerator
from vllm.sampling_params import SamplingParams

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.utils import random_uuid

import json
import os

# For local development on an RTX 3060 with 12GiB of VRAM
if os.environ.get("ENV") == "development":
    engine_args = AsyncEngineArgs(
        model="TheBloke/OpenOrcaxOpenChat-Preview2-13B-AWQ",
        download_dir="/usr/local/huggingface/hub",
        gpu_memory_utilization=0.85,
        dtype="half",
        quantization="awq",
    )

# For deployment an an RTX A6000 with 48GiB of VRAM
engine_args = AsyncEngineArgs(
    model="Open-Orca/OpenOrcaxOpenChat-Preview2-13B",
    download_dir="/usr/local/huggingface/hub",
    gpu_memory_utilization=0.80,
)


engine = AsyncLLMEngine.from_engine_args(engine_args)


async def ChatPipeline(
    prompt: str, sampling_params: SamplingParams
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
                "text": request_output.outputs[-1].text,
                }
            yield (json.dumps(ret) + "\0").encode("utf-8")

    return stream_results()
