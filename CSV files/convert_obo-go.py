import csv
from pronto import Ontology

obo_file = "go.obo"
onto = Ontology(obo_file)


def parse_obo_tags(obo_path):
    term_tags = {}
    current_id = None
    inside_term = False
    with open(obo_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "[Term]":
                inside_term = True
                current_id = None
                continue
            elif line == "":
                inside_term = False
                current_id = None
                continue
            if not inside_term:
                continue
            if ":" not in line:
                continue
            tag, value = line.split(":", 1)
            tag = tag.strip()
            value = value.strip()
            if tag == "id":
                current_id = value
                term_tags[current_id] = {}
            if current_id:
                term_tags[current_id].setdefault(tag, []).append(value)
    return term_tags

# Parse all raw tags from the OBO file
raw_tags = parse_obo_tags(obo_file)


term_file = "go_terms.csv"
rel_file = "go_relationships.csv"

with open(term_file, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow([
        "id", "name", "namespace", "synonyms", "alt_id",
        "is_obsolete", "replaced_by", "xrefs", "subsets",
        "created_by", "creation_date", "consider",
        "definition", "comment", "property_value"
    ])
    
    for term in onto.terms():
        ID = term.id
        NAME = term.name or ""
        NAMESPACE = term.namespace or ""
        DEFINITION = term.definition or ""
        COMMENT = term.comment or ""
        IS_OBSOLETE = str(term.obsolete)
        SYNONYMS = "; ".join([s.description for s in term.synonyms])
        raw = raw_tags.get(ID, {})  # FIX: use ID not id
        raw_xrefs = raw.get("xref", [])
        xref_entries = []

        for x in raw_xrefs:
            parts = x.split(" ", 1)
            ref_id = parts[0].strip()
            if len(parts) == 2:
                desc = parts[1].strip().strip('"')
                entry = f"{ref_id} | {desc}"
            else:
                entry = ref_id
            xref_entries.append(entry)

        XREFS = "; ".join(xref_entries)

        SUBSETS = "; ".join(term.subsets)

        ALT_ID = "; ".join(raw.get("alt_id", []))
        PROP_VAL = "; ".join(raw.get("property_value", []))
        CONSIDER = "; ".join(raw.get("consider", []))
        CREATED_BY = "; ".join(raw.get("created_by", []))
        CREATION_DATE = "; ".join(raw.get("creation_date", []))
        REPLACED_BY = "; ".join(raw.get("replaced_by", [])) if term.obsolete else ""

        writer.writerow([
            ID, NAME, NAMESPACE, SYNONYMS, ALT_ID,
            IS_OBSOLETE, REPLACED_BY, XREFS, SUBSETS,
            CREATED_BY, CREATION_DATE, CONSIDER,
            DEFINITION, COMMENT, PROP_VAL
        ])

# --- Write Relationships ---
with open(rel_file, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["source", "relation", "target", "target_name"])

    for term in onto.terms():
        source = term.id

        # is_a relationships
        for parent in term.superclasses(distance=1):
            if parent.id != source:
                target = parent.id
                target_name = onto.get(target).name if onto.get(target) else ""
                writer.writerow([source, "is_a", target, target_name])

        # Raw tags: intersection_of and relationship (FIXED)
        raw = raw_tags.get(source, {})
        for tag in ["intersection_of", "relationship"]:
            for line in raw.get(tag, []):
                line = line.split("!")[0].strip()  
                parts = line.split(None, 1)  

                if len(parts) == 1:
                    target = parts[0]
                    relation = tag
                elif len(parts) == 2:
                    inner_relation, target = parts
                    relation = f"{tag}:{inner_relation}"
                else:
                    continue  
                target_name = onto.get(target).name if onto.get(target) else ""
                writer.writerow([source, relation, target, target_name])
