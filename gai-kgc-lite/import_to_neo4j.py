import argparse
import json
import os
from pathlib import Path
from typing import Any
from typing import Iterator

from tqdm import tqdm


DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parent / "output"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def iter_entities(entities_data: dict) -> Iterator[tuple[str, str, str]]:
    for doc_path, entity_dict in entities_data.items():
        doc_name = Path(doc_path).name
        for entity_type, entities in entity_dict.items():
            for entity in entities:
                yield doc_name, entity_type, entity


def iter_triples(triples_data: dict) -> Iterator[tuple[str, str, str, str]]:
    for doc_path, triples in triples_data.items():
        doc_name = Path(doc_path).name
        for triple in triples:
            if len(triple) >= 3:
                yield doc_name, triple[0], triple[1], triple[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import the public GAI-KGC Lite extraction artifacts into Neo4j."
    )
    parser.add_argument(
        "--output-path",
        default=str(DEFAULT_OUTPUT_PATH),
        help="Directory containing all_entities.json and all_triples.json.",
    )
    parser.add_argument(
        "--uri",
        default=os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687"),
        help="Neo4j URI.",
    )
    parser.add_argument(
        "--username",
        default=os.getenv("NEO4J_USERNAME", "neo4j"),
        help="Neo4j username.",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("NEO4J_PASSWORD", ""),
        help="Neo4j password. Prefer passing via environment variable.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and count the artifacts without connecting to Neo4j.",
    )
    return parser.parse_args()


def summarize(entities_data: dict, triples_data: dict) -> dict[str, int]:
    entity_count = sum(1 for _ in iter_entities(entities_data))
    relation_count = sum(1 for _ in iter_triples(triples_data))
    document_count = len(set(entities_data.keys()) | set(triples_data.keys()))
    return {
        "documents": document_count,
        "entities": entity_count,
        "relations": relation_count,
    }


def import_to_neo4j(
    output_path: Path,
    uri: str,
    username: str,
    password: str,
    dry_run: bool = False,
) -> None:
    entities_path = output_path / "all_entities.json"
    triples_path = output_path / "all_triples.json"

    if not entities_path.exists() or not triples_path.exists():
        missing = [str(path) for path in [entities_path, triples_path] if not path.exists()]
        raise FileNotFoundError(f"Missing required artifact files: {', '.join(missing)}")

    entities_data = load_json(entities_path)
    triples_data = load_json(triples_path)
    summary = summarize(entities_data, triples_data)

    print("Artifact summary:")
    print(f"- documents: {summary['documents']}")
    print(f"- entities: {summary['entities']}")
    print(f"- relations: {summary['relations']}")

    if dry_run:
        print("Dry run enabled. Skipping database import.")
        return

    if not password:
        raise ValueError("Neo4j password is empty. Set NEO4J_PASSWORD or pass --password.")

    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        with driver.session() as session:
            session.run(
                "CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT entity_type_unique IF NOT EXISTS FOR (t:EntityType) REQUIRE t.name IS UNIQUE"
            )

        entity_rows = list(iter_entities(entities_data))
        with driver.session() as session:
            progress = tqdm(entity_rows, desc="Import entities")
            for doc_name, entity_type, entity_name in progress:
                session.run(
                    """
                    MERGE (e:Entity {name: $entity_name})
                    SET e.source_doc = $doc_name
                    MERGE (t:EntityType {name: $entity_type})
                    MERGE (e)-[:IS_TYPE_OF]->(t)
                    """,
                    entity_name=entity_name,
                    entity_type=entity_type,
                    doc_name=doc_name,
                )

        triple_rows = list(iter_triples(triples_data))
        with driver.session() as session:
            progress = tqdm(triple_rows, desc="Import relations")
            for doc_name, head, relation, tail in progress:
                session.run(
                    """
                    MERGE (h:Entity {name: $head})
                    MERGE (t:Entity {name: $tail})
                    MERGE (h)-[r:RELATION {type: $relation_type}]->(t)
                    SET r.source_doc = $doc_name
                    """,
                    head=head,
                    tail=tail,
                    relation_type=relation,
                    doc_name=doc_name,
                )

        print("Neo4j import completed successfully.")
        print("Suggested Cypher:")
        print("MATCH (n:Entity) RETURN n LIMIT 10;")
        print("MATCH (a:Entity)-[r:RELATION]->(b:Entity) RETURN a,r,b LIMIT 10;")
    finally:
        driver.close()


def main() -> None:
    args = parse_args()
    import_to_neo4j(
        output_path=Path(args.output_path),
        uri=args.uri,
        username=args.username,
        password=args.password,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
