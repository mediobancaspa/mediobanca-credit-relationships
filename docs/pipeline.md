# Processing Pipeline

This document describes the data processing workflow used to construct the network, starting from archival records and ending with the datasets used in the visualization layer.

The pipeline is designed to ensure:

- traceability from archival sources  
- consistency between extracted and reconstructed relationships  
- preservation of archival identifiers (IdxDams)  
- reproducibility of the network structure  

---

## Overview

The workflow is composed of three main phases:

1. extraction from a general graph representation  
2. reconstruction from archival CSV data  
3. consolidation and validation  

These phases are not redundant: they serve complementary purposes. The extraction phase provides a structured baseline, while the reconstruction phase ensures that the network faithfully reflects the underlying archival records.

---

## Step 1 — Extraction from general network

### Input

- `updated-graph-data-final.json`

This file represents a fully constructed graph (nodes + edges) in a generic format, where:

- nodes are identified by internal IDs and include metadata (name, codice = IdxDams)  
- edges include type, weight, and references to source/target node IDs  

### Process

This phase is implemented in:

- `New_Json.py` :contentReference[oaicite:0]{index=0}  

The script performs the following operations:

1. **Node mapping**

   - builds a dictionary `node_id → {name, codice}`  
   - resolves internal IDs into human-readable entity names  
   - preserves the archival identifier (`codice`, i.e. IdxDams)

2. **Edge filtering by type**

   - iterates over all elements in the graph  
   - selects only elements with `source` and `target`  
   - separates edges into:
     - `Soci_entities`
     - `Garanzie_entities`

3. **Edge normalization**

   For each edge:
   - replaces node IDs with entity names  
   - keeps original IDs (`source_id`, `target_id`)  
   - attaches IdxDams identifiers to both endpoints  

4. **Dataset separation**

   - edges are written into two distinct outputs:
     - `soci_edges_by_name_with_idxdams.json`  
     - `garanzie_edges_by_name_with_idxdams.json`  

### Output

- `soci_edges_by_name_with_idxdams.json`  
- `garanzie_edges_by_name_with_idxdams.json`  

### Purpose

This step transforms a **technical graph representation** into **readable, entity-based datasets** while preserving archival identifiers. It creates a clean baseline that can be inspected independently of the visualization.

---

## Step 2 — Reconstruction from CSV

### Input

- CSV dataset of credit records  
- extracted JSON datasets from Step 1  

The CSV represents the **primary archival source**, containing raw relational information derived from credit files.

### Process

This phase is implemented through:

- `json_maker.py`  
- `Enrich_json.py`  

The reconstruction process includes:

1. **Parsing of CSV records**

   - extraction of entities from structured fields  
   - normalization of names  
   - handling of multi-entity cells  

2. **Reconstruction of relationships**

   - identification of:
     - shareholder relationships (soci)  
     - guarantee relationships (garanzie)  
   - generation of directed edges (`source → target`)  

3. **Aggregation of edges**

   - multiple occurrences of the same relationship are merged  
   - edge weight is computed as:
     - number of occurrences across records  
     - number of associated documents  

4. **Attachment of archival references**

   - each edge is enriched with:
     - document references  
     - IdxDams identifiers  

5. **Alignment with extracted graph**

   The reconstructed edges are compared with those extracted in Step 1:

   - exact matches are identified  
   - existing edge IDs are reused when possible  
   - new IDs are generated for unmatched edges  
   - inconsistencies are detected  

This process is explicitly documented in validation reports such as:

- `soci_rebuild_report.json` :contentReference[oaicite:1]{index=1}  
- `garanzie_rebuild_report.json`  

### Output

- `soci_edges_by_name_with_idxdams_rebuilt.json`  
- `garanzie_edges_by_name_with_idxdams_rebuilt.json`  
- validation reports  

### Purpose

This step ensures that the network is not only structurally valid, but also **faithful to the archival evidence**. It transforms the CSV into a network representation and verifies its consistency against the previously extracted graph.

---

## Step 3 — Consolidation

### Input

- rebuilt JSON datasets  
- validation reports  

### Process

This phase consolidates the reconstructed data into the final datasets used by the visualization:

1. **Final edge validation**

   - ensures all edges have:
     - valid source/target  
     - weight  
     - document references  

2. **Consistency checks**

   From the reports:

   - comparison between existing and rebuilt edges  
   - identification of unmatched edges  
   - verification of document coverage  

   Example (Soci dataset):

   - total edges: 1813  
   - reused IDs: 1005  
   - new edges: 808  
   - edges with documents: 100% :contentReference[oaicite:2]{index=2}  

3. **Final dataset preparation**

   - datasets are structured for direct use in the HTML visualization  
   - no further transformation is required client-side  

### Output

- `soci_edges_by_name_with_idxdams_rebuilt.json`  
- `garanzie_edges_by_name_with_idxdams_rebuilt.json`  

These are the datasets loaded by the visualization layer.

---

## Role of IdxDams identifiers

Throughout the pipeline, particular attention is given to the preservation of IdxDams identifiers:

- extracted from node metadata in Step 1  
- propagated and aligned during reconstruction  
- attached to both endpoints of each edge  

This ensures that every relationship in the graph can be traced back to archival records, enabling integration with document retrieval systems.

---

## Notes

The pipeline is tailored to the structure of the Mediobanca archival dataset, particularly:

- the presence of structured credit records  
- the availability of entity identifiers (IdxDams)  
- the distinction between shareholder and guarantee relationships  

Adapting this pipeline to other datasets would require:

- redefining entity extraction rules  
- adjusting normalization procedures  
- revising alignment and validation logic  
