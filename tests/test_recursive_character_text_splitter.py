import unittest

from src.doc_intelligence.chunking.recursive_character_text_splitter import RecursiveCharacterTextSplitter


class TestRecursiveCharacterTextSplitter(unittest.TestCase):
    def test_instantiation(self) -> None:
        """Test that the splitter can be instantiated with default separators."""
        splitter = RecursiveCharacterTextSplitter()
        self.assertIsNotNone(splitter)

    def test_empty_string(self) -> None:
        """Test that splitting an empty string returns an empty list."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        chunks = splitter.split_text("")
        self.assertEqual(chunks, [])

    def test_separator_hierarchy(self) -> None:
        """Test that the splitter respects the hierarchy of separators."""
        text = "Paragraph one.\n\nParagraph two has more text."
        splitter = RecursiveCharacterTextSplitter(chunk_size=30, chunk_overlap=0)
        chunks = splitter.split_text(text)
        self.assertIn("Paragraph one.", chunks)
        self.assertIn("Paragraph two has more text.", chunks)

    def test_unbreakable_text(self) -> None:
        """Test handling of text that cannot be split further by separators."""
        text = "Supercalifragilisticexpialidocious"
        splitter = RecursiveCharacterTextSplitter(chunk_size=10, chunk_overlap=0)
        chunks = splitter.split_text(text)
        self.assertTrue(len(chunks) > 0)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 10)


if __name__ == "__main__":
    unittest.main()
