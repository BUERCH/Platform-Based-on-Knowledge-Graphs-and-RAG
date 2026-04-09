import json
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ENTITIES_PATH = OUTPUT_DIR / "all_entities.json"
TRIPLES_PATH = OUTPUT_DIR / "all_triples.json"
SUMMARY_PATH = OUTPUT_DIR / "docs_summary.json"
REPORT_PATH = OUTPUT_DIR / "gai_kgc_public_demo_report.md"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_report() -> str:
    entities_data = load_json(ENTITIES_PATH)
    triples_data = load_json(TRIPLES_PATH)
    summary_data = load_json(SUMMARY_PATH) if SUMMARY_PATH.exists() else {}

    entity_type_counter: Counter[str] = Counter()
    relation_counter: Counter[str] = Counter()
    per_doc_entities: dict[str, int] = defaultdict(int)
    per_doc_relations: dict[str, int] = defaultdict(int)

    for doc_path, entity_dict in entities_data.items():
        doc_name = Path(doc_path).name
        for entity_type, entities in entity_dict.items():
            entity_type_counter[entity_type] += len(entities)
            per_doc_entities[doc_name] += len(entities)

    for doc_path, triples in triples_data.items():
        doc_name = Path(doc_path).name
        for triple in triples:
            if len(triple) >= 3:
                relation_counter[triple[1]] += 1
                per_doc_relations[doc_name] += 1

    doc_names = sorted(set(per_doc_entities.keys()) | set(per_doc_relations.keys()))
    total_entities = sum(per_doc_entities.values())
    total_relations = sum(per_doc_relations.values())

    lines = [
        "# GAI-KGC Lite Public Demo Report",
        "",
        "## Summary",
        "",
        f"- Documents: {len(doc_names)}",
        f"- Entities: {total_entities}",
        f"- Relations: {total_relations}",
        "",
        "## Top Entity Types",
        "",
    ]

    for entity_type, count in entity_type_counter.most_common(10):
        lines.append(f"- {entity_type}: {count}")

    lines.extend(["", "## Top Relations", ""])
    for relation, count in relation_counter.most_common(10):
        lines.append(f"- {relation}: {count}")

    lines.extend(["", "## Per-document Statistics", ""])
    for doc_name in doc_names:
        lines.append(
            f"- {doc_name}: {per_doc_entities.get(doc_name, 0)} entities, {per_doc_relations.get(doc_name, 0)} relations"
        )

    if summary_data:
        lines.extend(["", "## Sample Document Summaries", ""])
        for doc_name, summary in list(summary_data.items())[:5]:
            clean_summary = str(summary).replace("\n", " ").strip()
            lines.append(f"- {Path(doc_name).name}: {clean_summary[:180]}")

    lines.extend(
        [
            "",
            "## Public Release Note",
            "",
            "- This report is generated from the sanitized public demo artifacts only.",
            "- Full industrial corpora, private prompts, and thesis evaluation settings are intentionally omitted.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    missing_files = [str(path) for path in [ENTITIES_PATH, TRIPLES_PATH] if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing required artifact files: {', '.join(missing_files)}")

    report = build_report()
    REPORT_PATH.write_text(report, encoding="utf-8")
    print(f"Public demo report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
