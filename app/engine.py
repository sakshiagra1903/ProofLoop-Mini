import json
import math
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent / "workspace"

class TaskExecutionError(Exception):
    pass

def _safe_file(filename, suffix):
    if Path(filename).name != filename or filename in {".", ".."}:
        raise TaskExecutionError("Only filenames inside the workspace are allowed.")
    if not filename.lower().endswith(suffix):
        raise TaskExecutionError(f"Expected a {suffix} file.")
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    target = (WORKSPACE / filename).resolve()
    if target.parent != WORKSPACE.resolve():
        raise TaskExecutionError("Path is outside the allowed workspace.")
    return target

def run_sales_report(input_file, output_file):
    import csv
    from collections import defaultdict
    source = _safe_file(input_file, ".csv")
    target = _safe_file(output_file, ".json")
    if not source.is_file():
        raise TaskExecutionError(f"Input file not found: {input_file}")
    if source.resolve() == target.resolve():
        raise TaskExecutionError("Input and output files must be different.")
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise TaskExecutionError("CSV needs a header row.")
        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
        if not {"category", "amount"}.issubset(set(reader.fieldnames)):
            raise TaskExecutionError("CSV must contain 'category' and 'amount' columns.")
        rows = list(reader)
    seen = set()
    unique_rows = []
    for row in rows:
        normalized = {str(k).strip().lower(): str(v).strip() for k, v in row.items() if k}
        signature = tuple(sorted(normalized.items()))
        if signature not in seen:
            seen.add(signature)
            unique_rows.append(normalized)
    totals = defaultdict(float)
    for index, row in enumerate(unique_rows, start=1):
        category = row.get("category", "").strip()
        if not category:
            raise TaskExecutionError(f"Row {index} has an empty category.")
        try:
            amount = float(row.get("amount", ""))
        except (TypeError, ValueError):
            raise TaskExecutionError(f"Row {index} has a non-numeric amount.") from None
        if not math.isfinite(amount):
            raise TaskExecutionError(f"Row {index} has a non-finite amount.")
        totals[category] += amount
    report = {
        "source_file": input_file,
        "output_file": output_file,
        "rows_read": len(rows),
        "rows_after_deduplication": len(unique_rows),
        "duplicates_removed": len(rows) - len(unique_rows),
        "category_totals": {key: round(value, 2) for key, value in sorted(totals.items())},
    }
    temporary = target.with_suffix(".tmp")
    try:
        temporary.write_text(json.dumps(report, indent=2), encoding="utf-8")
        temporary.replace(target)
    finally:
        if temporary.exists():
            temporary.unlink()
    return report

def verify_sales_report(output_file, expected):
    target = _safe_file(output_file, ".json")
    if not target.is_file():
        return {"verified": False, "checks": {"output_exists": False}, "errors": ["Output file is missing."]}
    try:
        actual = json.loads(target.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {"verified": False, "checks": {"valid_json": False}, "errors": [str(exc)]}
    checks = {
        "output_exists": True,
        "valid_json": True,
        "category_totals_match": actual.get("category_totals") == expected.get("category_totals"),
        "row_counts_consistent": (
            isinstance(actual.get("rows_read"), int)
            and isinstance(actual.get("rows_after_deduplication"), int)
            and isinstance(actual.get("duplicates_removed"), int)
            and actual["rows_read"] - actual["rows_after_deduplication"] == actual["duplicates_removed"]
        ),
    }
    return {"verified": all(checks.values()), "checks": checks, "errors": [key for key, value in checks.items() if not value]}
