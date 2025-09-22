import csv
import re

input_file = "GO_Biological_Process_2025.txt"
output_file = "GO_Biological_Process_2025.csv"

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["geneset", "go_id", "gene"])  # header

    for line in infile:
        parts = line.strip().split("\t")
        if len(parts) >= 3:
            # Extract GO ID from the set name (e.g., "Process (GO:XXXXXXX)")
            geneset_raw = parts[0]
            match = re.search(r"\(GO:\d+\)", geneset_raw)
            go_id = match.group(0).strip("()") if match else "UNKNOWN"
            geneset = geneset_raw.replace(f" ({go_id})", "") if go_id != "UNKNOWN" else geneset_raw

            genes = parts[2:]
            for gene in genes:
                if gene.strip():
                    writer.writerow([geneset, go_id, gene.strip()])

import csv
import re

input_file = "GO_Cellular_Component_2025.txt"
output_file = "GO_Cellular_Component_2025.csv"

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["geneset", "go_id", "gene"]) 

    for line in infile:
        parts = line.strip().split("\t")
        if len(parts) >= 3:
            # Extract GO ID from the set name (e.g., "Process (GO:XXXXXXX)")
            geneset_raw = parts[0]
            match = re.search(r"\(GO:\d+\)", geneset_raw)
            go_id = match.group(0).strip("()") if match else "UNKNOWN"
            geneset = geneset_raw.replace(f" ({go_id})", "") if go_id != "UNKNOWN" else geneset_raw

            genes = parts[2:]
            for gene in genes:
                if gene.strip():
                    writer.writerow([geneset, go_id, gene.strip()])

import csv
import re

input_file = "GO_Molecular_Function_2025.txt"
output_file = "GO_Molecular_Function_2025.csv"

with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["geneset", "go_id", "gene"]) 

    for line in infile:
        parts = line.strip().split("\t")
        if len(parts) >= 3:
            # Extract GO ID from the set name (e.g., "Process (GO:XXXXXXX)")
            geneset_raw = parts[0]
            match = re.search(r"\(GO:\d+\)", geneset_raw)
            go_id = match.group(0).strip("()") if match else "UNKNOWN"
            geneset = geneset_raw.replace(f" ({go_id})", "") if go_id != "UNKNOWN" else geneset_raw

            genes = parts[2:]
            for gene in genes:
                if gene.strip():
                    writer.writerow([geneset, go_id, gene.strip()])
