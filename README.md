# ⚙️ Automation Toolkit

**A full-stack data automation platform built with FastAPI and Streamlit.**

Automation Toolkit is a full-stack data automation platform built with FastAPI and Streamlit. It allows users to upload CSV/Excel files, automatically clean data, remove duplicates, fix missing values, generate downloadable reports, and optionally send alerts through multiple channels.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Polars](https://img.shields.io/badge/Polars-0.20-CD792C)](https://pola.rs)
[![Tests](https://img.shields.io/badge/Tests-16%20passing-22c55e)](tests/)
[![CI](https://github.com/Arcan17/automation-toolkit/actions/workflows/ci.yml/badge.svg)](https://github.com/Arcan17/automation-toolkit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What problem it solves

Data teams and businesses regularly receive messy CSV or Excel files:
- **Duplicate rows** that inflate counts and reports
- **Missing values** that break analysis and dashboards
- **Manual cleaning** that takes hours and introduces errors

Automation Toolkit automates the entire cleaning pipeline in seconds, generates a professional Excel report, and notifies your team automatically.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📤 **Upload** | Accept CSV or Excel files via dashboard or REST API |
| 🧹 **Deduplicate** | Remove fully duplicate rows automatically |
| 🩹 **Fill missing values** | Numbers → `0`, text → `N/A` |
| 📊 **Excel reports** | Two-sheet report: `Summary` (stats) + `Clean Data` (rows) |
| 🔔 **Multi-channel alerts** | Telegram, Email (SMTP), WhatsApp (Twilio) |
| 🗓️ **Scheduling** | Cron-based recurring tasks with APScheduler |
| 🖥️ **Dashboard** | Interactive Streamlit UI with KPIs, charts, and download buttons |
| 🔌 **REST API** | Full FastAPI backend with Swagger docs at `/docs` |
| ✅ **Tests** | 16 tests covering API endpoints and data processing logic |
| 🐳 **Docker** | One command to run the full stack |

---

## 🛠 Tech stack

| Layer | Technology | Purpose |
|---|---|---|
| **API** | FastAPI 0.111 | REST endpoints, request validation, Swagger docs |
| **Database** | SQLAlchemy + SQLite | Job tracking, task scheduling state |
| **Processing** | Polars 0.20 | High-performance DataFrame operations |
| **Reports** | openpyxl + xlsxwriter | Multi-sheet Excel generation |
| **Scheduler** | APScheduler (AsyncIO) | Cron-based recurring tasks |
| **Alerts** | python-telegram-bot, smtplib, Twilio | Multi-channel notifications |
| **Frontend** | Streamlit 1.35 + Plotly | Interactive dashboard |
| **Testing** | pytest + pytest-asyncio | Unit and integration tests |
| **Deploy** | Docker + Docker Compose | Containerized full-stack setup |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard :8501                 │
│   Sidebar (upload, demo, alerts) │ KPIs │ Charts │ History  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP requests
┌───────────────────────▼─────────────────────────────────────┐
│                    FastAPI Backend :8000                     │
│   /jobs/upload  │  /jobs/{id}  │  /jobs/{id}/download       │
│   /tasks/       │  /health     │  /docs (Swagger)           │
└──────────┬────────────┬────────────────────────────────────-┘
           │            │
    ┌──────▼──────┐ ┌───▼──────────────────────────────────┐
    │  SQLite DB  │ │        Services Layer                  │
    │  jobs       │ │  processor.py  →  Polars cleaning      │
    │  tasks      │ │  notifier.py   →  Telegram/Email/WA   │
    │  notifs     │ │  scheduler.py  →  APScheduler cron     │
    └─────────────┘ └──────────────────────────────────────-┘
```

---

## 📸 Screenshots

> Add screenshots here after running locally. See [What to screenshot](#-what-to-screenshot) at the bottom.

---

## 🔄 How it works

```
1. Upload a CSV or Excel file via the dashboard or API
2. The system removes duplicate rows automatically
3. Missing values are filled: 0 for numbers, "N/A" for text
4. A clean Excel report is generated with two sheets:
   - "Summary" — processing stats (rows, duplicates, missing values)
   - "Clean Data" — the actual cleaned rows
5. Optional alerts are sent through the configured channels
6. Scheduled tasks can run the same pipeline automatically on a cron schedule
```

**Example — input vs output:**

| name | email | age | score |
|---|---|---|---|
| Alice | alice@co.com | 28 | 9.5 |
| Bob | bob@co.com | 34 | 8.0 |
| Alice | alice@co.com | 28 | 9.5 | ← duplicate |
| Charlie | *(empty)* | 41 | *(empty)* |

→ After processing:

| name | email | age | score |
|---|---|---|---|
| Alice | alice@co.com | 28 | 9.5 |
| Bob | bob@co.com | 34 | 8.0 |
| Charlie | N/A | 41 | 0.0 |

Stats: `rows_raw=4`, `rows_clean=3`, `duplicates_removed=1`, `nulls_filled=2`

---

## 🚀 Installation

### Requirements
- Python 3.11+
- pip

### 1. Clone

```bash
git clone https://github.com/Arcan17/automation-toolkit.git
cd automation-toolkit
```

### 2. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure (optional — only required for alerts)

```bash
cp .env.example .env
# Edit .env with your credentials
```

---

## ▶️ Run locally

**Terminal 1 — API backend**
```bash
uvicorn app.main:app --reload
# Running at http://localhost:8000
```

**Terminal 2 — Streamlit dashboard**
```bash
streamlit run dashboard.py
# Running at http://localhost:8501
```

### Or with Docker Compose (recommended)

```bash
docker-compose up --build
```

- Dashboard → `http://localhost:8501`
- API docs  → `http://localhost:8000/docs`

---

## 📡 API docs

Full interactive Swagger docs: **`http://localhost:8000/docs`**

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET`    | `/health`              | API status, scheduler state, DB connectivity |
| `POST`   | `/jobs/upload`         | Upload and process a CSV/Excel file |
| `GET`    | `/jobs/`               | List all processing jobs |
| `GET`    | `/jobs/{id}`           | Get job status and stats |
| `GET`    | `/jobs/{id}/download`  | Download the Excel report |
| `POST`   | `/tasks/`              | Create a scheduled task |
| `GET`    | `/tasks/`              | List all scheduled tasks |
| `GET`    | `/tasks/{id}`          | Get task details |
| `DELETE` | `/tasks/{id}`          | Deactivate a scheduled task |

### Example — upload via curl

```bash
curl -X POST http://localhost:8000/jobs/upload \
  -F "file=@data/sample_demo.csv" \
  -F "notify_telegram=false"
```

Response:
```json
{
  "job_id": 1,
  "status": "processing",
  "filename": "sample_demo.csv"
}
```

Poll for result:
```bash
curl http://localhost:8000/jobs/1
```

```json
{
  "id": 1,
  "status": "done",
  "rows_raw": 13,
  "rows_clean": 11,
  "duplicates_removed": 2,
  "nulls_filled": 5,
  "report_path": "reports/report_1_20260514_120000.xlsx"
}
```

---

## 🔐 Environment variables

All credentials are optional. The app works fully without them (alerts are silently skipped).

```env
# Database (default: SQLite)
DATABASE_URL=sqlite:///./data/toolkit.db

# Telegram alerts
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Email alerts (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=you@gmail.com

# WhatsApp alerts (Twilio)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

Copy `.env.example` → `.env` and fill in what you need.

---

## 🎲 Demo file

A realistic sample CSV is included at `data/sample_demo.csv`:

```
13 rows total
2 duplicate rows
5 missing values (email, age, salary, score)
6 columns: name, email, department, age, salary, performance_score
```

**Try it in the dashboard:**
1. Click **⚡ Load sample CSV** in the sidebar
2. Click **🚀 Process file**
3. See the cleaning result and download the Excel report

---

## 📋 Example workflow

**Scenario:** Weekly HR report automation

1. Upload `employees.csv` via dashboard or API
2. System cleans 500 rows → removes 23 duplicates, fills 47 missing values
3. Excel report generated with Summary + Clean Data sheets
4. Telegram alert sent to HR channel: _"Job #42 complete — 500 rows processed"_
5. Scheduled task runs every Monday 8am automatically

---

## 📁 Project structure

```
automation-toolkit/
├── app/
│   ├── main.py              # FastAPI app, lifespan, CORS, tags metadata
│   ├── models.py            # SQLAlchemy models: Job, ScheduledTask, Notification
│   ├── schemas.py           # Pydantic response models
│   ├── database.py          # Engine, SessionLocal, init_db
│   ├── config.py            # Pydantic Settings (.env)
│   ├── routers/
│   │   ├── jobs.py          # Upload, status, download endpoints
│   │   └── tasks.py         # Scheduled task CRUD
│   └── services/
│       ├── processor.py     # Polars cleaning + Excel report generation
│       ├── notifier.py      # Telegram, Email, WhatsApp
│       └── scheduler.py     # APScheduler cron integration
├── dashboard.py             # Streamlit UI
├── data/
│   └── sample_demo.csv      # Demo file with duplicates and missing values
├── tests/
│   ├── test_api.py          # 9 FastAPI endpoint tests
│   └── test_processor.py    # 7 data processing unit tests
├── .github/
│   └── workflows/ci.yml     # GitHub Actions CI (runs tests on push)
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

---

## 🧪 Tests

```bash
pytest tests/ -v
```

```
tests/test_processor.py::test_clean_removes_duplicates      PASSED
tests/test_processor.py::test_clean_fills_nulls             PASSED
tests/test_processor.py::test_clean_strips_whitespace       PASSED
tests/test_processor.py::test_clean_stats_keys              PASSED
tests/test_processor.py::test_generate_report_creates_excel PASSED
tests/test_processor.py::test_process_csv                   PASSED
tests/test_processor.py::test_process_empty_csv             PASSED
tests/test_api.py::test_health                              PASSED
tests/test_api.py::test_root                                PASSED
tests/test_api.py::test_list_jobs_empty                     PASSED
tests/test_api.py::test_upload_csv                          PASSED
tests/test_api.py::test_upload_invalid_type                 PASSED
tests/test_api.py::test_get_job_not_found                   PASSED
tests/test_api.py::test_list_tasks_empty                    PASSED
tests/test_api.py::test_create_task_invalid_cron            PASSED
tests/test_api.py::test_get_task_not_found                  PASSED

16 passed
```

---

## 🔮 Future improvements

- [ ] PostgreSQL support for production deployments
- [ ] User authentication (API keys)
- [ ] Custom cleaning rules (configurable per upload)
- [ ] Email delivery of the Excel report as attachment
- [ ] Support for JSON and Parquet input formats
- [ ] Data preview before processing
- [ ] Webhook notifications (Slack, Discord)
- [ ] Cloud storage for reports (S3, GCS)

---

## 💼 Portfolio description

> Use this for LinkedIn, CV, GitHub, and freelance pitches.

**For developers / technical recruiters:**
> Built a full-stack data automation platform with FastAPI (REST API, Pydantic v2, SQLAlchemy), Streamlit, Polars for high-performance data cleaning, APScheduler for cron-based task scheduling, and multi-channel alert delivery (Telegram, SMTP, Twilio). Includes 16 tests, GitHub Actions CI, and Docker Compose setup.

**For clients / non-technical:**
> Automation Toolkit is a web tool that automatically cleans messy spreadsheets — removing duplicate records, fixing empty fields, and generating a professional Excel report. You upload a file, the system handles the rest, and you get an alert when it's ready.

---

## 📸 What to screenshot

For GitHub and LinkedIn:

1. **Dashboard overview** — `http://localhost:8501` with jobs table + KPIs
2. **Processing result** — the green success box after uploading `sample_demo.csv`
3. **Excel report** — open the downloaded `.xlsx` and show Summary + Clean Data sheets
4. **API docs** — `http://localhost:8000/docs` showing all endpoints
5. **Charts** — the two side-by-side charts (cleaning impact + issues resolved)

---

## 👤 Author

**Bastian Altamirano** — Python Backend Developer  
[GitHub](https://github.com/Arcan17) · [LinkedIn](https://linkedin.com/in/bastian-altamirano)

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

*Built with FastAPI · Streamlit · Polars · APScheduler · openpyxl*
