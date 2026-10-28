# Architecture

## Request and execution path

1. FastAPI serves the static dashboard and validates API input with Pydantic.
2. `POST /api/tasks` accepts only the allowlisted `sales_report` operation and bounded retry values.
3. The engine resolves filenames inside the fixed `workspace/` directory; it rejects paths and unsupported extensions.
4. CSV input is checked for the required `category` and `amount` columns. Exact duplicate rows are removed, amounts must be numeric and finite, and category totals are calculated.
5. The JSON report is written to a temporary file and atomically replaced into the requested output path.
6. The verifier independently reopens the saved JSON and checks file existence, valid JSON, matching category totals and consistent row counts.
7. SQLite stores task state, final result, timestamps and per-step evidence.
8. `/api/analytics` derives dashboard counts from the task history. The frontend does not use mock task data.

## Frontend

`app/static/index.html`, `styles.css` and `app.js` provide a responsive dashboard. It talks to the same FastAPI origin, so local use does not require a separate frontend build or CORS setup. The task detail view exposes stored step evidence and verification checks.

## Additional API

- CSV upload is limited to 5 MB and UTF-8 text, and writes only inside the workspace.
- File listing and download endpoints expose only workspace CSV/JSON files and reject path-shaped names.
- The browser is not given arbitrary command execution or filesystem paths.

## Security and limitations

- No generated shell commands or Python code are executed.
- Retry count is bounded by request validation.
- SQLite is suitable for this local starter; multi-user concurrency and production operations need additional design.
- No LLM is called. Future Groq/Ollama integration should use strict structured output, explicit tool allowlists, timeouts, and independent verification rather than trusting model output.
- Do not expose the development server publicly without authentication, rate limiting and stronger isolation.
