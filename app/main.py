from contextlib import asynccontextmanager
from uuid import uuid4
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app import database
from app.engine import TaskExecutionError, run_sales_report, verify_sales_report, WORKSPACE
from app.models import TaskRequest, TaskCreated

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield

app = FastAPI(title="ProofLoop Mini", description="Self-verifying task execution starter MVP", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.mount("/static", StaticFiles(directory=Path(__file__).resolve().parent / "static"), name="static")
# Initialize schema on import as well as at startup so local test clients and CLI tools work.
database.init_db()

@app.get("/")
def home():
    index = Path(__file__).resolve().parent / "static" / "index.html"
    return FileResponse(index)

@app.get("/api/health")
def health():
    return {"api": "healthy", "database": "sqlite", "llm": "not_configured", "mode": "deterministic_local", "version": "0.2.0"}

@app.post("/api/tasks", response_model=TaskCreated)
def create_task(request: TaskRequest):
    task_id = str(uuid4())
    database.create_task(task_id, request.task, request.operation)
    status = "failed"
    result = {"verified": False, "attempts": 0, "message": ""}
    for attempt in range(request.max_retries + 1):
        database.add_step(task_id, attempt + 1, "validate_and_plan", "passed", "Request validated; operation is allowlisted.", {"operation": request.operation, "input_file": request.input_file, "output_file": request.output_file})
        try:
            report = run_sales_report(request.input_file, request.output_file)
            database.add_step(task_id, attempt + 1, "execute_sales_report", "passed", "Processed CSV and wrote JSON report.", {"rows_read": report["rows_read"], "rows_after_deduplication": report["rows_after_deduplication"], "duplicates_removed": report["duplicates_removed"]})
            verification = verify_sales_report(request.output_file, report)
            database.add_step(task_id, attempt + 1, "verify_output", "passed" if verification["verified"] else "failed", "Independent output verification completed.", verification)
            result = {"verified": verification["verified"], "attempts": attempt + 1, "report": report, "verification": verification}
            if verification["verified"]:
                status = "succeeded"
                break
            result["message"] = "Output verification failed; task not marked successful."
        except TaskExecutionError as exc:
            result = {"verified": False, "attempts": attempt + 1, "message": str(exc)}
            database.add_step(task_id, attempt + 1, "execute_sales_report", "failed", str(exc), {"retry_attempted": False})
            break
        except Exception as exc:
            result = {"verified": False, "attempts": attempt + 1, "message": f"Unexpected error: {type(exc).__name__}"}
            database.add_step(task_id, attempt + 1, "execute_sales_report", "failed", f"Unexpected error: {type(exc).__name__}")
            break
    database.update_task(task_id, status, result)
    message = "Task completed and verified." if status == "succeeded" else result.get("message", "Task failed verification.")
    return TaskCreated(task_id=task_id, status=status, message=message)

@app.get("/api/tasks")
def list_tasks():
    return {"tasks": database.list_tasks()}

@app.get("/api/tasks/{task_id}")
def task_detail(task_id: str):
    item = database.get_task(task_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return item


@app.get("/api/files")
def list_workspace_files():
    """List safe CSV inputs and generated JSON reports in the workspace."""
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    files = []
    for path in sorted(WORKSPACE.iterdir(), key=lambda p: p.name.lower()):
        if path.is_file() and path.suffix.lower() in {".csv", ".json"} and not path.name.endswith(".tmp"):
            try:
                files.append({"name": path.name, "kind": "input" if path.suffix.lower() == ".csv" else "report", "size": path.stat().st_size})
            except OSError:
                continue
    return {"files": files}

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a bounded CSV file into the isolated workspace."""
    original_name = file.filename or ""
    name = Path(original_name).name
    if not name or name != original_name or "\\" in name or name in {".", ".."} or not name.lower().endswith(".csv") or not all(c.isalnum() or c in "._- " for c in name):
        raise HTTPException(status_code=400, detail="Choose a CSV file with a simple filename.")
    data = await file.read(5 * 1024 * 1024 + 1)
    await file.close()
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded CSV is empty.")
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="CSV files must be 5 MB or smaller.")
    # Restrict uploads to UTF-8-compatible CSV text before storing.
    try:
        data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV must be encoded as UTF-8.") from None
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    safe_name = "_".join(name.strip().split())
    target = (WORKSPACE / safe_name).resolve()
    if target.parent != WORKSPACE.resolve():
        raise HTTPException(status_code=400, detail="Invalid filename.")
    target.write_bytes(data)
    return {"filename": safe_name, "size": len(data), "message": "CSV uploaded to the local workspace."}

@app.get("/api/files/{filename}")
def download_workspace_file(filename: str):
    """Download a workspace CSV or generated JSON without accepting paths."""
    if Path(filename).name != filename or filename in {".", ".."} or Path(filename).suffix.lower() not in {".csv", ".json"}:
        raise HTTPException(status_code=400, detail="Only workspace CSV and JSON files can be downloaded.")
    target = (WORKSPACE / filename).resolve()
    if target.parent != WORKSPACE.resolve() or not target.is_file():
        raise HTTPException(status_code=404, detail="Workspace file not found.")
    return FileResponse(target, filename=target.name)

@app.get("/api/analytics")
def analytics():
    """Compute dashboard analytics from persisted task records, not mock data."""
    history = database.list_tasks()
    succeeded = [t for t in history if t["status"] == "succeeded"]
    failed = [t for t in history if t["status"] == "failed"]
    checks = rows = duplicates = 0
    for task in succeeded:
        result = task.get("result") or {}
        verification = result.get("verification") or {}
        checks += len(verification.get("checks") or {})
        report = result.get("report") or {}
        rows += int(report.get("rows_read", 0) or 0)
        duplicates += int(report.get("duplicates_removed", 0) or 0)
    total = len(history)
    return {"total_tasks": total, "verified_tasks": len(succeeded), "failed_tasks": len(failed), "success_rate": round(len(succeeded) * 100 / total, 1) if total else 0, "verification_checks": checks, "rows_processed": rows, "duplicates_removed": duplicates}
