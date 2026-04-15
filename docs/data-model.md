# Data Model

This document defines both the structural data model and the visual logic underlying the Mediobanca Credit Network Visualization, with specific focus on the arc diagram representation of shareholder (*soci*) and guarantee (*garanzie*) relationships.

---

## Overview

The network is modeled as a directed graph where nodes represent economic actors and edges represent reconstructed relationships derived from archival credit records.

This graph is a specialized projection of a broader relational network and is designed to explicitly qualify the nature of connections between entities.

The visualization layer is tightly coupled with the data model: node properties, edge attributes, and interaction mechanisms are all derived from the structure of the processed datasets.

---

## Nodes

Each node represents a unique entity involved in credit operations.

### Identity and normalization

Nodes are identified by their normalized name, corresponding to the *forma autorizzata* used during data processing. This ensures consistency across:

- the general network  
- reconstructed datasets  
- visualization layer  

---

### Node size

Node size is determined by its **relational weight**, computed as the sum of incoming connections.

In particular:

- nodes with a higher number of incoming relationships (i.e. frequently referenced as shareholder or guarantor) are visually larger  
- node size reflects the **structural relevance** of the entity within the network  

---

### Node positioning

Nodes are arranged along a **linear axis**, following a fixed ordering.

This ordering is consistent across the dataset and is designed to:

- minimize visual clutter  
- enable comparison of relational patterns  
- support the arc diagram structure  

---

### Search and visibility

Nodes can be accessed through a search interface:

- the search operates on normalized entity names  
- selecting a node triggers:
  - visual focus (highlighting of connected edges)  
  - contextual information in the side panel  

Node labels are not permanently displayed, but are dynamically revealed through interaction (e.g. hover or zoom level), reducing overlap and improving readability.

---

## Edges

Edges represent directed relationships between entities.

---

### Directionality

Edges are directed and encode the relational structure:

- **client → shareholder (socio)**  
- **client → guarantor (garante)**  

---

### Edge thickness

Edge thickness is proportional to its **weight**, defined as:

- the number of occurrences of the same relationship across archival records  

This means:

- thicker edges represent stronger or more frequent relationships  
- thinner edges represent weaker or less frequent connections  

---

### Arc positioning (above / below)

Edges are rendered as arcs either **above or below** the node axis.

This distinction encodes the type of relationship:

- one side represents **shareholder relationships (soci)**  
- the opposite side represents **guarantee relationships (garanzie)**  

This separation allows both types of relationships to be visualized simultaneously without overlap.

---

### Aggregation and cumulative links

Edges are **aggregated** across multiple records:

- repeated relationships between the same pair of nodes are merged  
- weights are accumulated  
- document references are combined  
- IdxDams identifiers are deduplicated and preserved  

This produces cumulative links that reflect the overall intensity of the relationship.

---

## Interaction model

The visualization supports multiple interactive features that are directly tied to the data structure.

---

### Zooming and navigation

Users can zoom and pan across the diagram:

- zooming allows finer inspection of dense regions  
- label visibility adapts to zoom level to maintain readability  

---

### Filtering

Users can filter the network by relationship type:

- soci (shareholders)  
- garanzie (guarantees)  

This enables focused analysis of specific relational dimensions.

---

### Node and edge selection

Interaction includes:

- node selection → highlights all connected edges  
- edge inspection → reveals detailed information about the relationship  

This supports both local (node-level) and relational (edge-level) exploration.

---

## Side panel and analytical features

The visualization includes a side panel that provides additional analytical tools.

---

### Adjacency matrix

The system generates a **local adjacency matrix** based on the selected node:

- rows and columns represent connected entities  
- entries reflect the presence and weight of relationships  

The matrix is dynamically constructed from the underlying graph data and can be exported for further analysis.

This feature provides:

- a structured representation of local connectivity  
- a bridge between visual exploration and analytical workflows  

---

### Archival documentation

Each edge is linked to its supporting archival evidence.

Through the side panel, users can:

- access the list of associated documents  
- inspect IdxDams identifiers  
- navigate to archival references supporting the relationship  

This ensures full traceability between:

- visualized connections  
- underlying historical documentation  

---

## Traceability

A core principle of the model is the preservation of traceability.

Each visual element corresponds to structured data that:

- originates from archival records  
- is processed and aggregated  
- remains linked to its documentary sources  

This guarantees that the visualization is not only exploratory, but also grounded in verifiable evidence.

---

## Limitations

The model depends on:

- consistent normalization of entity names  
- structure and quality of the source CSV  
- correctness of relationship extraction from the general network  

Additionally:

- aggregation may obscure temporal dynamics  
- visual density may increase in highly connected regions  

These aspects should be considered when interpreting the network.
