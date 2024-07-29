from typing import Any, List

from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings

from ..pipelines.embed import EmbeddingPipeline
from ..schemas.embedding import (
    ChunkInput,
    DeleteUnusedInput,
    RetrievalInput,
    RetrievalResults,
    RetrievalStrategy,
)
from .supabase import SupabaseClient


class Embedding(Embeddings):
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        self.embed_query(*args, **kwds)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        return [EmbeddingPipeline()(text).tolist() for text in texts]

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return EmbeddingPipeline()(text).tolist()[0]


class FAISS:
    def __init__(self, supabase: SupabaseClient) -> None:
        self.supabase = supabase
        self.db = None

    async def create_faiss_index(self) -> None:
        """Creates a FAISS index for the vector store."""
        response = await self.supabase.table("embeddings").select("*").execute()
        vector_data = response.data

        metadata = []
        embeddings = []

        vector_data = filter(lambda x: x["embedding"] is not None, vector_data)

        for data in vector_data:
            data_info = {
                "chunk": data["chunk"],
                "text": data["text"],
                "chapter": data["chapter"],
                "module": data["module"],
                "page": data["page"],
                "context": data["content"],
            }
            metadata.append(data_info)
            arr = data["embedding"].replace("[", "").replace("]", "").split(",")
            embeddings.append((data["chunk"], [float(i) for i in arr]))

        embedding = Embedding()

        self.db = FAISS.from_embeddings(embeddings, embedding)
        self.db.save_local(folder_path="faiss_db", index_name="myFaissIndex")
        print(self.db.index.ntotal)

        # searchDocs = self.db.similarity_search("What is governance?")
        # print(searchDocs[0])

    async def retrieve_chunks(self, input_body: RetrievalInput) -> RetrievalResults:
        def search_filter(doc):
            return doc["page_slug"] in input_body.page_slugs

        if input_body.retrieve_strategy == RetrievalStrategy.least_similar:
            search_docs = self.db.similarity_search_with_score(
                input_body.text,
                k=1000,  # get all docs
                filter=search_filter,
                score_threshold=input_body.similarity_threshold,
                reverse=True,
            )

            # sort in ascending order
            search_docs = sorted(search_docs, key=lambda x: x[1])
            return search_docs[: input_body.match_count]

        searchDocs = self.db.similarity_search_with_score(
            input_body.text,
            k=input_body.match_count,
            filter=search_filter,
            score_threshold=input_body.similarity_threshold,
        )
        return searchDocs


# pip install -U langchain-community faiss-cpu langchain-openai tiktoken
