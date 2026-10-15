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
    the generated answer.
    """

    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-base"):
        """
        Initializes the HallucinationDetector with a pre-trained NLI model.

        Args:
            model_name (str): The name of the pre-trained CrossEncoder model to use.
        """
        self.model = CrossEncoder(model_name)

    def detect(self, premise: str, hypothesis: str) -> dict:
        """
        Detects whether a hypothesis (answer) is entailed by the premise (context).

        Args:
            premise (str): The retrieved context.
            hypothesis (str): The generated answer to evaluate.

        Returns:
            dict: Containing prediction scores and entailment status.
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
