# Limitations

This document outlines the main limitations of the current model, the data processing pipeline, and the visualization layer. These limitations should be considered when interpreting the network and its analytical outputs.

---

## Data dependency

The entire pipeline is strongly dependent on the structure and quality of the source data.

In particular, it relies on:

- the internal structure of the CSV dataset of credit records  
- the consistency and completeness of entity naming across records  
- the availability of a pre-existing general network (`updated-graph-data-final.json`)  

Any inconsistency in these inputs directly propagates into the graph.

The model does not currently include automated mechanisms for detecting or correcting all such issues at the source level.

---

## Entity normalization

Entity normalization constitutes a foundational component of the current pipeline, but also a critical limitation in terms of reproducibility.

The workflow relies on the availability of a structured and curated system of authority files developed by the Mediobanca Historical Archive. This work ensures that:

- entities are identified in a consistent and controlled manner across records  
- naming conventions are standardized  
- each entity is associated with a stable archival identifier (IdxDams)  

This level of normalization enables:

- reliable aggregation of relationships across multiple documents  
- coherent construction of the network structure  
- direct traceability between graph entities and archival records  

However, this strength introduces a significant constraint.

The pipeline implicitly assumes the existence of:

- a well-defined authority control system  
- consistent entity identifiers across datasets  
- prior archival standardization work  

In the absence of such conditions, the same approach would encounter substantial difficulties:

- entity matching would become ambiguous and error-prone  
- relationships could be incorrectly split or merged  
- the overall network structure would lose coherence  

In particular, without authority files:

- string-based matching would be insufficient to guarantee identity resolution  
- additional layers of disambiguation (manual or algorithmic) would be required  
- the reliability of the resulting graph would be significantly reduced  

Therefore, while entity normalization is a strength of the current implementation, it also represents a major barrier to generalization. Replicating the pipeline on other datasets would require comparable authority control systems or the development of robust entity resolution methodologies.
---

## Aggregation and loss of granularity

Edges are aggregated across multiple archival records.

This implies that:

- repeated occurrences of the same relationship are merged into a single edge  
- the **weight** of the edge represents frequency (number of occurrences / documents)  

While this improves readability and reduces graph complexity, it introduces important limitations:

- the **temporal dimension is lost** (no distinction between early and late relationships)  
- variations in the nature or context of the relationship are not preserved  
- individual document-level differences are flattened into a single quantitative measure  

The graph should therefore be interpreted as a **cumulative relational structure**, not as a sequence of events.

---

## Validation and alignment constraints

The alignment between extracted and reconstructed datasets is not perfect.

Validation reports show:

- partial reuse of existing edge identifiers  
- creation of new edges during reconstruction  
- presence of unmatched edges between datasets  

These discrepancies may arise from:

- differences in normalization  
- incomplete extraction in the original graph  
- structural differences between CSV-derived and pre-existing data  

Although the pipeline tracks and reports these inconsistencies, it does not automatically resolve them.

---

## Visualization constraints

The arc diagram provides an effective compact representation, but introduces limitations:

- dense regions with many overlapping arcs may reduce readability  
- long-distance connections may become visually cluttered  
- node ordering along the axis affects interpretability  

Furthermore:

- the layout is not optimized for community detection or clustering  
- the diagram emphasizes local adjacency rather than global structure  

The interactive features (zoom, hover, filtering) mitigate these issues, but do not eliminate them.

---

## Directionality and interpretation

The visualization encodes directionality relative to the selected node (above/below axis), but:

- this is a **context-dependent representation**, not a global orientation  
- the same edge may appear differently depending on which node is selected  

This means that:

- the graph does not provide a single fixed directional layout  
- interpretation requires awareness of the current selection context  

---

## Limited semantic depth

The graph encodes the existence and frequency of relationships, but not their full semantic content.

In particular:

- it does not distinguish between different types or strengths of relationships beyond frequency  
- it does not encode legal, contractual, or qualitative nuances  
- it does not model multi-layer or hierarchical dependencies  

As a result, the network should be interpreted as a **structural abstraction**, not as a complete representation of economic or institutional reality.

---

## Generalization

The pipeline is tailored to the Mediobanca archival dataset and reflects its specific characteristics:

- structured credit records  
- identifiable entities with archival identifiers (IdxDams)  
- well-defined categories of relationships (soci / garanzie)  

Applying the same pipeline to other datasets would require:

- redefining parsing and extraction logic  
- adapting normalization procedures  
- revising validation and alignment strategies  

The current implementation should therefore be considered **dataset-specific**, not fully generalizable.
