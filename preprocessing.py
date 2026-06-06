import pandas as pd
import os

# Load Data 
gene_go = pd.read_csv("gene_go_explanations.csv")
bp = pd.read_csv("GO_Biological_Process_2025.csv")
cc = pd.read_csv("GO_Cellular_Component_2025.csv")
mf = pd.read_csv("GO_Molecular_Function_2025.csv")
relationships = pd.read_csv("go_relationships.csv")
terms = pd.read_csv("go_terms.csv")

# Normalize column names
for df in [gene_go, bp, cc, mf, relationships, terms]:
    df.columns = [c.lower() for c in df.columns]

# Merge GO type data
go_data = pd.concat([bp, cc, mf], ignore_index=True)

# Build lookup dictionaries
term_lookup = dict(zip(terms.get("go_id", []), terms.get("name", [])))

# relationships.csv - "source","target"
relationship_lookup = {}
if "source" in relationships.columns and "target" in relationships.columns:
    relationship_lookup = relationships.groupby("source")["target"].apply(list).to_dict()

#  Build Knowledge Chunks 
chunks = []

for _, row in gene_go.iterrows():
    gene = row.get("gene", "")
    go_id = row.get("go_id", "")
    go_name = term_lookup.get(go_id, "Unknown Term")

    # Relationships
    related_terms = relationship_lookup.get(go_id, [])
    related_texts = [f"{go_id} ({term_lookup.get(t, 'Unknown')}) -> {t}" for t in related_terms]

    # Chunk text
    chunk_text = f"""
    GENE: {gene}
    ASSOCIATED GO TERM: {go_name} ({go_id})
    RELATED TERMS: {', '.join(related_texts) if related_terms else 'None'}
    """
    chunks.append(chunk_text.strip())

# Save for embedding 
os.makedirs("processed_data", exist_ok=True)
with open("processed_data.txt", "w", encoding="utf-8") as f:
    for ch in chunks:
        f.write(ch + "\n\n")

print(f"Built {len(chunks)} knowledge chunks. Saved to processed_data.txt")
