import argparse
import json
import os
from pathlib import Path
from typing import Any

import networkx as nx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a lightweight centrality analysis on the public GAI-KGC Lite graph."
    )
    parser.add_argument(
        "--uri",
        default=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
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
        help="Neo4j password.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of top entities to print.",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional JSON output path.",
    )
    return parser.parse_args()


def build_graph(driver: Any) -> tuple[nx.Graph, dict[str, str]]:
    graph = nx.Graph()
    id_to_name: dict[str, str] = {}

    with driver.session() as session:
        node_result = session.run(
            """
            MATCH (n)
            RETURN elementId(n) AS element_id, coalesce(n.name, elementId(n)) AS name
            """
        )
        for record in node_result:
            node_id = record["element_id"]
            id_to_name[node_id] = record["name"]
            graph.add_node(node_id)

        edge_result = session.run(
            """
            MATCH (a)-[r]->(b)
            RETURN elementId(a) AS source, elementId(b) AS target, coalesce(r.type, type(r)) AS relation
            """
        )
        for record in edge_result:
            graph.add_edge(
                record["source"],
                record["target"],
                relation=record["relation"],
            )

    return graph, id_to_name


def analyze(uri: str, username: str, password: str, top_k: int, output: str = "") -> None:
    if not password:
        raise ValueError("Neo4j password is empty. Set NEO4J_PASSWORD or pass --password.")

    from neo4j import GraphDatabase

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        graph, id_to_name = build_graph(driver)
    finally:
        driver.close()

    pagerank_scores = nx.pagerank(graph) if graph.number_of_nodes() else {}
    top_nodes = sorted(pagerank_scores.items(), key=lambda item: item[1], reverse=True)[:top_k]

    result = [
        {
            "node_id": node_id,
            "name": id_to_name.get(node_id, node_id),
            "pagerank": round(score, 6),
        }
        for node_id, score in top_nodes
    ]

    print(f"Loaded graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")
    print("Top nodes by PageRank:")
    for item in result:
        print(f"- {item['name']}: {item['pagerank']}")

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                {
                    "node_count": graph.number_of_nodes(),
                    "edge_count": graph.number_of_edges(),
                    "top_nodes": result,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"Analysis written to {output_path}")


def main() -> None:
    args = parse_args()
    analyze(
        uri=args.uri,
        username=args.username,
        password=args.password,
        top_k=args.top_k,
        output=args.output,
    )


if __name__ == "__main__":
    main()
