import logging
import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .dependencies.auth import developer_role, get_role
from .dependencies.strapi import Strapi
from .dependencies.supabase import SupabaseClient
from .logging.setup import setup_logging
from .schemas.message import Message
from .routers import admin, chat, generate, score
from transformers import logging as transformers_logging

transformers_logging.set_verbosity_error()
logger = logging.getLogger(__name__)

setup_logging()

description = """
Welcome to iTELL AI, a REST API for intelligent textbooks.
iTELL AI provides the following principal features:

- Summary scoring
- Constructed response item scoring
- Structured dialogues with conversational AI

iTELL AI also provides some utility endpoints
that are used by the content management system.
- Generating transcripts from YouTube videos
- Creating chunk embeddings and managing a vector store.
"""

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("ENV"),
    traces_sample_rate=1.0,
    profiles_sample_rate=0.05,  # Log 5% of transactions
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.strapi = Strapi()
    app.state.supabase = SupabaseClient(
        os.environ["VECTOR_HOST"],
        os.environ["VECTOR_KEY"],
    )
    try:
        yield
    finally:
        await app.state.strapi.client.aclose()


app = FastAPI(
    lifespan=lifespan,
    # MetaData
    title="iTELL AI",
    description=description,
    summary="AI for intelligent textbooks",
    version="0.0.2",
    contact={
        "name": "LEAR Lab",
        "url": "https://learlab.org/contact",
        "email": "lear.lab.vu@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "identifier": "MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def hello() -> Message:
    """Welcome to iTELL AI!"""
    return Message(message="This is a summary scoring API for iTELL.")


app.include_router(score.router, dependencies=[Depends(get_role)])
app.include_router(chat.router, dependencies=[Depends(get_role)])
app.include_router(generate.router, dependencies=[Depends(developer_role)])
app.include_router(admin.router, dependencies=[Depends(developer_role)])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.app:app", host="0.0.0.0", port=int(os.getenv("port", 8001)), reload=False
    )
