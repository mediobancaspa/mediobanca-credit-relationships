#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:50:38 2026

@author: filippooberto
"""

import json
import ast
import re
from pathlib import Path

import pandas as pd


# ======================
# CONFIG
# ======================

CSV_PATH = Path("2024_10_14_CREDITI_GRAFO_FINALE.csv")
SOCI_JSON_PATH = Path("soci_edges_by_name_with_idxdams.json")
GARANZIE_JSON_PATH = Path("garanzie_edges_by_name_with_idxdams.json")

OUT_SOCI_JSON_PATH = Path("soci_edges_with_docs.json")
OUT_GARANZIE_JSON_PATH = Path("garanzie_edges_with_docs.json")

CSV_ENCODING = "latin1"
CSV_SEP = ";"


# ======================
# HELPERS
# ======================

def normalize_text(value: str) -> str:
    """
    Normalizzazione leggera per il matching:
    - converte a stringa
    - trim spazi
    - collassa spazi multipli
    """
    if value is None:
        return ""
    value = str(value).strip()
    value = re.sub(r"\s+", " ", value)
    return value


def parse_entities_cell(cell_value: str) -> list[tuple[str, str]]:
    """
    Converte una cella del tipo:
    "[('Conti-Vecchi, Enrico', 'PER'), ('Minio Paluello, Vittorio', 'PER')]"
    in una lista di tuple Python.

    Restituisce [] in caso di cella vuota o parsing fallito.
    """
    if cell_value is None:
        return []

    cell_value = str(cell_value).strip()

    if not cell_value or cell_value == "[]" or cell_value.lower() == "nan":
        return []

    try:
        parsed = ast.literal_eval(cell_value)
    except Exception:
        return []

    if not isinstance(parsed, list):
        return []

    out = []
    for item in parsed:
        if isinstance(item, tuple) and len(item) >= 2:
            entity_name = normalize_text(item[0])
            entity_label = str(item[1]).strip()
            out.append((entity_name, entity_label))

    return out


def load_json(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ======================
# INDEX COSTRUZIONE DOCS
# ======================

def build_doc_index(df: pd.DataFrame, entity_col: str) -> dict[tuple[str, str], list[str]]:
    """
    Costruisce un indice del tipo:
        (authority_normalized, target_normalized) -> [Id xDams, Id xDams, ...]

    usando come target la prima componente delle tuple presenti in entity_col.
    """
    index: dict[tuple[str, str], list[str]] = {}

    required_cols = {"Id xDams", "authority", entity_col}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Nel CSV mancano le colonne richieste per {entity_col}: {missing}")

    for _, row in df.iterrows():
        doc_id = normalize_text(row["Id xDams"])
        authority = normalize_text(row["authority"])
        entities_raw = row[entity_col]

        if not doc_id or not authority:
            continue

        entities = parse_entities_cell(entities_raw)
        if not entities:
            continue

        for entity_name, _entity_label in entities:
            key = (authority, entity_name)
            index.setdefault(key, []).append(doc_id)

    return index


def enrich_edges_with_docs(
    edges: list[dict],
    doc_index: dict[tuple[str, str], list[str]],
    entity_col_name: str,
) -> tuple[list[dict], list[dict]]:
    """
    Aggiunge a ogni edge:
    - docs_count
    - docs

    Restituisce:
    - lista edges arricchiti
    - lista report per mismatch o assenza docs
    """
    enriched = []
    report = []

    for edge in edges:
        source = normalize_text(edge.get("source", ""))
        target = normalize_text(edge.get("target", ""))
        weight = edge.get("weight", None)

        docs = doc_index.get((source, target), [])
        docs = list(dict.fromkeys(docs))  # dedup preservando ordine

        new_edge = dict(edge)
        new_edge["docs_count"] = len(docs)
        new_edge["docs"] = docs

        enriched.append(new_edge)

        weight_num = None
        try:
            weight_num = int(weight)
        except Exception:
            try:
                weight_num = float(weight)
            except Exception:
                weight_num = None

        if len(docs) == 0:
            report.append({
                "edge_id": edge.get("id"),
                "type": edge.get("type"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "issue": "no_docs_found",
                "entity_column_used": entity_col_name,
                "weight": weight,
                "docs_count": 0,
            })
        elif weight_num is not None and len(docs) != weight_num:
            report.append({
                "edge_id": edge.get("id"),
                "type": edge.get("type"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "issue": "weight_docs_mismatch",
                "entity_column_used": entity_col_name,
                "weight": weight_num,
                "docs_count": len(docs),
                "docs": docs,
            })

    return enriched, report


# ======================
# REPORT DETTAGLIATO MANCANTI
# ======================

def build_missing_docs_report(
    edges: list[dict],
    df: pd.DataFrame,
    entity_col: str,
    max_targets_preview: int = 15,
) -> list[dict]:
    """
    Costruisce un report dettagliato dei soli archi per cui non sono stati trovati documenti.

    Per ogni edge mancante indica:
    - se la source/authority non compare mai nel CSV
    - oppure compare, ma il target non compare mai tra le entità associate
    - alcuni target realmente presenti per quella authority, per diagnosi
    """
    required_cols = {"Id xDams", "authority", entity_col}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Nel CSV mancano le colonne richieste per {entity_col}: {missing}")

    rows_by_authority: dict[str, list[dict]] = {}

    for _, row in df.iterrows():
        authority = normalize_text(row["authority"])
        if not authority:
            continue

        row_info = {
            "doc_id": normalize_text(row["Id xDams"]),
            "entities": parse_entities_cell(row[entity_col]),
        }
        rows_by_authority.setdefault(authority, []).append(row_info)

    missing_report = []

    for edge in edges:
        # consideriamo solo quelli che non hanno docs
        if edge.get("docs_count", 0) > 0:
            continue

        source = normalize_text(edge.get("source", ""))
        target = normalize_text(edge.get("target", ""))

        rows_for_source = rows_by_authority.get(source, [])

        if not rows_for_source:
            missing_report.append({
                "edge_id": edge.get("id"),
                "type": edge.get("type"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "weight": edge.get("weight"),
                "entity_column_used": entity_col,
                "reason": "source_not_found_in_authority",
                "authority_rows_found": 0,
                "available_targets_for_source_preview": [],
                "available_doc_ids_for_source_preview": [],
            })
            continue

        all_targets_for_source = []
        all_doc_ids_for_source = []

        for row_info in rows_for_source:
            if row_info["doc_id"]:
                all_doc_ids_for_source.append(row_info["doc_id"])
            for entity_name, _label in row_info["entities"]:
                all_targets_for_source.append(entity_name)

        unique_targets = list(dict.fromkeys(all_targets_for_source))
        unique_doc_ids = list(dict.fromkeys(all_doc_ids_for_source))

        target_found = target in set(unique_targets)

        if not target_found:
            missing_report.append({
                "edge_id": edge.get("id"),
                "type": edge.get("type"),
                "source": edge.get("source"),
                "target": edge.get("target"),
                "weight": edge.get("weight"),
                "entity_column_used": entity_col,
                "reason": "target_not_found_for_existing_source",
                "authority_rows_found": len(rows_for_source),
                "available_targets_for_source_preview": unique_targets[:max_targets_preview],
                "available_doc_ids_for_source_preview": unique_doc_ids[:max_targets_preview],
            })

    return missing_report


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

    print("Costruzione indici documentali...")
    soci_doc_index = build_doc_index(df, "Soci_entities")
    garanzie_doc_index = build_doc_index(df, "Garanzie_entities")

    print("Lettura JSON archi...")
    soci_edges = load_json(SOCI_JSON_PATH)
    garanzie_edges = load_json(GARANZIE_JSON_PATH)

    print("Arricchimento JSON SOCI...")
    soci_enriched, soci_report = enrich_edges_with_docs(
        soci_edges,
        soci_doc_index,
        "Soci_entities",
    )

    print("Arricchimento JSON GARANZIE...")
    garanzie_enriched, garanzie_report = enrich_edges_with_docs(
        garanzie_edges,
        garanzie_doc_index,
        "Garanzie_entities",
    )

    print("Costruzione report dettagliato dei mancanti...")
    soci_missing_report = build_missing_docs_report(
        edges=soci_enriched,
        df=df,
        entity_col="Soci_entities",
    )
    garanzie_missing_report = build_missing_docs_report(
        edges=garanzie_enriched,
        df=df,
        entity_col="Garanzie_entities",
    )

    print("Salvataggio output...")
    save_json(soci_enriched, OUT_SOCI_JSON_PATH)
    save_json(garanzie_enriched, OUT_GARANZIE_JSON_PATH)

    save_json(soci_report, Path("soci_docs_report.json"))
    save_json(garanzie_report, Path("garanzie_docs_report.json"))
    save_json(soci_missing_report, Path("soci_missing_docs_report.json"))
    save_json(garanzie_missing_report, Path("garanzie_missing_docs_report.json"))

    soci_total = len(soci_enriched)
    soci_with_docs = sum(1 for e in soci_enriched if e.get("docs_count", 0) > 0)
    soci_mismatch = sum(1 for r in soci_report if r["issue"] == "weight_docs_mismatch")
    soci_missing = len(soci_missing_report)

    gar_total = len(garanzie_enriched)
    gar_with_docs = sum(1 for e in garanzie_enriched if e.get("docs_count", 0) > 0)
    gar_mismatch = sum(1 for r in garanzie_report if r["issue"] == "weight_docs_mismatch")
    gar_missing = len(garanzie_missing_report)

    print("\n=== REPORT ===")
    print(f"SOCI: {soci_total} archi totali")
    print(f"SOCI: {soci_with_docs} archi con almeno un documento")
    print(f"SOCI: {soci_missing} archi senza documenti trovati")
    print(f"SOCI: {soci_mismatch} archi con docs_count != weight")

    print()

    print(f"GARANZIE: {gar_total} archi totali")
    print(f"GARANZIE: {gar_with_docs} archi con almeno un documento")
    print(f"GARANZIE: {gar_missing} archi senza documenti trovati")
    print(f"GARANZIE: {gar_mismatch} archi con docs_count != weight")

    print("\nFile creati:")
    print(f"- {OUT_SOCI_JSON_PATH}")
    print(f"- {OUT_GARANZIE_JSON_PATH}")
    print("- soci_docs_report.json")
    print("- garanzie_docs_report.json")
    print("- soci_missing_docs_report.json")
    print("- garanzie_missing_docs_report.json")


if __name__ == "__main__":
    main()