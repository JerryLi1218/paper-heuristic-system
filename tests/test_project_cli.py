import tempfile
import unittest
from pathlib import Path

from paper_hs.project import init_project, install_skill
from paper_hs.citation_audit import audit_project


class ProjectTests(unittest.TestCase):
    def test_init_and_audit(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "src"
            src.mkdir()
            (src / "main.tex").write_text(r"""\documentclass{article}\begin{document}Hi \cite{missing}.\bibliography{refs}\end{document}""", encoding="utf-8")
            (src / "refs.bib").write_text("@article{present, title={X}, year={2024}}", encoding="utf-8")
            project = init_project(Path(td) / "paper", source=src)
            skill = install_skill(project)
            self.assertTrue((project / "paper_hs" / "state" / "claim_graph.json").exists())
            self.assertTrue((skill / "SKILL.md").exists())
            report = audit_project(project)
            codes = {i["code"] for i in report["issues"]}
            self.assertIn("cited_key_missing", codes)


if __name__ == "__main__":
    unittest.main()

class SourceCardAuditTests(unittest.TestCase):
    def test_source_card_title_mismatch_catches_wrong_bib_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "paper"
            root.mkdir()
            (root / "main.tex").write_text(r"We cite \cite{rightkey}.", encoding="utf-8")
            (root / "refs.bib").write_text("@article{rightkey, title={A Different Paper}, author={Doe, Jane}, year={2024}, doi={10.1234/example}}", encoding="utf-8")
            state = root / "paper_hs" / "state"
            state.mkdir(parents=True)
            (state / "source_cards.jsonl").write_text('{"source_id":"S001","bib_key":"rightkey","title":"The Intended Paper","year":"2024","doi":"10.1234/example","usage":"novelty contrast","verification_status":"verified"}\n', encoding="utf-8")
            report = audit_project(root)
            codes = {i["code"] for i in report["issues"]}
            self.assertIn("source_card_title_mismatch", codes)
