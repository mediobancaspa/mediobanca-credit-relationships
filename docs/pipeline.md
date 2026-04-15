# Processing Pipeline

This document describes the data processing workflow used to construct the network.

---

## Overview

The pipeline combines extraction from a general network representation with reconstruction from archival CSV data.

---

## Step 1 — Extraction from general network

**Input**

- `updated-graph-data-final.json`

**Output**

- `soci_edges_by_name_with_idxdams.json`
- `garanzie_edges_by_name_with_idxdams.json`

**Process**

- filtering edges by type (soci / garanzie)  
- resolving entity identifiers to names  
- preserving IdxDams references  

---

## Step 2 — Reconstruction from CSV

**Input**

- CSV dataset of credit records  
- extracted JSON datasets  

**Output**

- rebuilt JSON datasets  
- validation reports  

**Process**

- reconstruction of relationships from CSV  
- aggregation of edges  
- alignment with extracted network  
- reuse of identifiers  
- detection of inconsistencies  

---

## Step 3 — Consolidation

Final datasets are produced:

- `*_rebuilt.json`  
- validation reports  

These datasets are used directly by the visualization layer.

---

## Notes

The pipeline is tailored to the structure of the Mediobanca dataset and may require adaptation for different data sources.
