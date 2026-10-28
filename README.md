# ProofLoop Mini — Verified Automation Workspace

ProofLoop Mini is a local-first, full-stack starter for **self-verifying workflows**. The project now includes a responsive browser dashboard and a FastAPI + SQLite backend. It deliberately uses a deterministic, allowlisted workflow rather than claiming to use an LLM that is not configured.

## Features

- **Modern dashboard:** workspace pulse metrics, recent executions, task history, report ledger and responsive layout.
- **End-to-end workflow UI:** launch a sales report, select a CSV from the workspace, name the JSON output, and set a bounded retry count.
- **Local CSV upload:** upload UTF-8 CSVs (up to 5 MB) directly to the workspace.
- **Safe processing:** filenames only (no arbitrary paths), allowlisted `sales_report` operation, numeric/finite amount validation, exact duplicate removal, atomic JSON output.
- **Independent verification:** reopens the saved JSON and validates output existence, JSON format, category totals and row-count consistency.
- **Execution trace:** SQLite task history and per-step evidence, inspectable in the UI and API.
- **Evidence/report download:** download generated JSON and inspect verification checks.
- **Real analytics:** counts and totals are derived from persisted task records; no seeded/mock dashboard numbers.
- **API docs and tests:** OpenAPI at `/docs`; pytest tests cover validation and engine behavior.

## Run on Windows PowerShell

Python 3.12 is recommended (Python 3.11+ should also work with compatible dependencies).

```powershell
cd ProofLoop-Mini
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

If PowerShell blocks virtual-environment activation, run this in the same terminal and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Open **http://127.0.0.1:8000** for the dashboard, or **http://127.0.0.1:8000/docs** for API docs. The backend serves the frontend itself, so no separate frontend server is required.

## First workflow

1. Open the dashboard and click **Run a workflow**.
2. Choose `sales.csv`, which is included in `workspace/`, or upload another CSV.
3. Keep the default output name `sales_report.json` or enter another `.json` filename.
4. Click **Run & verify**.
5. Inspect the execution timeline, row counts, category totals, evidence and verification checks. Use **Download JSON report** to retrieve the result.

Input CSV must have `category` and `amount` columns. Output files are stored in `workspace/`. The SQLite database is stored at `app/proofloop.db` and is created automatically on first run.

## Tests

In a second terminal, activate the virtual environment and run:

```powershell
python -m pytest -q
```

## API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | Dashboard frontend |
| `GET /api/health` | API/database/mode health |
| `GET /api/files` | List workspace CSVs and JSON reports |
| `POST /api/upload` | Upload a CSV into the workspace (max 5 MB) |
| `GET /api/files/{filename}` | Download a workspace CSV/JSON file |
| `POST /api/tasks` | Execute and verify an allowlisted task |
| `GET /api/tasks` | List persisted task history |
| `GET /api/tasks/{task_id}` | Task result and step evidence |
| `GET /api/analytics` | Computed dashboard metrics |

## Important scope and security notes

- The current supported operation is **sales_report**. The app is not yet a general-purpose autonomous agent.
- LLM planning (Groq/Ollama), authentication, multi-user deployment, background workers and additional workflow types are not implemented. The dashboard labels the current mode as deterministic/local rather than pretending these features exist.
- This is designed for local development. Do not expose the development server to the public internet without authentication, rate limiting, stronger isolation and deployment hardening.
