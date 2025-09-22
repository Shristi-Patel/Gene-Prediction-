from neo4j import GraphDatabase
import csv

# Neo4j connection details (adjust as needed)
uri = "bolt://localhost:7687"
username = "neo4j"
password = "18052004"  

driver = GraphDatabase.driver(uri, auth=(username, password))

# Output CSV path
output_csv = "gene_go_explanations.csv"

# Cypher query to find explanations
cypher_query = """
MATCH (g:Gene)-[:ANNOTATED_TO]->(term:GO_Term)
OPTIONAL MATCH path = (term)-[
  :IS_A |
  :RELATIONSHIP:PART_OF |
  :RELATIONSHIP:ENDS_DURING |
  :RELATIONSHIP:HAPPENS_DURING |
  :RELATIONSHIP:HAS_PART |
  :RELATIONSHIP:REGULATES |
  :RELATIONSHIP:OCCURS_IN |
  :RELATIONSHIP:POSITIVELY_REGULATES |
  :RELATIONSHIP:NEGATIVELY_REGULATES |
  :INTERSECTION_OF |
  :INTERSECTION_OF:PART_OF |
  :INTERSECTION_OF:HAPPENS_DURING |
  :INTERSECTION_OF:HAS_PART |
  :INTERSECTION_OF:NEGATIVELY_REGULATES |
  :INTERSECTION_OF:OCCURS_IN |
  :INTERSECTION_OF:POSITIVELY_REGULATES |
  :INTERSECTION_OF:REGULATES
*1..5
]->(parent:GO_Term)
WITH g.name AS gene, term.name AS direct_term, 
     COLLECT(DISTINCT parent.name) AS parent_terms, term.id AS term_id
RETURN gene, direct_term, parent_terms, term_id

"""
with driver.session() as session:
    results = session.run(cypher_query)

    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Gene", "GO_ID", "Explanation"])

        for record in results:
            gene = record["gene"]
            direct_term = record["direct_term"]
            go_id = record["term_id"]
            parent_terms = record["parent_terms"]

            if parent_terms:
                explanation = (
                    f"Gene {gene} is involved in {parent_terms[0]} because it is annotated to "
                    f"{direct_term}, which is part of the GO term hierarchy."
                )
            else:
                explanation = (
                    f"Gene {gene} is annotated to {direct_term} ({go_id})."
                )

            writer.writerow([gene, go_id, explanation])

print(f"Explanations saved to: {output_csv}")
