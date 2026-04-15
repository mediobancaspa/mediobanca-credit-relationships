# Data Model

This document defines the structural data model underlying the Mediobanca Credit Network Visualization.

---

## Overview

The network is modeled as a directed graph where nodes represent economic actors and edges represent reconstructed relationships derived from archival credit records.

The graph is a specialized projection of a broader relational network and focuses on qualifying the nature of relationships between entities.

---

## Nodes

Each node represents a unique entity involved in credit operations.

### Identity and normalization

Nodes are identified by their normalized name (*forma autorizzata*), ensuring consistency across datasets and alignment with the general network.

### Node weight

Nodes carry an implicit weight defined as the number of incoming relationships.

This value is used in the visualization layer to determine node size.

---

## Edges

Edges represent directed relationships between entities.

### Directionality

- client → shareholder (socio)  
- client → guarantor (garante)  

---

## Edge attributes

```json
{
  "source": "Entity A",
  "target": "Entity B",
  "weight": 3,
  "documents": [...],
  "idxdams": [...]
}
```

### Description

- **source / target**: entities involved in the relationship  
- **weight**: number of occurrences across archival records  
- **documents**: supporting archival references  
- **idxdams**: unique identifiers linked to archival records  

---

## Aggregation

Relationships are aggregated:

- repeated edges are merged  
- weights are summed  
- documents are combined  
- identifiers are deduplicated  

---

## Dataset structure

The model is implemented through separate datasets:

- soci (shareholder relationships)  
- garanzie (guarantee relationships)  

These share the same node space but represent different relational semantics.
