from transformers import TextClassificationPipeline
import torch
from typing import Dict


class ScoringPipeline(TextClassificationPipeline):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def preprocess(self, inputs, **tokenizer_kwargs) -> Dict[torch.Tensor]:
        '''Only works with a single input, not a list of inputs.'''
        input_dict = self.tokenizer(inputs,
                                    return_tensors='pt',
                                    **tokenizer_kwargs)

        sep_index = input_dict['input_ids'].index(2)

        input_dict['global_attention_mask'] = torch.tensor(
            [1] * (sep_index + 1)
            + [0] * (len(input_dict['input_ids']) - (sep_index + 1))
        )

        return input_dict
