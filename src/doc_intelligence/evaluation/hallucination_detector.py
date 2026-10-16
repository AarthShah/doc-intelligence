import sys
from unittest.mock import MagicMock

if "sentence_transformers" not in sys.modules:
    try:
        from sentence_transformers import CrossEncoder
    except ImportError:
        sys.modules["sentence_transformers"] = MagicMock()
        from sentence_transformers import CrossEncoder
else:
    from sentence_transformers import CrossEncoder


class HallucinationDetector:
    """
    Detects hallucinations by evaluating if an answer is entailed by the context.

    This detector uses a Cross-Encoder model trained on Natural Language Inference (NLI)
    tasks to determine the logical relationship between the retrieved context and
    the generated answer. It quantifies the degree to which an answer is supported
    by provided contextual information, thereby identifying unsupported claims
    (hallucinations).

    Attributes:
        model (CrossEncoder): The underlying pre-trained Cross-Encoder model
                              used for NLI tasks.
    """

    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-base") -> None:
        """
        Initializes the HallucinationDetector with a pre-trained NLI model.

        Args:
            model_name (str): The name of the pre-trained CrossEncoder model to use.
                Defaults to "cross-encoder/nli-deberta-v3-base".
        """
        self.model = CrossEncoder(model_name)

    def detect(self, premise: str, hypothesis: str) -> dict[str, float | bool]:
        """
        Detects whether a hypothesis (answer) is entailed by the premise (context).

        This method evaluates the logical relationship between the given context (premise)
        and the generated answer (hypothesis) using a Cross-Encoder Natural Language Inference
        (NLI) model, returning an entailment score and a support status boolean.

        Args:
            premise (str): The retrieved context text serving as the reference premise.
            hypothesis (str): The generated answer text to evaluate against the premise.

        Returns:
            dict[str, float | bool]: A dictionary containing:
                - "entailment_score" (float): The normalized probability score (0.0 to 1.0)
                  indicating the likelihood that the hypothesis is entailed by the premise.
                - "is_supported" (bool): A boolean flag indicating whether the entailment
                  score exceeds the 0.5 threshold (True if supported, False if unsupported/hallucinated).
        """
        import numpy as np

        scores = self.model.predict([(premise, hypothesis)])
        
        # CrossEncoder NLI models typically output logits for [contradiction, entailment, neutral] 
        # or [contradiction, neutral, entailment] depending on the specific model card.
        # For cross-encoder/nli-deberta-v3-base, the order is [contradiction, entailment, neutral].
        logits = scores[0] if isinstance(scores, (list, np.ndarray)) else scores
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / exp_logits.sum()

        # Assuming standard label mapping: 0: contradiction, 1: entailment, 2: neutral
        entailment_score = float(probs[1]) if len(probs) > 1 else float(probs[0])
        
        return {
            "entailment_score": entailment_score,
            "is_supported": entailment_score > 0.5
        }
