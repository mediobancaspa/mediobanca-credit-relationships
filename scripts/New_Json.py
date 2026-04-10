#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 14:20:24 2026

@author: filippooberto
"""

import json
import re
import uuid
from pathlib import Path
from collections import Counter, defaultdict
from itertools import zip_longest

import pandas as pd


# ======================
# CONFIG
# ======================

CSV_PATH = Path("2026_02_27_exportCrediti_updated.csv")

SOCI_JSON_PATH = Path("soci_edges_by_name_with_idxdams.json")
GARANZIE_JSON_PATH = Path("garanzie_edges_by_name_with_idxdams.json")

OUT_SOCI_JSON_PATH = Path("soci_edges_by_name_with_idxdams_rebuilt.json")
OUT_GARANZIE_JSON_PATH = Path("garanzie_edges_by_name_with_idxdams_rebuilt.json")

OUT_SOCI_REPORT_PATH = Path("soci_rebuild_report.json")
OUT_GARANZIE_REPORT_PATH = Path("garanzie_rebuild_report.json")

CSV_SEP = ";"
CSV_ENCODING = "latin1"

# Se True, nello stesso documento la stessa coppia source->target viene contata una sola volta.
# In genere è la scelta più prudente.
DEDUP_PAIRS_WITHIN_DOCUMENT = True

# Se True, evita auto-archi source == target
SKIP_SELF_LOOPS = True


# ======================
# NORMALIZZAZIONE
# ======================

def normalize_text(value) -> str:
    if value is None:
        return ""
    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_key(value) -> str:
    return normalize_text(value).lower()


# ======================
# JSON I/O
# ======================

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path: Path):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ======================
# PARSING TOKEN ENTITÀ
# ======================

ENTITY_TOKEN_RE = re.compile(r"^(.*?)\s*\(([^()]*)\)\s*$")


def parse_entity_token(token: str) -> dict:
    """
    Esempio input:
    'Sanitaria Ceschina & C. SpA (IT-MEDIOBANCA-EACCPF0001-003894)'

    Output:
    {
        "name": "Sanitaria Ceschina & C. SpA",
        "idxdams": "IT-MEDIOBANCA-EACCPF0001-003894"
    }
    """
    token = normalize_text(token)
    if not token:
        return {"name": "", "idxdams": None}

    m = ENTITY_TOKEN_RE.match(token)
    if m:
        name = normalize_text(m.group(1))
        idxdams = normalize_text(m.group(2))
        return {"name": name, "idxdams": idxdams or None}

    return {"name": token, "idxdams": None}


def split_hash_values(value) -> list[str]:
    value = normalize_text(value)
    if not value:
        return []
    return [normalize_text(x) for x in str(value).split("#")]


def find_role_column(df: pd.DataFrame, base_col: str) -> str | None:
    """
    Gestisce sia ..._tipo sia ..._ruolo
    """
    candidates = [
        f"{base_col}_tipo",
        f"{base_col}_ruolo",
    ]
    for c in candidates:
        if c in df.columns:
            return c
    return None


def extract_entities_from_column_pair(row, value_col: str, role_col: str | None) -> list[dict]:
    """
    Estrae entità e ruolo da una coppia di colonne:
    - chiavi_di_accesso_enti
    - chiavi_di_accesso_enti_tipo / ruolo
    """
    raw_values = split_hash_values(row.get(value_col, ""))
    raw_roles = split_hash_values(row.get(role_col, "")) if role_col else []

    entities = []
    for token, role in zip_longest(raw_values, raw_roles, fillvalue=""):
        parsed = parse_entity_token(token or "")
        name = parsed["name"]
        idxdams = parsed["idxdams"]
        role = normalize_text(role)

        if not name:
            continue

        entities.append({
            "name": name,
            "idxdams": idxdams,
            "role": role,
            "source_column": value_col,
        })

    return entities


def extract_row_entities(row, df_columns: set[str]) -> list[dict]:
    """
    Estrae tutte le entità da:
    - chiavi_di_accesso_enti
    - chiavi_di_accesso_persone
    - chiavi_di_accesso_famiglie
    """
    all_entities = []

    base_columns = [
        "chiavi_di_accesso_enti",
        "chiavi_di_accesso_persone",
        "chiavi_di_accesso_famiglie",
    ]

    for base_col in base_columns:
        if base_col not in df_columns:
            continue
        role_col = None
        if f"{base_col}_tipo" in df_columns:
            role_col = f"{base_col}_tipo"
        elif f"{base_col}_ruolo" in df_columns:
            role_col = f"{base_col}_ruolo"

        extracted = extract_entities_from_column_pair(row, base_col, role_col)
        all_entities.extend(extracted)

    return all_entities


# ======================
# COSTRUZIONE ARCHI DA CSV
# ======================

def choose_most_common_nonempty(counter: Counter) -> str | None:
    if not counter:
        return None
    for value, _count in counter.most_common():
        if value:
            return value
    return None


def build_edges_from_csv(df: pd.DataFrame, target_role: str) -> dict[tuple[str, str], dict]:
    """
    Costruisce archi direzionali:
        cliente -> target_role
    dove target_role è 'socio' oppure 'garante'

    Restituisce una mappa:
        (source_name, target_name) -> edge_info aggregata
    """
    edges = {}

    df_columns = set(df.columns)

    for row_idx, row in df.iterrows():
        doc_code = normalize_text(row.get("codice", ""))
        if not doc_code:
            continue

        entities = extract_row_entities(row, df_columns)
        if not entities:
            continue

        clients = [e for e in entities if normalize_key(e["role"]) == "cliente"]
        targets = [e for e in entities if normalize_key(e["role"]) == normalize_key(target_role)]

        if not clients or not targets:
            continue

        pairs_seen_in_this_doc = set()

        for src in clients:
            for tgt in targets:
                src_name = normalize_text(src["name"])
                tgt_name = normalize_text(tgt["name"])

                if not src_name or not tgt_name:
                    continue

                if SKIP_SELF_LOOPS and normalize_key(src_name) == normalize_key(tgt_name):
                    continue

                pair_key = (src_name, tgt_name)

                if DEDUP_PAIRS_WITHIN_DOCUMENT:
                    doc_pair_key = (doc_code, src_name, tgt_name)
                    if doc_pair_key in pairs_seen_in_this_doc:
                        continue
                    pairs_seen_in_this_doc.add(doc_pair_key)

                if pair_key not in edges:
                    edges[pair_key] = {
                        "source": src_name,
                        "target": tgt_name,
                        "weight": 0,
                        "docs": set(),
                        "source_idxdams_counter": Counter(),
                        "target_idxdams_counter": Counter(),
                        "row_indices": [],
                    }

                edges[pair_key]["weight"] += 1
                edges[pair_key]["docs"].add(doc_code)
                edges[pair_key]["row_indices"].append(int(row_idx))

                if src.get("idxdams"):
                    edges[pair_key]["source_idxdams_counter"][src["idxdams"]] += 1
                if tgt.get("idxdams"):
                    edges[pair_key]["target_idxdams_counter"][tgt["idxdams"]] += 1

    return edges


# ======================
# SUPPORTO MERGE CON JSON ESISTENTE
# ======================

def build_existing_edge_map(existing_edges: list[dict]) -> tuple[dict, dict]:
    """
    Restituisce:
    - exact map: (source, target) -> edge
    - normalized map: (norm_source, norm_target) -> [edges]
    """
    exact_map = {}
    norm_map = defaultdict(list)

    for edge in existing_edges:
        source = normalize_text(edge.get("source", ""))
        target = normalize_text(edge.get("target", ""))

        exact_map[(source, target)] = edge
        norm_map[(normalize_key(source), normalize_key(target))].append(edge)

    return exact_map, norm_map


def build_existing_node_id_map(existing_edges: list[dict]) -> dict[str, str]:
    """
    Mappa nome nodo -> node_id, ricavata da source_id/target_id dei JSON esistenti.
    """
    node_id_map = {}

    for edge in existing_edges:
        source = normalize_text(edge.get("source", ""))
        target = normalize_text(edge.get("target", ""))

        source_id = edge.get("source_id")
        target_id = edge.get("target_id")

        if source and source_id is not None and source not in node_id_map:
            node_id_map[source] = str(source_id)
        if target and target_id is not None and target not in node_id_map:
            node_id_map[target] = str(target_id)

    return node_id_map


def next_numeric_node_id(node_id_map: dict[str, str]) -> int:
    numeric_ids = []
    for v in node_id_map.values():
        try:
            numeric_ids.append(int(str(v)))
        except Exception:
            continue
    return max(numeric_ids, default=0) + 1


def get_or_create_node_id(name: str, node_id_map: dict[str, str], next_id_holder: dict) -> str:
    if name in node_id_map:
        return str(node_id_map[name])

    new_id = str(next_id_holder["next_id"])
    node_id_map[name] = new_id
    next_id_holder["next_id"] += 1
    return new_id


# ======================
# RICOSTRUZIONE JSON
# ======================

def rebuild_edges_json(
    csv_edges: dict[tuple[str, str], dict],
    existing_edges: list[dict],
    edge_type: str,
) -> tuple[list[dict], dict]:
    """
    Ricostruisce l'array finale di edge JSON.
    Preserva gli id edge e gli id nodo quando possibile.
    """
    exact_map, norm_map = build_existing_edge_map(existing_edges)
    node_id_map = build_existing_node_id_map(existing_edges)
    next_id_holder = {"next_id": next_numeric_node_id(node_id_map)}

    rebuilt = []
    reused_edge_ids = 0
    new_edge_ids = 0
    exact_matches = 0
    normalized_matches = 0
    unmatched_existing = set(edge.get("id") for edge in existing_edges if edge.get("id") is not None)

    for (source, target), info in sorted(csv_edges.items(), key=lambda x: (x[0][0].lower(), x[0][1].lower())):
        matched_existing = exact_map.get((source, target))

        if matched_existing is not None:
            exact_matches += 1
        else:
            candidates = norm_map.get((normalize_key(source), normalize_key(target)), [])
            if len(candidates) == 1:
                matched_existing = candidates[0]
                normalized_matches += 1

        if matched_existing is not None and matched_existing.get("id") in unmatched_existing:
            unmatched_existing.remove(matched_existing.get("id"))

        source_id = get_or_create_node_id(source, node_id_map, next_id_holder)
        target_id = get_or_create_node_id(target, node_id_map, next_id_holder)

        edge_id = None
        if matched_existing is not None and matched_existing.get("id") is not None:
            edge_id = matched_existing["id"]
            reused_edge_ids += 1
        else:
            edge_id = str(uuid.uuid4())
            new_edge_ids += 1

        source_idxdams = choose_most_common_nonempty(info["source_idxdams_counter"])
        target_idxdams = choose_most_common_nonempty(info["target_idxdams_counter"])
        docs_sorted = sorted(info["docs"])

        rebuilt_edge = {
            "id": edge_id,
            "type": edge_type,
            "weight": int(info["weight"]),
            "source": source,
            "target": target,
            "source_id": source_id,
            "target_id": target_id,
            "source_IdxDams": source_idxdams,
            "target_IdxDams": target_idxdams,
            "docs_count": len(docs_sorted),
            "docs": docs_sorted,
        }

        rebuilt.append(rebuilt_edge)

    report = {
        "edge_type": edge_type,
        "existing_edges_count": len(existing_edges),
        "rebuilt_edges_count": len(rebuilt),
        "exact_matches_on_existing": exact_matches,
        "normalized_matches_on_existing": normalized_matches,
        "reused_edge_ids": reused_edge_ids,
        "new_edge_ids": new_edge_ids,
        "unmatched_existing_edge_ids_count": len(unmatched_existing),
        "unmatched_existing_edge_ids_preview": list(sorted(str(x) for x in unmatched_existing))[:50],
        "new_nodes_count": sum(1 for v in node_id_map.values()),  # totale nodi mappati finali
    }

    return rebuilt, report


# ======================
# REPORT COMPATTO
# ======================

def build_summary_report(edges: list[dict], report: dict) -> dict:
    total_weight = sum(int(e.get("weight", 0)) for e in edges)
    total_docs_refs = sum(int(e.get("docs_count", 0)) for e in edges)

    return {
        **report,
        "edges_total": len(edges),
        "total_weight_sum": total_weight,
        "total_docs_refs_sum": total_docs_refs,
        "edges_with_docs": sum(1 for e in edges if e.get("docs_count", 0) > 0),
        "edges_without_docs": sum(1 for e in edges if e.get("docs_count", 0) == 0),
        "top_20_edges_by_weight": sorted(
            [
                {
                    "source": e["source"],
                    "target": e["target"],
                    "weight": e["weight"],
                    "docs_count": e["docs_count"],
                }
                for e in edges
            ],
            key=lambda x: (-x["weight"], x["source"].lower(), x["target"].lower())
        )[:20],
    }


# ======================
# MAIN
# ======================

def main():
    print("Lettura CSV...")
    df = pd.read_csv(
        CSV_PATH,
        sep=CSV_SEP,
        dtype=str,
        keep_default_na=False,
        encoding=CSV_ENCODING,
    )

    if "codice" not in df.columns:
        raise ValueError("Nel CSV manca la colonna 'codice'.")

    print("Costruzione archi SOCI dal CSV...")
    soci_edges_from_csv = build_edges_from_csv(df, target_role="socio")

    print("Costruzione archi GARANZIE dal CSV...")
    garanzie_edges_from_csv = build_edges_from_csv(df, target_role="garante")

    print("Lettura JSON esistenti...")
    soci_existing = load_json(SOCI_JSON_PATH)
    garanzie_existing = load_json(GARANZIE_JSON_PATH)

    print("Ricostruzione JSON SOCI...")
    soci_rebuilt, soci_report_base = rebuild_edges_json(
        csv_edges=soci_edges_from_csv,
        existing_edges=soci_existing,
        edge_type="Soci_entities",
    )

    print("Ricostruzione JSON GARANZIE...")
    garanzie_rebuilt, garanzie_report_base = rebuild_edges_json(
        csv_edges=garanzie_edges_from_csv,
        existing_edges=garanzie_existing,
        edge_type="Garanzie_entities",
    )

    soci_report = build_summary_report(soci_rebuilt, soci_report_base)
    garanzie_report = build_summary_report(garanzie_rebuilt, garanzie_report_base)

    print("Salvataggio output...")
    save_json(soci_rebuilt, OUT_SOCI_JSON_PATH)
    save_json(garanzie_rebuilt, OUT_GARANZIE_JSON_PATH)
    save_json(soci_report, OUT_SOCI_REPORT_PATH)
    save_json(garanzie_report, OUT_GARANZIE_REPORT_PATH)

    print("\n=== REPORT SOCI ===")
    print(f"Archi ricostruiti: {soci_report['edges_total']}")
    print(f"Somma pesi: {soci_report['total_weight_sum']}")
    print(f"Archi con docs: {soci_report['edges_with_docs']}")
    print(f"ID edge riutilizzati: {soci_report['reused_edge_ids']}")
    print(f"Nuovi ID edge: {soci_report['new_edge_ids']}")
    print(f"Match esatti con JSON precedente: {soci_report['exact_matches_on_existing']}")
    print(f"Match normalizzati con JSON precedente: {soci_report['normalized_matches_on_existing']}")
    print(f"Edge vecchi non più presenti: {soci_report['unmatched_existing_edge_ids_count']}")

    print("\n=== REPORT GARANZIE ===")
    print(f"Archi ricostruiti: {garanzie_report['edges_total']}")
    print(f"Somma pesi: {garanzie_report['total_weight_sum']}")
    print(f"Archi con docs: {garanzie_report['edges_with_docs']}")
    print(f"ID edge riutilizzati: {garanzie_report['reused_edge_ids']}")
    print(f"Nuovi ID edge: {garanzie_report['new_edge_ids']}")
    print(f"Match esatti con JSON precedente: {garanzie_report['exact_matches_on_existing']}")
    print(f"Match normalizzati con JSON precedente: {garanzie_report['normalized_matches_on_existing']}")
    print(f"Edge vecchi non più presenti: {garanzie_report['unmatched_existing_edge_ids_count']}")

    print("\nFile creati:")
    print(f"- {OUT_SOCI_JSON_PATH}")
    print(f"- {OUT_GARANZIE_JSON_PATH}")
    print(f"- {OUT_SOCI_REPORT_PATH}")
    print(f"- {OUT_GARANZIE_REPORT_PATH}")


if __name__ == "__main__":
    main()