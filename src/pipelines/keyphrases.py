import random
import re

from spacy.tokens import Doc

from .nlp import nlp


def suggest_keyphrases(summary: Doc, chunks: list) -> tuple[list[str], list[str]]:
    """Return keyphrases that were included in the summary and suggests
    keyphrases that were not included.
    """
    included_keyphrases = list()
    candidate_keyphrases = list()
    weights = list()

    summary_lemmas = " ".join([t.lemma_.lower() for t in summary if not t.is_stop])

    for chunk in chunks:
        if not chunk.keyphrases:
            continue

        for keyphrase in nlp.pipe(chunk.keyphrases):
            keyphrase_lemmas = [t.lemma_ for t in keyphrase if not t.is_stop]
            keyphrase_included = re.search(
                re.escape(r" ".join(keyphrase_lemmas)),
                summary_lemmas,
                re.IGNORECASE,
            )
            if keyphrase_included:
                # keyphrase is included in summary
                included_keyphrases.append(keyphrase.text)
            elif keyphrase.text in candidate_keyphrases:
                # keyphrase has already been suggested
                # increase the weight of this keyphrase suggestion
                keyphrase_index = candidate_keyphrases.index(keyphrase.text)
                weights[keyphrase_index] += chunk.weight
            else:
                # New keyphrase suggestion
                candidate_keyphrases.append(keyphrase.text)
                # weight keyphrase suggestions by inverse focus time
                weights.append(chunk.weight)

    if len(candidate_keyphrases) <= 3:
        suggested_keyphrases = candidate_keyphrases
    else:
        suggested_keyphrases = random.choices(
            candidate_keyphrases,
            k=3,
            weights=weights,
        )

    return included_keyphrases, suggested_keyphrases
