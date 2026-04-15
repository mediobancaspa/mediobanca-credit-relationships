# Mediobanca Credit Network Visualization

Interactive network analysis of shareholder (soci) and guarantee (garanzie) relationships derived from Mediobanca archival credit data.

Open the interactive visualization:  
https://mediobancaspa.github.io/mediobanca-credit-relationships/

---
## Overview

This project presents a web-based environment for exploring reconstructed relationships between economic actors — individuals and companies — derived from archival credit records.

The network originates as a specific analytical layer of a broader graph representing the system of relationships inferred from the Mediobanca historical archive. While the general network captures the existence and structure of connections between entities, this graph is designed to qualify those connections by focusing on their nature.

In particular, it enables the distinction and exploration of:

- shareholder relationships (soci)
- guarantee relationships (garanzie)
- frequency and intensity of connections

By isolating these relational dimensions, the project provides a more granular interpretation of ties between entities, which are not explicitly differentiated in the general network.

The system integrates data processing, validation, and visualization into a single reproducible workflow.

---

## Data sources

The network is derived from a combination of structured and pre-processed data sources originating from the Mediobanca historical archive.

The primary input is a structured CSV dataset containing credit records. Each record includes:

- entities involved in credit operations  
- roles (client, shareholder, guarantor)  
- references to archival documentation  
- unique archival identifiers (IdxDams)  

In addition to the CSV, the workflow incorporates a pre-existing JSON representation of a broader network of relationships reconstructed from the same archival corpus. This general graph provides the initial relational structure from which specific subsets of connections — namely shareholder (soci) and guarantee (garanzie) relationships — are extracted.

The final network results from the integration of these sources:

- the CSV dataset, used to reconstruct and validate relationships  
- the intermediate JSON datasets derived from the general graph, used to preserve structural consistency and identifier continuity  

Through this process, the data are transformed into graph-ready JSON datasets used by the visualization layer.

---

## Data model

The graph is represented as a set of directed edges between entities, derived as a typed subgraph of a broader network of relationships reconstructed from the Mediobanca archival corpus.

While the general network encodes the existence of connections between entities, this model explicitly qualifies those connections by isolating and structuring specific relational types, namely shareholder (soci) and guarantee (garanzie) links.

Each edge includes:

```json
{
  "source": "Entity A",
  "target": "Entity B",
  "weight": 3,
  "documents": [...],
  "idxdams": [...]
}
```

Key characteristics:
- directed relationships (client → shareholder / guarantor), preserving the semantic orientation of roles
- projection of a broader relational graph into a typed subset focused on specific link categories
- aggregation of multiple records into weighted edges representing relational intensity
- preservation of document-level traceability through associated references
- continuity of identifiers across transformations, ensuring alignment with the original network structure

---

## Processing pipeline

The data processing workflow is implemented in Python and is structured as a multi-stage transformation pipeline combining extraction from an existing network representation and reconstruction from archival data.

### 1. Extraction from the general network

The process begins with a pre-existing JSON representation of a broader relational graph derived from the Mediobanca archival corpus.

From this graph, edges corresponding to specific relationship types are extracted:

- shareholder relationships (soci)  
- guarantee relationships (garanzie)  

During this step:

- edges are filtered by type  
- entity identifiers are resolved into normalized names  
- associated archival identifiers (IdxDams) are preserved  

This stage produces intermediate JSON datasets representing typed subsets of the original network.

### 2. Reconstruction from CSV data

The extracted edge sets are then compared against a structured CSV dataset of credit records.

In this phase:

- relationships are reconstructed from the CSV  
- edges are aggregated based on recurring co-occurrences  
- weights are computed as the frequency of observed relations  
- document references are associated to each edge  

The reconstruction process is not independent: it explicitly aligns with the previously extracted JSON datasets in order to:

- ensure consistency with the original network structure  
- reuse existing edge identifiers where possible  
- detect discrepancies between sources  

### 3. Consolidation and validation

The reconstructed edges are consolidated into final graph-ready datasets.

At the same time, validation reports are generated to assess:

- coverage of reconstructed relations with respect to the extracted network  
- reuse and consistency of identifiers (IdxDams)  
- structural integrity of the resulting graph  

The final output consists of enriched JSON files used directly by the visualization layer, along with diagnostic reports documenting the reconstruction process.

---

## Repository structure

```
assets/
  img/                # static images used in the interface

data/
  raw/                # source CSV dataset
  graph/              # graph datasets (intermediate and final JSON)
  reports/            # validation and rebuild reports

docs/                 # documentation

scripts/              # data processing pipeline (Python)
  json_maker.py       # extraction from general graph
  New_Json.py         # reconstruction and alignment with CSV
  Enrich_json.py      # enrichment with document references

index.html            # project entry point (GitHub Pages)
arc-diagram.html      # interactive arc diagram visualization

README.md             # project documentation
LICENSE               # license information
```

The `data/graph/` directory includes both intermediate datasets extracted from the general network and final rebuilt datasets used in the visualization.

---

## Visualization

The network is visualized through a static HTML interface designed for deployment via GitHub Pages.

The visualization adopts an arc diagram layout, where entities are arranged along a linear axis and relationships are represented as curved links. This configuration enables a compact and readable representation of dense relational structures, particularly suited for highlighting recurring connections and overlaps.

Main features:

- separation of relationship types, allowing users to explore shareholder (soci) and guarantee (garanzie) networks independently  
- interactive node selection, with dynamic highlighting of connected edges  
- inspection of individual relationships, including associated archival identifiers (IdxDams)  
- access to document-level references linked to each edge  
- visual encoding of relational intensity through edge aggregation  

The interface is implemented as a fully client-side application, requiring no backend infrastructure and ensuring portability and ease of deployment.
---

## How to use

### Online

Access the visualization via GitHub Pages:

https://mediobancaspa.github.io/mediobanca-credit-relationships/

### Local

Clone the repository and open:

```text
index.html
```

No server or additional dependencies are required.

---

## Reproducibility

The data processing pipeline is tailored to the structure and conventions of the Mediobanca archival dataset.

While the provided Python scripts allow the reconstruction of the graph from the original data, their direct reuse on different datasets is not guaranteed without adaptation.

In particular, the pipeline assumes:

- a specific organization of entities and roles within the source CSV  
- consistent formatting of entity names and relational fields  
- the availability of a pre-existing general network in JSON format for alignment and identifier continuity  

For datasets with different structures or conventions, adjustments may be required in order to:

- correctly parse entities and roles  
- redefine the logic used to extract and classify relationships  
- adapt the reconstruction and aggregation procedures  

The current implementation should therefore be understood as a reproducible workflow within a well-defined data context, rather than a fully general-purpose pipeline.

---

## License

MIT License
