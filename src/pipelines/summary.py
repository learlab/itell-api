from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    TextClassificationPipeline,
)
import torch
from typing import Dict


class SummaryPipeline(TextClassificationPipeline):
    def __init__(self, model, *args, **kwargs):
    self.model_name = model    
        super().__init__(
            model=AutoModelForSequenceClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model),
            function_to_apply="None",
            device="cuda" if torch.cuda.is_available() else "cpu",
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

        # Configure the global attention mask only for longformer, not for deberta.
        if self.model_name in ["tiedaar/longformer-content-global", "tiedaar/longformer-wording-global"]: 
            sep_index = input_ids.index(2)       
            input_dict["global_attention_mask"] = [1] * (sep_index + 1) + [0] * (
                len(input_ids) - (sep_index + 1)
            )

        return {k: torch.tensor([v]) for k, v in input_dict.items()}
