#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 20 12:14:40 2026

@author: filippooberto
"""

import json

INPUT = "updated-graph-data-final.json"
OUT_GARANZIE = "garanzie_edges_by_name_with_idxdams.json"
OUT_SOCI = "soci_edges_by_name_with_idxdams.json"

def main():
    with open(INPUT, "r", encoding="utf-8") as f:
        elements = json.load(f)

    # Mappa: node_id -> {name, codice}
    node_map = {}
    for el in elements:
        d = el.get("data", {})
        if "name" in d and "id" in d and "source" not in d and "target" not in d:
            node_id = str(d.get("id"))
            node_map[node_id] = {
                "name": d.get("name"),
                "codice": d.get("codice")  # qui sta l'IdxDams
            }

    garanzie_edges = []
    soci_edges = []

    for el in elements:
        d = el.get("data", {})
        if "source" not in d or "target" not in d:
            continue

        edge_type = (d.get("type") or "").strip()
        edge_type_lc = edge_type.lower()

        src_id = str(d.get("source"))
        tgt_id = str(d.get("target"))

        src_node = node_map.get(src_id, {})
        tgt_node = node_map.get(tgt_id, {})

        edge_out = {
            "id": d.get("id"),
            "type": d.get("type"),
            "weight": d.get("weight"),
            "source": src_node.get("name", src_id),
            "target": tgt_node.get("name", tgt_id),
            "source_id": src_id,
            "target_id": tgt_id,
            "source_IdxDams": src_node.get("codice"),
            "target_IdxDams": tgt_node.get("codice"),
        }

        if edge_type_lc == "garanzie_entities":
            garanzie_edges.append(edge_out)
        elif edge_type_lc == "soci_entities":
            soci_edges.append(edge_out)

    with open(OUT_GARANZIE, "w", encoding="utf-8") as f:
        json.dump(garanzie_edges, f, ensure_ascii=False, indent=2)

    with open(OUT_SOCI, "w", encoding="utf-8") as f:
        json.dump(soci_edges, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
