
from .models.message import Message

from .auth import get_role, developer_role
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import sentry_sdk
from .routers import score, chat, generate


logging.basicConfig(level=logging.WARNING)

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


app = FastAPI(
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.app:app", host="0.0.0.0", port=int(os.getenv("port", 8001)), reload=False
    )
