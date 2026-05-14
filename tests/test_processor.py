"""Tests for CSV/Excel processor."""

import pytest
import polars as pl
from pathlib import Path
from app.services.processor import clean, generate_report, process_file
import tempfile
import os


def make_df_with_issues() -> pl.DataFrame:
    return pl.DataFrame({
        "name":  ["Alice", "Bob", "Alice", "  Charlie  ", None],
        "age":   [25, 30, 25, None, 22],
        "score": [9.5, 8.0, 9.5, 7.5, None],
    })


def test_clean_removes_duplicates():
    df = make_df_with_issues()
    clean_df, stats = clean(df)
    assert stats["duplicates_removed"] == 1
    assert stats["rows_raw"] == 5
    assert stats["rows_clean"] == 4


def test_clean_fills_nulls():
    df = make_df_with_issues()
    clean_df, stats = clean(df)
    assert stats["nulls_filled"] > 0
    assert clean_df["age"].null_count() == 0
    assert clean_df["score"].null_count() == 0


def test_clean_strips_whitespace():
    df = pl.DataFrame({"name": ["  Alice  ", " Bob "]})
    clean_df, _ = clean(df)
    names = set(clean_df["name"].to_list())
    assert "Alice" in names
    assert "Bob" in names


def test_clean_stats_keys():
    df = make_df_with_issues()
    _, stats = clean(df)
    assert "rows_raw" in stats
    assert "rows_clean" in stats
    assert "duplicates_removed" in stats
    assert "nulls_filled" in stats
    assert "columns" in stats


def test_generate_report_creates_excel():
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    stats = {"rows_raw": 3, "rows_clean": 3, "duplicates_removed": 0,
             "nulls_filled": 0, "columns": ["a", "b"]}
    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = generate_report(df, stats, job_id=1, reports_dir=Path(tmpdir))
        assert report_path.exists()
        assert report_path.suffix == ".xlsx"


def test_process_csv(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("name,age\nAlice,25\nBob,30\nAlice,25\n")
    reports_dir = tmp_path / "reports"
    stats = process_file(csv_file, job_id=1, reports_dir=reports_dir)
    assert stats["rows_raw"] == 3
    assert stats["duplicates_removed"] == 1
    assert stats["rows_clean"] == 2
    assert Path(stats["report_path"]).exists()


def test_process_empty_csv(tmp_path):
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("name,age\n")
    reports_dir = tmp_path / "reports"
    stats = process_file(csv_file, job_id=2, reports_dir=reports_dir)
    assert stats["rows_raw"] == 0
    assert stats["rows_clean"] == 0
