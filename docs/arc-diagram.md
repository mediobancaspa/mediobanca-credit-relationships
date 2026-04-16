# Arc Diagram Visualization

This section explains how to read and use the interactive arc diagram interface.  
It focuses on the visualization layer, the available controls, and the ways in which the interface supports exploration of the relational structure represented in the graph.

---

## Interface structure

The visualization is organized into two main areas:

- a large central canvas for the network view
- a right-hand information panel for contextual details and actions

The canvas occupies most of the screen and is used for direct visual exploration of the graph.  
The side panel acts as a reading and inspection environment: it updates dynamically according to the currently selected node or edge and provides access to further analytical tools, including the document list and the local adjacency matrix. The interface also includes a search bar and dataset toggle buttons placed above the canvas, allowing users to move quickly between different subsets of relationships.

---

## Reading the arc diagram

The network is displayed as an arc diagram, a layout that arranges nodes along a shared axis and represents relationships through curved links. This solution is especially effective for archival and relational datasets in which many entities recur across multiple records, because it reduces spatial dispersion and allows comparison of multiple links in a compact field.

The interface separates the two available relational layers into distinct datasets:

- **SOCI**
- **GARANZIE**

Users do not see both at once. Instead, the visualization switches between them through dedicated controls. This means that the same node may appear in both views, but its visible relational context depends on the dataset currently active.

### Arc direction relative to the selected node

When a node is selected, the position of the arcs relative to the central axis does not identify the dataset itself, but the direction of the relationship with respect to that node.

- arcs drawn **above** the axis represent relationships in which the selected node acts as **source**
- arcs drawn **below** the axis represent relationships in which the selected node acts as **target**

This is a structural rule of the interface. The graph is therefore not only showing whether a connection exists, but also how that connection is oriented.

In practical terms, the meaning of this convention depends on the active dataset. In the **GARANZIE** view, for example, arcs above and below distinguish guarantees **issued** by the selected node from guarantees **received** by it. The same logic applies in the **SOCI** view: what changes is the semantic type of the relationship, not the geometric rule used to display its direction.

This makes the axis a visual reference line for interpreting the selected node’s role within the local network. The user can therefore distinguish at a glance between outgoing and incoming ties, while the exact source-target direction is preserved consistently across selection, edge inspection, and adjacency-matrix generation.

## Datasets and view switching

The graph loads two separate JSON files, one for shareholder relationships and one for guarantee relationships. Each dataset is indexed independently inside the application, with its own nodes, edges, incidence structure, degree counts, and edge lookup map. Switching dataset does not simply recolor the same geometry: it changes the active relational universe that the interface is exploring. 
This has an important interpretive consequence. The visualization should not be read as a single undifferentiated network. It is better understood as an interface for moving between two complementary relational projections built from the same archival corpus. In practice, the dataset buttons act as a semantic filter at the highest level of the interface.

---

## Navigation and spatial exploration

The canvas supports continuous navigation through direct manipulation:

- **pan** by dragging the canvas
- **zoom** with the mouse wheel
- **reset view** through the dedicated button in the side panel

The view state is managed through zoom and pan coordinates, with explicit minimum and maximum zoom thresholds. Zooming is centered on the pointer position, which makes local inspection much more precise than a generic page zoom. The default opening view is not perfectly centered but slightly shifted upward, indicating that the composition has been visually calibrated for readability rather than left in a neutral automatic state. 
Because of this, the visualization is not only a static map of relations: it is an exploratory field in which proximity, density, and local clusters are progressively revealed by moving across the canvas.

---

## Labels and legibility

Node labels are not displayed permanently for every entity. Instead, the interface uses a layered legibility strategy:

- labels appear on **hover**
- a subset of node names can become visible depending on the current view state
- label visibility is tied to zoom-sensitive logic and prominence management

This design reduces clutter in dense areas and prevents the canvas from being overwhelmed by overlapping text. The HTML explicitly defines a hover label component and a zoom threshold for automatic label display, showing that legibility is treated as a dynamic condition rather than a fixed graphic property. 

As a result, the graph should be read interactively. Names are meant to emerge in response to inspection, not to remain fully exposed at all times.

---

## Search and guided access

The search interface supports direct access to entities by name. It performs case-insensitive matching against the names of the nodes in the currently active dataset and returns a suggestion list as the user types. When no query is entered, the interface can display a capped alphabetical list of available nodes, encouraging guided exploration even without prior knowledge of a specific entity.

Selecting a suggestion triggers a focus action on the chosen node. This turns search into more than a lookup mechanism: it becomes a navigational shortcut that links textual access and spatial exploration.

This feature is especially useful in large archival graphs, where manual identification of a specific entity on the canvas would otherwise be difficult.

---

## Node selection

Clicking a node activates it as the current focus of the interface. Once selected, the node becomes the reference point for a set of contextual operations:

- the side panel is updated with node-specific information
- document extraction can be performed at node level
- a local adjacency matrix can be generated from the node’s neighborhood

The application internally stores the selected node name and uses the incidence structure of the active dataset to retrieve all connected edges. This makes node selection the main analytical entry point for local exploration. 
The side panel therefore functions as an interpretive companion to the visual scene: the graph provides topology, while the panel translates the selected entity into readable metadata and actions.

---

## Edge selection

Edges are also directly selectable from the canvas. When an arc is clicked, it becomes the active edge and can be inspected independently of node selection. In this state, the interface privileges relationship-level reading over entity-level reading.

This distinction is important. A node selection answers the question “what is connected to this entity?”, while an edge selection answers the question “what archival evidence supports this specific connection?”. The presence of separate logic for node documents and edge documents confirms that the interface recognizes these as two different analytical scales. 

---

## Side panel

The right-hand panel is a central interpretive component of the interface. It does not merely repeat data already visible in the graph, but organizes what the user needs in order to move from visual inspection to documentary verification.

The panel includes:

- contextual details for the current selection
- action buttons for documents and adjacency matrix
- a reset control
- dataset-level status metadata

In the lower part of the panel, the interface reports the current dataset, the number of nodes, the number of edges, and the general state of the loaded view. This means that the panel also serves as a lightweight dashboard, not only as a record card for selections. 

From a documentation perspective, this is one of the most important aspects of the interface: the arc diagram is not meant to be read in isolation, but in continuous dialogue with the explanatory layer provided by the side panel.

---

## Document inspection

The button **VEDI I DOCUMENTI** opens a modal window listing the archival references associated with the current selection. The behavior changes depending on context:

- if an **edge** is selected, the modal shows the documents linked to that specific relationship
- if a **node** is selected, the modal aggregates the unique documents associated with all incident edges of that node

The modal includes a title, a contextual subtitle, a count of associated records, and a downloadable CSV export. Each listed item is presented as a coded archival reference, explicitly treated by the interface as a “scheda xDams”. 

This feature is crucial because it turns the visualization into a documented research instrument rather than a purely illustrative network. The graph is therefore not only navigable but also auditable: visual patterns can be checked against the underlying archival references.

The rebuilt edge JSON files confirm that document identifiers are embedded directly in each edge record together with `docs_count`, enabling this documentary inspection layer in the interface itself :contentReference.

---

## Local adjacency matrix

The button **APRI MATRICE DI ADIACENZA** generates a local adjacency matrix for the currently selected node. The matrix is shown in a dedicated modal window and can be exported as CSV. The interface requires a node selection before opening this view, which makes clear that the matrix is not global but local and context-dependent. 

This tool complements the visual reading of arcs with a more formal analytic representation. While the arc diagram is better for recognizing shapes, densities, and recurrent neighboring entities, the matrix is better for structured inspection and tabular export. The coexistence of these two views shows that the interface was designed both for visual communication and for closer analytical use.

---

## Hover, focus, and progressive disclosure

A key design principle of the HTML is progressive disclosure. Information is not displayed all at once; it is revealed through interaction:

- moving the pointer over a node reveals its name
- clicking a node opens a deeper contextual layer
- clicking an edge isolates a specific relationship
- opening a modal moves from graph view to documentary or tabular inspection

This sequence supports multiple levels of reading, from quick orientation to detailed verification. It is particularly well suited to archival datasets, where users often need to move from overview to source evidence without leaving the interface. 

---

## Status feedback and usability

The interface includes a small status HUD that communicates loading states, reset actions, and selection-related prompts. For example, if no node is selected and the user tries to open the adjacency matrix, the system responds by prompting the appropriate prerequisite action. Similar feedback is provided when the user tries to open documents without having selected a node or an edge. 

These elements are minor in appearance but important in practice: they help frame the graph as a usable application rather than a passive visualization.

---

## Interpretive use

The visualization is best used as a multi-step exploratory environment:

1. choose the relational layer to inspect  
2. navigate the field visually through pan and zoom  
3. search for or manually select a node  
4. inspect local connections in the side panel  
5. open the adjacency matrix for a structured local view  
6. open the document modal to verify the archival evidence behind the selected entity or relationship  

This workflow reflects the actual structure of the HTML application and shows how the visualization supports both discovery and verification within the same interface. 
---

## Notes on interpretation

This interface should be read as an exploratory and evidence-linked visualization environment. Its purpose is not only to display a network, but to let users move across different levels of abstraction: from the overview of a relational field, to the neighborhood of a single entity, to the individual supporting archival references.

For that reason, the most meaningful way to use the arc diagram is not to treat it as a static image, but as a structured workspace in which graphical inspection, local network analysis, and documentary validation are continuously connected.
