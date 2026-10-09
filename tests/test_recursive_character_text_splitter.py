import unittest

from src.doc_intelligence.chunking.recursive_character_text_splitter import RecursiveCharacterTextSplitter


class TestRecursiveCharacterTextSplitter(unittest.TestCase):
    def test_instantiation(self) -> None:
        """Test that the splitter can be instantiated with default separators."""
        splitter = RecursiveCharacterTextSplitter()
        self.assertIsNotNone(splitter)


if __name__ == "__main__":
    unittest.main()
