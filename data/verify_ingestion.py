#!/usr/bin/env python3
"""Verify NutriAI ingestion meets BAX-423 rubric (≥10,000 deduplicated records)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

from dataclasses import replace

from ingest_pipeline import (
    MIN_INGESTED_RECORDS,
    deduplicate_food_dataframe,
    print_ingestion_summary,
    save_ingestion_artifacts,
)

DATA_DIR = Path(__file__).resolve().parent
CSV_PATH = DATA_DIR / "food_database.csv"
REPORT_PATH = DATA_DIR / "ingested" / "ingestion_report.json"


def main() -> int:
    if not CSV_PATH.exists():
        print(f"Missing {CSV_PATH}. Run: python fetch_usda_data.py")
        return 1

    raw_df = pd.read_csv(CSV_PATH)
    df, stats = deduplicate_food_dataframe(raw_df)
    curated = min(249, len(df))
    stats = replace(stats, curated_count=curated, bulk_count=len(df) - curated)
    print_ingestion_summary(stats)

    if REPORT_PATH.exists():
        saved = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        print(f"\nSaved ingestion report: {REPORT_PATH}")
        print(f"  Last pipeline run: {saved.get('deduplicated_row_count', 'n/a'):,} records")

    if not stats.meets_rubric:
        print(
            f"\nTo reach {MIN_INGESTED_RECORDS:,}+ records without re-fetching curated dishes:\n"
            f"  cd {DATA_DIR}\n"
            f"  EXTEND_ONLY=1 SKIP_BACKFILL=1 python fetch_usda_data.py"
        )
        return 1

    # Refresh artifacts if CSV passes but report is stale
    if not REPORT_PATH.exists():
        paths = save_ingestion_artifacts(df, stats)
        print(f"\nUpdated {paths['report']}")
    else:
        saved = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        if saved.get("deduplicated_row_count") != stats.deduplicated_row_count:
            paths = save_ingestion_artifacts(df, stats)
            print(f"\nUpdated {paths['report']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
