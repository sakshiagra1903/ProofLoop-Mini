import csv
import json
import pytest
from app import engine

def test_sales_report_and_verification(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "WORKSPACE", tmp_path)
    source = tmp_path / "sales.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["category", "amount"])
        writer.writeheader()
        writer.writerows([{"category": "books", "amount": "10"}, {"category": "books", "amount": "10"}, {"category": "games", "amount": "5.5"}])
    report = engine.run_sales_report("sales.csv", "report.json")
    verified = engine.verify_sales_report("report.json", report)
    saved = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["duplicates_removed"] == 1
    assert report["category_totals"] == {"books": 10.0, "games": 5.5}
    assert saved["category_totals"] == report["category_totals"]
    assert verified["verified"] is True

def test_missing_file_fails_safely(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "WORKSPACE", tmp_path)
    with pytest.raises(engine.TaskExecutionError, match="not found"):
        engine.run_sales_report("missing.csv", "report.json")

def test_path_traversal_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "WORKSPACE", tmp_path)
    with pytest.raises(engine.TaskExecutionError):
        engine.run_sales_report("../secret.csv", "report.json")
