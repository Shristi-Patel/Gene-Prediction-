from neo4j import GraphDatabase
import csv

# Neo4j connection settings
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "18052004"

# Snippet-generating Cypher queries
SNIPPET_QUERIES = [
    {
        "type": "gene_to_go",
        "query": """
        MATCH (g:Gene)-[r]->(go:GO_Term)
        WHERE type(r) IN ["INVOLVED_IN_BP", "INVOLVED_IN_CC", "INVOLVED_IN_MF", "ANNOTATED_TO"]
        RETURN
          "Gene " + g.symbol + " (" + g.name + ") " +
          CASE
            WHEN type(r) = "INVOLVED_IN_BP" OR go.namespace = "biological_process" THEN "is involved in biological process: "
            WHEN type(r) = "INVOLVED_IN_CC" OR go.namespace = "cellular_component" THEN "is located in cellular component: "
            WHEN type(r) = "INVOLVED_IN_MF" OR go.namespace = "molecular_function" THEN "performs molecular function: "
            ELSE "is annotated to GO term: "
          END +
          go.name + " (" + go.id + ")." AS snippet
        LIMIT 30000
        """
    },
    {
        "type": "go_hierarchy_all",
        "query": """
        MATCH (child:GO_Term)-[r]->(parent:GO_Term)
        WHERE type(r) IN ["IS_A"] OR type(r) STARTS WITH "RELATIONSHIP:" OR type(r) STARTS WITH "INTERSECTION_OF:"
        RETURN child.name + " (" + child.id + ") " +
               CASE
                   WHEN type(r) = "IS_A" THEN "is a"
                   WHEN type(r) STARTS WITH "RELATIONSHIP:" THEN toLower(replace(type(r), 'RELATIONSHIP:', ''))
                   WHEN type(r) STARTS WITH "INTERSECTION_OF:" THEN toLower(replace(type(r), 'INTERSECTION_OF:', ''))
                   ELSE type(r)
               END +
               " " + parent.name + " (" + parent.id + ")." AS snippet
        """
    },
    {
        "type": "go_is_a_only",
        "query": """
        MATCH (child:GO_Term)-[:IS_A]->(parent:GO_Term)
        RETURN child.name + " (" + child.id + ") is a subtype of " + parent.name + " (" + parent.id + ")." AS snippet
        """
    },
    {
        "type": "go_meaning",
        "query": """
        MATCH (go:GO_Term)
        WHERE go.name IS NOT NULL
        RETURN "GO term (" + go.id + ") means: " + go.name AS snippet
        """
    },
    {
        "type": "gene_annotation",
        "query": """
        MATCH (g:Gene)-[:ANNOTATED_TO]->(go:GO_Term)
        RETURN "Gene " + g.symbol + " is annotated to GO term " + go.name + " (" + go.id + ")." AS snippet
        """
    }
]

# Function to export all snippets to CSV
def export_snippets_to_csv(uri, user, password, queries, output_path):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session, open(output_path, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["source", "snippet"])
        for q in queries:
            print(f"Running query for: {q['type']}")
            result = session.run(q["query"])
            count = 0
            for record in result:
                writer.writerow([q["type"], record["snippet"]])
                count += 1
            print(f"✔ {count} snippets added for type: {q['type']}")
    driver.close()
    print(f"\n All snippets exported to: {output_path}")
    
# Run export
if __name__ == "__main__":
    export_snippets_to_csv(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD,
        queries=SNIPPET_QUERIES,
        output_path="knowledge_snippets.csv"
    )
