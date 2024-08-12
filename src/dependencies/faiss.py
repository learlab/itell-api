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


class FAISS_Wrapper:
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

        self.db = FAISS.from_embeddings(embeddings, embedding, metadata)
        self.db.save_local(folder_path="faiss_db", index_name="myFaissIndex")

    async def retrieve_chunks(self, input_body: RetrievalInput) -> RetrievalResults:
        def search_filter(doc):
            return doc["page"] in input_body.page_slugs

        search_docs = []
        if input_body.retrieve_strategy == RetrievalStrategy.least_similar:
            results = self.db.similarity_search_with_score(
                input_body.text,
                k=1000,  # get all docs
                filter=search_filter,
            )

            # sort in descending order
            results = sorted(results, key=lambda x: x[1], reverse=True)
            search_docs = results[: input_body.match_count]
        else:
            search_docs = self.db.similarity_search_with_score(
                input_body.text,
                k=input_body.match_count,
                filter=search_filter,
                score_threshold=input_body.similarity_threshold,
            )
        matches = []
        for doc in search_docs:
            matches.append(
                {
                    "chunk": doc[0].metadata["chunk"],
                    "page": doc[0].metadata["page"],
                    "content": doc[0].metadata["context"],
                    "similarity": doc[1],
                }
            )
        return RetrievalResults(matches=matches)
        return searchDocs
    
    async def page_similarity(self, text: str, page_slug: str) -> float:
        """Returns the similarity between the embedding and the target page."""
        results = self.db.similarity_search_with_score(
            text,
            k=1000,  # get all docs
            filter={"page": page_slug},
        )
        if not results:
            return 100.0
        similarities = [result[1] for result in results]
        return sum(similarities) / len(similarities)


# pip install -U langchain-community faiss-cpu langchain-openai tiktoken
