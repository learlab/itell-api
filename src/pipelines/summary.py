from typing import Dict

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TextClassificationPipeline,
)


class SummaryPipeline(TextClassificationPipeline):
    def __init__(self, model, *args, **kwargs):
        self.model_name = model
        super().__init__(
            model=AutoModelForSequenceClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model, use_fast=False),
            function_to_apply="None",
            device=0 if torch.cuda.is_available() else -1,
            truncation=True,
            max_length=4096,
            *args,
            **kwargs,
        )

    def preprocess(self, input_str: str, **tokenizer_kwargs) -> Dict[str, torch.Tensor]:
        """Only works with a single input, not a list of inputs."""
        input_dict = self.tokenizer(input_str, **tokenizer_kwargs)  # type: ignore

        input_ids = input_dict["input_ids"]
        if not isinstance(input_ids, list):
            raise TypeError(f"Expected list, got {type(input_ids)}")

        return {k: torch.tensor([v]) for k, v in input_dict.items()}

    def score(self, input_str: str, **kwargs) -> float:
        try:
            score = self(input_str, **kwargs)[0]["score"]
        except (IndexError, KeyError) as e:
            raise ValueError(f"Failed to get score: {e}")
        return float(score)


class LongformerPipeline(SummaryPipeline):
    def preprocess(self, input_str: str, **tokenizer_kwargs) -> Dict[str, torch.Tensor]:
        """Only works with a single input, not a list of inputs."""
        input_dict = self.tokenizer(input_str, **tokenizer_kwargs)  # type: ignore

        input_ids = input_dict["input_ids"]
        if not isinstance(input_ids, list):
            raise TypeError(f"Expected list, got {type(input_ids)}")

        # Configure the global attention mask.
        sep_index = input_ids.index(2)  # Find the first [SEP] token in the input_ids.
        input_dict["global_attention_mask"] = [1] * (sep_index + 1) + [0] * (
            len(input_ids) - (sep_index + 1)
        )

        return {k: torch.tensor([v]) for k, v in input_dict.items()}
