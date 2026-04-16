# Data Model

This document defines the structural data model underlying the Mediobanca Credit Network Visualization.

---

## Overview

The network documented here should be understood as a specialization of a broader relational graph derived from the Mediobanca historical archive and published in the companion repository:

https://github.com/mediobancaspa/Mediobanca-Credit-Network

Within that broader model, connections between entities are represented as part of a general relational structure. The present graph is conceived as an extension and analytical specification of that network, designed to make explicit the nature of the links connecting entities.

More specifically, its purpose is to reconstruct and visualize two classes of relationships that are not explicitly distinguished in the general graph:

- shareholder relationships (*soci*)
- guarantee relationships (*garanzie*)

The resulting network is therefore not an independent graph, but a typed and specialized projection of the broader Mediobanca Credit Network. Its analytical value lies in qualifying relational ties that, in the general graph, remain structurally visible but semantically undifferentiated.

In this sense, the model serves both as an interpretative refinement of the original network and as a dedicated environment for exploring the role of shareholders and guarantors in the relational structure emerging from archival credit records.

## Relationship to the general network

![General network](../assets/img/general-network-preview.png)

*Figure 1. General relational network derived from the Mediobanca historical archive.*

![Specialized soci-garanzie network](../assets/img/arc-diagram-preview.png)

*Figure 2. Specialized network focused on shareholder and guarantee relationships.*

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
