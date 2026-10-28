# ProofLoop Mini

**A local-first workflow automation platform with CSV processing, independent output verification, execution history, and a FastAPI-powered dashboard.**

ProofLoop Mini helps users process CSV data, generate structured reports, and verify outputs through a simple web interface. It is built with Python and FastAPI, with a lightweight frontend and local data storage.

## ✨ Features

- **CSV Processing** — Load and process structured CSV files.
- **Data Cleaning** — Identify and remove duplicate records.
- **Sales Aggregation** — Summarize sales by category.
- **Report Generation** — Generate structured JSON reports.
- **Independent Verification** — Check processed outputs against verification rules.
- **Execution History** — Track workflow executions and their results.
- **Web Dashboard** — Interact with the application through a browser-based interface.
- **REST API** — Access supported functionality through FastAPI endpoints.
- **Automated Tests** — Test core processing and API behavior using pytest.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend logic |
| FastAPI | REST API and application server |
| SQLite | Local data storage |
| HTML5 | Frontend structure |
| CSS3 | Styling and layout |
| JavaScript | Frontend interactions |
| pytest | Automated testing |

## 📁 Project Structure

```text
ProofLoop-Mini/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── engine.py
│   ├── models.py
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── docs/
│   └── ARCHITECTURE.md
├── tests/
│   ├── test_api.py
│   └── test_engine.py
├── workspace/
│   ├── ProofLoop-Sample-Sales.csv
│   ├── sales.csv
│   └── sales_report.json
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or newer
- Git
- A terminal such as PowerShell or Command Prompt

### 1. Clone the repository

```bash
git clone https://github.com/sakshiagra1903/ProofLoop-Mini.git
cd ProofLoop-Mini
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can run the commands below instead:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the application

```bash
python -m uvicorn app.main:app --reload
```

Open the local address printed in the terminal. By default, Uvicorn uses:

`http://127.0.0.1:8000`

FastAPI's interactive API documentation is generally available at:

`http://127.0.0.1:8000/docs`

## 🧪 Run Tests

From the project root, execute:

```bash
python -m pytest -v
```

The test suite includes API and core-engine tests.

## 🔌 API Documentation

Once the server is running, open `/docs` on your local application address to inspect the available API endpoints and try supported requests.



## 🗺️ Future Improvements

- More configurable verification rules
- Improved workflow monitoring and error reporting
- Additional CSV validation options
- Exportable execution summaries
- Enhanced dashboard visualizations

## 👩‍💻 Author

**Sakshi Agrawal**
<img width="1920" height="1080" alt="Screenshot 2026-10-28 114346" src="https://github.com/user-attachments/assets/1e4c520a-4206-436d-b0fb-b8db56b59e97" />
<img width="1920" height="1080" alt="Screenshot 2026-10-28 114346" src="https://github.com/user-attachments/assets/a87c3635-897c-40bf-addf-eddab83fe15d" />

GitHub: [@sakshiagra1903](https://github.com/sakshiagra1903)
