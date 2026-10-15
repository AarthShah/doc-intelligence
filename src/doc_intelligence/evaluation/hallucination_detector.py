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
