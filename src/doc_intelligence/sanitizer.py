import re

class DocumentSanitizer:
    """
    Redacts personally identifiable information (PII) such as emails, phone numbers,
    and API keys from text content using regular expressions.
    """

    # Regex for common email patterns
    EMAIL_PATTERN = re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    )
    # Regex for common phone number patterns (US-centric, but covers many international formats)
    # Allows for various separators like spaces, hyphens, periods, or no separator.
    # Covers formats like (123) 456-7890, 123-456-7890, 123.456.7890, +1 123 456 7890 etc.
    PHONE_PATTERN = re.compile(
        r"(?:\+?\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}"
    )
    # Regex for common API key patterns (example: 32-char alphanumeric, potentially with hyphens)
    # This is a generic pattern; specific API keys might need more targeted regex.
    # Examples: AWS, Stripe, etc.
    API_KEY_PATTERN = re.compile(
        r"(?:[A-Za-z0-9+/]{20,40}|sk-[A-Za-z0-9]{32,})"  # Generic Base64-like or 'sk-' prefixed keys
    )

    def sanitize(self, text: str) -> str:
        """
        Redacts PII from the input text.

        Args:
            text: The input string potentially containing PII.

        Returns:
            The sanitized string with PII replaced by placeholders.
        """
        # Redact emails
        text = self.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", text)
        # Redact phone numbers
        text = self.PHONE_PATTERN.sub("[REDACTED_PHONE]", text)
        # Redact API keys
        text = self.API_KEY_PATTERN.sub("[REDACTED_API_KEY]", text)

        return text
