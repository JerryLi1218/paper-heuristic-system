import unittest

from paper_hs.latex import extract_citation_keys_from_text


class LatexTests(unittest.TestCase):
    def test_extract_multiple_cites(self):
        text = r"""
        We cite \citep[see][p. 2]{a2020,b2021} and \textcite{c2022}.
        % \cite{ignored}
        """
        self.assertEqual(extract_citation_keys_from_text(text), {"a2020", "b2021", "c2022"})


if __name__ == "__main__":
    unittest.main()
