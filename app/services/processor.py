"""
CSV/Excel processor using Polars.
Cleans data and generates a summary report.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import polars as pl


def load_file(path: Path) -> pl.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pl.read_csv(path, infer_schema_length=500, ignore_errors=True)
    elif suffix in (".xlsx", ".xls"):
        return pl.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def clean(df: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    """Clean dataframe and return (clean_df, stats)."""
    rows_raw = len(df)

    # 1. Strip whitespace from string columns
    str_cols = [c for c, t in zip(df.columns, df.dtypes) if t == pl.Utf8 or t == pl.String]
    if str_cols:
        df = df.with_columns([pl.col(c).str.strip_chars() for c in str_cols])

    # 2. Remove fully duplicate rows
    df_dedup = df.unique()
    duplicates_removed = rows_raw - len(df_dedup)
    df = df_dedup

    # 3. Count nulls per column before fill
    null_counts = {c: df[c].null_count() for c in df.columns}
    total_nulls = sum(null_counts.values())

    # 4. Fill nulls: numeric → 0, string → "N/A"
    fill_exprs = []
    for col_name, dtype in zip(df.columns, df.dtypes):
        if dtype in (pl.Int32, pl.Int64, pl.Float32, pl.Float64):
            fill_exprs.append(pl.col(col_name).fill_null(0))
        elif dtype in (pl.Utf8, pl.String):
            fill_exprs.append(pl.col(col_name).fill_null("N/A"))
    if fill_exprs:
        df = df.with_columns(fill_exprs)

    rows_clean = len(df)

    stats = {
        "rows_raw": rows_raw,
        "rows_clean": rows_clean,
        "duplicates_removed": duplicates_removed,
        "nulls_filled": total_nulls,
        "columns": df.columns,
        "null_counts_before": null_counts,
        "column_count": len(df.columns),
    }

    return df, stats


def generate_report(df: pl.DataFrame, stats: dict, job_id: int, reports_dir: Path) -> Path:
    """Generate a JSON + Excel report for a processed job."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    # Numeric summary
    numeric_cols = [c for c, t in zip(df.columns, df.dtypes)
                    if t in (pl.Int32, pl.Int64, pl.Float32, pl.Float64)]
    numeric_summary = {}
    for col in numeric_cols:
        series = df[col]
        numeric_summary[col] = {
            "min": series.min(),
            "max": series.max(),
            "mean": round(series.mean() or 0, 2),
            "sum": series.sum(),
        }

    report = {
        "job_id": job_id,
        "generated_at": timestamp,
        "rows_raw": stats["rows_raw"],
        "rows_clean": stats["rows_clean"],
        "duplicates_removed": stats["duplicates_removed"],
        "nulls_filled": stats["nulls_filled"],
        "columns": stats["columns"],
        "numeric_summary": numeric_summary,
    }

    # Save JSON report
    json_path = reports_dir / f"report_{job_id}_{timestamp}.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    # Save Excel report
    excel_path = reports_dir / f"report_{job_id}_{timestamp}.xlsx"
    df.write_excel(excel_path)

    return excel_path


def process_file(file_path: Path, job_id: int, reports_dir: Path) -> dict:
    """Full pipeline: load → clean → report. Returns stats dict."""
    df_raw = load_file(file_path)
    df_clean, stats = clean(df_raw)
    report_path = generate_report(df_clean, stats, job_id, reports_dir)
    stats["report_path"] = str(report_path)
    return stats
