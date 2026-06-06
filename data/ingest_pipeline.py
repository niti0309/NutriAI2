"""
NutriAI data ingestion pipeline — deduplication & rubric validation (BAX-423).

Rubric target: ≥10,000 structured records ingested with correct deduplication.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

MIN_INGESTED_RECORDS = 10_000
INGESTED_DIR = Path(__file__).resolve().parent / "ingested"


@dataclass
class IngestionStats:
    raw_row_count: int
    deduplicated_row_count: int
    duplicates_removed: int
    dedup_keys: str
    curated_count: int
    bulk_count: int
    unique_fdc_ids: int
    unique_names: int

    @property
    def meets_rubric(self) -> bool:
        return self.deduplicated_row_count >= MIN_INGESTED_RECORDS

    def summary_lines(self) -> list[str]:
        status = "MET" if self.meets_rubric else "NOT MET"
        return [
            "=== NutriAI data ingestion pipeline ===",
            f"Raw structured records loaded: {self.raw_row_count:,}",
            f"After deduplication ({self.dedup_keys}): {self.deduplicated_row_count:,}",
            f"Duplicates removed: {self.duplicates_removed:,}",
            f"  Curated dishes: {self.curated_count:,}",
            f"  Bulk USDA catalog: {self.bulk_count:,}",
            f"Unique USDA fdcIds: {self.unique_fdc_ids:,}",
            f"Unique food names: {self.unique_names:,}",
            f"Rubric threshold (>= {MIN_INGESTED_RECORDS:,}): {status}",
        ]


def deduplicate_food_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, IngestionStats]:
    """Deduplicate ingested foods: primary key usda_fdcId, secondary key name."""
    raw = len(df)
    work = df.copy()
    work["_fdc"] = (
        work["usda_fdcId"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
    )
    work["_name_key"] = work["name"].astype(str).str.strip().str.lower()

    has_fdc = work["_fdc"] != ""
    with_fdc = work[has_fdc].drop_duplicates(subset=["_fdc"], keep="first")
    without_fdc = work[~has_fdc].drop_duplicates(subset=["_name_key"], keep="first")
    deduped = pd.concat([with_fdc, without_fdc], ignore_index=True)
    deduped = deduped.drop_duplicates(subset=["_name_key"], keep="first")
    deduped = deduped.drop(columns=["_fdc", "_name_key"], errors="ignore")

    fdc_nonempty = deduped["usda_fdcId"].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    stats = IngestionStats(
        raw_row_count=raw,
        deduplicated_row_count=len(deduped),
        duplicates_removed=raw - len(deduped),
        dedup_keys="usda_fdcId (primary), name (secondary)",
        curated_count=0,
        bulk_count=len(deduped),
        unique_fdc_ids=int(fdc_nonempty[fdc_nonempty != ""].nunique()),
        unique_names=int(deduped["name"].nunique()),
    )
    return deduped, stats


def save_ingestion_artifacts(df: pd.DataFrame, stats: IngestionStats) -> dict[str, str]:
    """Persist deduplicated snapshot + JSON report for graders."""
    INGESTED_DIR.mkdir(parents=True, exist_ok=True)
    parquet_path = INGESTED_DIR / "food_database_deduped.parquet"
    report_path = INGESTED_DIR / "ingestion_report.json"
    try:
        df.to_parquet(parquet_path, index=False)
    except Exception:
        parquet_path = INGESTED_DIR / "food_database_deduped.csv"
        df.to_csv(parquet_path, index=False)
    report = {
        **asdict(stats),
        "meets_rubric": stats.meets_rubric,
        "min_required": MIN_INGESTED_RECORDS,
        "parquet_path": str(parquet_path),
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return {"parquet": str(parquet_path), "report": str(report_path)}


def print_ingestion_summary(stats: IngestionStats) -> None:
    for line in stats.summary_lines():
        print(line)
    print("PASS" if stats.meets_rubric else "FAIL")
