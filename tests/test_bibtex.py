import unittest

from paper_hs.bibtex import parse_bibtex, is_plausible_doi


class BibtexTests(unittest.TestCase):
    def test_parse_basic_entry(self):
        text = """
        @article{key2024,
          title={A Paper},
          author={Doe, Jane and Smith, John},
          year={2024},
          doi={https://doi.org/10.1234/ABC.1}
        }
        """
        entries, dups = parse_bibtex(text)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].key, "key2024")
        self.assertEqual(entries[0].doi, "10.1234/abc.1")
        self.assertEqual(entries[0].year, "2024")
        self.assertFalse(dups)

    def test_doi_pattern(self):
        self.assertTrue(is_plausible_doi("10.1145/123456"))
        self.assertFalse(is_plausible_doi("not-a-doi"))


if __name__ == "__main__":
    unittest.main()
