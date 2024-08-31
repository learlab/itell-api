import logging
import time
from typing import List

import faiss
import numpy as np

from ..pipelines.embed import EmbeddingPipeline
from ..schemas.embedding import RetrievalInput, RetrievalResults, RetrievalStrategy
from .supabase import SupabaseClient


class FAISS_Wrapper:
    def __init__(self, supabase: SupabaseClient) -> None:
        self.supabase = supabase
        self.index = None
        self.metadata = []
        self.pipeline = EmbeddingPipeline()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self.pipeline(text).tolist()[0]

    async def create_faiss_index(self) -> None:
        """Creates a FAISS index for the vector store."""
        response = await self.supabase.table("embeddings").select("*").execute()
        vector_data = response.data
        dim = 384

        embeddings = np.array([[0] * dim])
        metadata = np.array(
            [
                {
                    "chunk": "",
                    "text": "",
                    "chapter": "",
                    "module": "",
                    "page": "",
                    "context": "",
                }
            ]
        )

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
            metadata = np.append(metadata, data_info)
            embedding = data["embedding"].replace("[", "").replace("]", "").split(",")
            if len(embedding) != dim:
                logging.info(f"Skipping {data['chunk']} due to incorrect embedding length")
                continue
            arr = np.asarray(embedding, dtype=np.float32)
            embeddings = np.append(embeddings, [arr], axis=0)

        res = faiss.StandardGpuResources()  # use a single GPU
        index = faiss.index_factory(dim, "Flat", faiss.METRIC_INNER_PRODUCT)
        gpu_index_flat = faiss.index_cpu_to_gpu(res, 0, index)

        logging.info("Indexing embeddings...")
        faiss.normalize_L2(embeddings.astype(np.float32))
        gpu_index_flat.add(embeddings)
        logging.info(f"Indexing complete. {gpu_index_flat.ntotal} embeddings indexed.")

        self.index = gpu_index_flat
        self.metadata = metadata

    async def retrieve_chunks(self, input_body: RetrievalInput) -> RetrievalResults:
        def search_filter(doc):
            return doc["page"] in input_body.page_slugs

        query_embedding = np.array([self.embed_query(input_body.text)])
        faiss.normalize_L2(query_embedding.astype(np.float32))

        search_docs = []
        if input_body.retrieve_strategy == RetrievalStrategy.least_similar:
            similarities, results = self.index.search(query_embedding, 1000)
            # apply filter
            for j, i in enumerate(results[0]):
                doc = self.metadata[i]
                if search_filter(doc):
                    search_docs.append((doc, similarities[0][j]))
            search_docs = sorted(search_docs, key=lambda x: x[1], reverse=False)[
                0 : input_body.match_count
            ]
        else:
            similarities, results = self.index.search(query_embedding, 20)
            # apply filter
            for j, i in enumerate(results[0]):
                doc = self.metadata[i]
                if (
                    search_filter(doc)
                    and similarities[0][j] >= input_body.similarity_threshold
                ):
                    search_docs.append((doc, similarities[0][j]))
            search_docs = sorted(search_docs, key=lambda x: x[1], reverse=True)[
                0 : input_body.match_count
            ]
        matches = []
        for doc in search_docs:
            matches.append(
                {
                    "chunk": doc[0]["chunk"],
                    "page": doc[0]["page"],
                    "content": doc[0]["context"],
                    "similarity": doc[1],
                }
            )
        return RetrievalResults(matches=matches)

    async def page_similarity(self, embedding: list[float], page_slug: str) -> float:
        """Returns the similarity between the embedding and the target page."""
        embedding_arr = np.array([embedding])
        faiss.normalize_L2(embedding_arr.astype(np.float32))

        distances, results = self.index.search(embedding_arr, 1000)
        similarities = [
            distances[0][j]
            for j, i in enumerate(results[0])
            if self.metadata[i]["page"] == page_slug
        ]
        if not results.any():
            return 100.0
        return sum(similarities) / len(similarities)
