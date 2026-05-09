from __future__ import annotations

import argparse
import json
from pathlib import Path

from .citation_audit import audit_project, citation_report_markdown
from .novelty import novelty_landscape, novelty_report_markdown
from .paths import reports_dir
from .project import init_project, install_skill
from .reporting import write_json, write_text
from .scan import scan_project, scan_markdown
from .source_cards import generate_source_cards, source_cards_report_markdown


def cmd_init(args: argparse.Namespace) -> int:
    root = init_project(args.project, title=args.title, venue=args.venue, source=args.source)
    if args.install_skill:
        install_skill(root, overwrite=args.overwrite_skill)
    print(f"Initialized Paper-HS project at {root}")
    return 0


def cmd_install_skill(args: argparse.Namespace) -> int:
    dst = install_skill(args.target, overwrite=args.overwrite)
    print(f"Installed paper_heuristic_system skill at {dst}")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    result = scan_project(args.project)
    out_dir = reports_dir(args.project)
    write_json(out_dir / "scan_report.json", result)
    write_text(out_dir / "scan_report.md", scan_markdown(result))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def cmd_source_cards(args: argparse.Namespace) -> int:
    report = generate_source_cards(args.project, overwrite=args.overwrite, cited_only=not args.all_entries)
    out_dir = reports_dir(args.project)
    write_json(out_dir / "source_cards_report.json", report)
    write_text(out_dir / "source_cards_report.md", source_cards_report_markdown(report))
    print(f"Wrote {report['output']}")
    return 0


def cmd_cite_check(args: argparse.Namespace) -> int:
    report = audit_project(args.project, online=args.online, mailto=args.mailto)
    out_dir = reports_dir(args.project)
    write_json(out_dir / "citation_report.json", report)
    write_text(out_dir / "citation_report.md", citation_report_markdown(report))
    print(f"Wrote {out_dir / 'citation_report.md'}")
    errors = report["summary"].get("errors", 0)
    return 2 if args.fail_on_error and errors else 0


def cmd_novelty_check(args: argparse.Namespace) -> int:
    report = novelty_landscape(args.project, query=args.query, online=args.online, rows=args.rows, mailto=args.mailto)
    out_dir = reports_dir(args.project)
    write_json(out_dir / "novelty_report.json", report)
    write_text(out_dir / "novelty_report.md", novelty_report_markdown(report))
    print(f"Wrote {out_dir / 'novelty_report.md'}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    scan = scan_project(args.project)
    cards = generate_source_cards(args.project, overwrite=False, cited_only=True)
    cite = audit_project(args.project, online=args.online, mailto=args.mailto)
    nov = novelty_landscape(args.project, query=args.query, online=args.online, rows=args.rows, mailto=args.mailto)
    out_dir = reports_dir(args.project)
    write_json(out_dir / "source_cards_report.json", cards)
    write_text(out_dir / "source_cards_report.md", source_cards_report_markdown(cards))
    write_json(out_dir / "scan_report.json", scan)
    write_text(out_dir / "scan_report.md", scan_markdown(scan))
    write_json(out_dir / "citation_report.json", cite)
    write_text(out_dir / "citation_report.md", citation_report_markdown(cite))
    write_json(out_dir / "novelty_report.json", nov)
    write_text(out_dir / "novelty_report.md", novelty_report_markdown(nov))
    summary = {
        "scan": {"tex_files": len(scan.get("tex_files", [])), "bib_files": len(scan.get("bib_files", []))},
        "source_cards": {"written": cards.get("source_cards", 0)},
        "citation": cite["summary"],
        "novelty": {"risk_level": nov.get("risk_level"), "nearest_works": len(nov.get("nearest_works", []))},
    }
    write_json(out_dir / "verification_summary.json", summary)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    errors = cite["summary"].get("errors", 0)
    return 2 if args.fail_on_error and errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paper-hs", description="Paper Heuristic System CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="Initialize an isolated paper project")
    p.add_argument("--project", required=True)
    p.add_argument("--title", default="Untitled Paper")
    p.add_argument("--venue", default="unknown")
    p.add_argument("--source", help="Existing paper file or directory to copy into manuscript/")
    p.add_argument("--install-skill", action="store_true")
    p.add_argument("--overwrite-skill", action="store_true")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("install-skill", help="Install the plug-and-play Codex skill into a paper project")
    p.add_argument("--target", required=True)
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_install_skill)

    p = sub.add_parser("scan", help="Scan manuscript files and citation keys")
    p.add_argument("--project", required=True)
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("source-cards", help="Generate conservative source_cards.jsonl rows from local BibTeX entries")
    p.add_argument("--project", required=True)
    p.add_argument("--all-entries", action="store_true", help="Include uncited BibTeX entries as source cards")
    p.add_argument("--overwrite", action="store_true", help="Rewrite existing cards from BibTeX fields")
    p.set_defaults(func=cmd_source_cards)

    p = sub.add_parser("cite-check", help="Verify LaTeX citations, BibTeX metadata, and source-card alignment")
    p.add_argument("--project", required=True)
    p.add_argument("--online", action="store_true", help="Use Crossref/OpenAlex metadata lookups for DOI verification")
    p.add_argument("--mailto", help="Email for polite API usage")
    p.add_argument("--fail-on-error", action="store_true")
    p.set_defaults(func=cmd_cite_check)

    p = sub.add_parser("novelty-check", help="Build a prior-art and novelty-risk map")
    p.add_argument("--project", required=True)
    p.add_argument("--query", help="Central idea or contribution statement")
    p.add_argument("--online", action="store_true", help="Use Crossref/OpenAlex/Semantic Scholar/arXiv metadata searches")
    p.add_argument("--rows", type=int, default=10)
    p.add_argument("--mailto", help="Email for polite API usage")
    p.set_defaults(func=cmd_novelty_check)

    p = sub.add_parser("verify", help="Run scan + citation + novelty checks")
    p.add_argument("--project", required=True)
    p.add_argument("--query", help="Central idea or contribution statement")
    p.add_argument("--online", action="store_true")
    p.add_argument("--rows", type=int, default=10)
    p.add_argument("--mailto", help="Email for polite API usage")
    p.add_argument("--fail-on-error", action="store_true")
    p.set_defaults(func=cmd_verify)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
