# Arc Diagram Visualization

This document explains how to read and interact with the network visualization.

---

## Layout

The visualization uses an arc diagram:

- nodes are arranged along a linear axis  
- relationships are drawn as arcs  

This allows compact representation of dense relational structures.

---

## Nodes

### Size

Node size reflects the number of incoming relationships.

### Labels

Labels are dynamically displayed:

- on hover  
- depending on zoom level  

---

## Edges

### Thickness

Edge thickness represents relationship weight.

### Position

- arcs above → shareholder relationships (soci)  
- arcs below → guarantee relationships (garanzie)  

---

## Interaction

### Zoom and navigation

- zoom for detailed inspection  
- pan across the network  

---

### Filtering

Users can isolate:

- soci  
- garanzie  

---

### Selection

- selecting a node highlights connections  
- selecting an edge reveals details  

---

## Side panel

### Adjacency matrix

- generated dynamically for selected node  
- represents local connectivity  
- exportable  

---

### Archival references

Each relationship includes:

- document references  
- IdxDams identifiers  

This enables direct access to supporting archival evidence.
