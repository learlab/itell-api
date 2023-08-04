from transformers import (LongformerForSequenceClassification,
                          AutoTokenizer, TextClassificationPipeline)
import torch
from typing import Dict


class ScoringPipeline(TextClassificationPipeline):
    def __init__(self, model, *args, **kwargs):
        super().__init__(
            model=LongformerForSequenceClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(
                'allenai/longformer-base-4096'),
            function_to_apply='None',
            device='cuda' if torch.cuda.is_available() else 'cpu',
            *args,
            **kwargs
        )

    def preprocess(self, inputs, **tokenizer_kwargs
                   ) -> Dict[str, torch.Tensor]:
        '''Only works with a single input, not a list of inputs.'''
        input_dict = self.tokenizer(inputs, **tokenizer_kwargs)

        sep_index = input_dict['input_ids'].index(2)

        input_dict['global_attention_mask'] = (
            [1] * (sep_index + 1)
            + [0] * (len(input_dict['input_ids']) - (sep_index + 1))
            )

        return {k: torch.tensor([v]) for k, v in input_dict.items()}
