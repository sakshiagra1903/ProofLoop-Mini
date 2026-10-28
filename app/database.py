import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "proofloop.db"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS tasks (task_id TEXT PRIMARY KEY, task TEXT NOT NULL, operation TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, result_json TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS steps (id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL, attempt INTEGER NOT NULL, step_name TEXT NOT NULL, status TEXT NOT NULL, detail TEXT NOT NULL, evidence_json TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(task_id) REFERENCES tasks(task_id))")

def create_task(task_id, task, operation):
    with connect() as conn:
        conn.execute("INSERT INTO tasks(task_id, task, operation, status) VALUES (?, ?, ?, ?)", (task_id, task, operation, "running"))

def update_task(task_id, status, result):
    with connect() as conn:
        conn.execute("UPDATE tasks SET status=?, result_json=? WHERE task_id=?", (status, json.dumps(result), task_id))

def add_step(task_id, attempt, step_name, status, detail, evidence=None):
    with connect() as conn:
        conn.execute("INSERT INTO steps(task_id, attempt, step_name, status, detail, evidence_json) VALUES (?, ?, ?, ?, ?, ?)", (task_id, attempt, step_name, status, detail, json.dumps(evidence or {})))

def list_tasks():
    with connect() as conn:
        rows = conn.execute("SELECT task_id, task, operation, status, created_at, result_json FROM tasks ORDER BY created_at DESC").fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["result"] = json.loads(item.pop("result_json")) if item["result_json"] else None
        result.append(item)
    return result

def get_task(task_id):
    with connect() as conn:
        row = conn.execute("SELECT task_id, task, operation, status, created_at, result_json FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["result"] = json.loads(item.pop("result_json")) if item["result_json"] else None
        steps = conn.execute("SELECT attempt, step_name, status, detail, evidence_json, created_at FROM steps WHERE task_id=? ORDER BY id", (task_id,)).fetchall()
    item["steps"] = []
    for step in steps:
        current = dict(step)
        current["evidence"] = json.loads(current.pop("evidence_json") or "{}")
        item["steps"].append(current)
    return item
