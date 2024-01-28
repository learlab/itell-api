from transformers import AutoTokenizer, AutoModel
import torch
from torch import Tensor
import torch.nn.functional as F


class EmbeddingPipeline:
    model_name = "sentence-transformers/all-MiniLM-L6-v2"

    def __init__(self):
        self.model = AutoModel.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

    def __call__(self, text_input: str) -> Tensor:
        encoded_input = self.tokenizer(
            text_input, padding=True, truncation=True, return_tensors="pt"
        )
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        embed = self.mean_pooling(model_output, encoded_input["attention_mask"])
        embed = F.normalize(embed, p=2, dim=1)

        return embed

    def score_similarity(self, a: str, b: str) -> float:
        """Return semantic similarity score between a and b"""
        a_embed = self(a)
        b_embed = self(b)

        return float(torch.mm(a_embed, b_embed.transpose(0, 1)))  # cosine

    def mean_pooling(self, model_output, attention_mask):
        """Take attention mask into account for correct averaging"""
        # First element of model_output contains all token embeddings
        token_embeddings = model_output[0]
        input_mask_expanded = (
            attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        )
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
            input_mask_expanded.sum(1), min=1e-9
        )
