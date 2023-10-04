from typing import AsyncGenerator
from fastapi.responses import StreamingResponse
from vllm.sampling_params import SamplingParams

from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.utils import random_uuid

import json


engine_args = AsyncEngineArgs(
    # model = "Open-Orca/OpenOrcaxOpenChat-Preview2-13B",
    model="TheBloke/OpenOrcaxOpenChat-Preview2-13B-AWQ",  # testing only
    download_dir="/usr/local/huggingface/hub",
    gpu_memory_utilization=0.95,  # .80 for production
    dtype="half",  # testing only
    quantization="awq",  # testing only
)

engine = AsyncLLMEngine.from_engine_args(engine_args)


async def ChatPipeline(
    prompt: str, sampling_params: SamplingParams
) -> StreamingResponse:
    """Generate completion for the request.
    - prompt: the prompt to use for the generation.
    - other fields: the sampling parameters (See `SamplingParams` for details).
    """
    request_id = random_uuid()

    results_generator = engine.generate(prompt, sampling_params, request_id)

    # Streaming case
    async def stream_results() -> AsyncGenerator[bytes, None]:
        async for request_output in results_generator: # type: ignore
            prompt = request_output.prompt
            text_outputs = [prompt + output.text for output in request_output.outputs]
            ret = {"text": text_outputs}
            yield (json.dumps(ret) + "\0").encode("utf-8")

    return StreamingResponse(stream_results())
