import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Assume LLMClient is defined elsewhere and has a method like generate(prompt: str) -> str
# For example:
# class LLMClient:
#     def generate(self, prompt: str) -> str:
#         # Implementation to call an LLM API
#         pass

PROMPT_TEMPLATE = """
Given the following query, generate a hypothetical document that answers it.
Query: "{query}"
Hypothetical Document:
"""


class HyDEGenerator:
    """
    Generates hypothetical documents based on a query using an LLM.

    This class leverages a language model to generate a document that is
    hypothetically relevant to a given query. This hypothetical document
    can then be embedded and used for retrieval, potentially improving
    search results by bridging the gap between query and document embeddings.

    Attributes:
        llm_client (object): An instance of an LLM client providing a ``generate`` method.
        prompt_template (str): The template string used to format prompts for the LLM.
    """

    DEFAULT_PROMPT_TEMPLATE = """
    Given the following query, generate a hypothetical document that answers it.
    Query: "{query}"
    Hypothetical Document:
    """

    def __init__(
        self,
        llm_client: object,  # Use duck typing as LLMClient is hypothetical
        prompt_template: Optional[str] = PROMPT_TEMPLATE,
    ):
        """
        Initializes the HyDEGenerator.

        Args:
            llm_client: An instance of an LLM client capable of generating text.
                Must implement a callable ``generate(prompt: str) -> str`` method.
            prompt_template: An optional custom prompt template. If not provided,
                a default template is used. The template must contain the placeholder "{query}".

        Raises:
            TypeError: If ``llm_client`` does not have a callable ``generate`` method.
        """
        if not hasattr(llm_client, "generate") or not callable(getattr(llm_client, "generate")):
            raise TypeError("llm_client must have a callable 'generate' method.")

        self.llm_client = llm_client
        self.prompt_template = prompt_template or self.DEFAULT_PROMPT_TEMPLATE

    def generate_hypothetical_document(self, query: str) -> str:
        """
        Generates a hypothetical document for the given query.

        Args:
            query: The input query string for which to generate a hypothetical document.

        Returns:
            A stripped string representing the generated hypothetical document.

        Raises:
            ValueError: If the prompt template does not contain the ``{query}`` placeholder,
                or if the LLM client encounters a connection/timeout error or fails to generate
                a valid response.
            TypeError: If the LLM client response is not a string.
        """
        if "{query}" not in self.prompt_template:
            raise ValueError("Prompt template must contain the '{query}' placeholder.")

        formatted_prompt = self.prompt_template.format(query=query)

        try:
            hypothetical_doc = self.llm_client.generate(formatted_prompt)
            if not isinstance(hypothetical_doc, str):
                raise TypeError("LLM client response must be a string.")
        except (ConnectionError, TimeoutError) as e:
            logger.error("Connection or timeout error while generating hypothetical document for query '%s': %s", query, e)
            raise ValueError(f"LLM service connection/timeout error for query: '{query}'.") from e
        except Exception as e:
            logger.error("Failed to generate hypothetical document for query '%s': %s", query, e)
            raise ValueError(f"Failed to generate hypothetical document for query: '{query}'. Error: {e}") from e

        # Basic cleaning: remove leading/trailing whitespace
        cleaned_doc = hypothetical_doc.strip()
        if not cleaned_doc:
            logger.warning("Generated hypothetical document was empty for query '%s'.", query)
        return cleaned_doc

    def generate(self, query: str) -> str:
        """
        Generates a hypothetical document for the given query.

        This is a convenience method that delegates directly to
        ``generate_hypothetical_document``.

        Args:
            query: The input query string.

        Returns:
            A string representing the generated hypothetical document.

        Raises:
            ValueError: If the prompt template is invalid or if the LLM fails
                        to generate a response.
        """
        try:
            return self.generate_hypothetical_document(query)
        except Exception as e:
            logger.error("Error in generate convenience method for query '%s': %s", query, e)
            raise

# Example usage (assuming LLMClient is defined and instantiated)
# llm = LLMClient(...)
# hyde_generator = HyDEGenerator(llm_client=llm)
# hypothetical_document = hyde_generator.generate_hypothetical_document("What is the capital of France?")
# print(hypothetical_document)
