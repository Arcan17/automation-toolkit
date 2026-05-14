# ⚙️ Automation Toolkit

**A full-stack data automation platform built with FastAPI and Streamlit.**

Upload CSV or Excel files → clean data automatically → generate downloadable reports → send alerts through Telegram, Email or WhatsApp.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)](https://streamlit.io)
[![Polars](https://img.shields.io/badge/Polars-0.20-orange)](https://pola.rs)
[![Tests](https://img.shields.io/badge/Tests-16%20passing-brightgreen)](#tests)

---

## What it does

| Feature | Description |
|---|---|
| 📤 Upload | Accept CSV or Excel files up to 10 MB |
| 🧹 Clean | Remove duplicate rows, strip whitespace, fill missing values |
| 📊 Report | Generate a formatted Excel report with clean + stats sheets |
| 🔔 Alerts | Send processing results via Telegram, Email (SMTP) or WhatsApp (Twilio) |
| 🗓️ Schedule | Set recurring tasks with cron expressions (APScheduler) |
| 🖥️ Dashboard | Interactive Streamlit UI — no code needed to use it |
| 🔌 API | Full REST API with Swagger docs at `/docs` |

---

## How it works

```
1. Upload a CSV or Excel file via the dashboard or API
2. Duplicate rows are detected and removed automatically
3. Missing values are filled: 0 for numbers, "N/A" for text columns
4. A clean Excel report is generated and stored on the server
5. Optional alerts are sent through the configured channels
6. Scheduled tasks run the same pipeline automatically on a cron schedule
```

---

## Tech stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI, SQLAlchemy, SQLite |
| **Processing** | Polars, openpyxl, xlsxwriter |
| **Scheduler** | APScheduler (AsyncIO) |
| **Alerts** | python-telegram-bot, smtplib, Twilio |
| **Frontend** | Streamlit, Plotly |
| **Testing** | pytest, pytest-asyncio, unittest.mock |
| **Deploy** | Docker, Docker Compose |

---

## Quick start

### 1. Clone & install

```bash
git clone https://github.com/Arcan17/automation-toolkit.git
cd automation-toolkit
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure (optional — required only for alerts)

```bash
cp .env.example .env
# Edit .env with your keys:
# TELEGRAM_BOT_TOKEN=...
# SMTP_USER=...   SMTP_PASSWORD=...
# TWILIO_ACCOUNT_SID=...   TWILIO_AUTH_TOKEN=...
```

### 3. Run

**Terminal 1 — API**
```bash
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

**Terminal 2 — Dashboard**
```bash
streamlit run dashboard.py
# → http://localhost:8501
```

### Or with Docker Compose

```bash
docker-compose up --build
# API   → http://localhost:8000/docs
# UI    → http://localhost:8501
```

---

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/jobs/upload` | Upload and process a CSV/Excel file |
| `GET`  | `/jobs/` | List all processing jobs |
| `GET`  | `/jobs/{id}` | Get job status and stats |
| `GET`  | `/jobs/{id}/download` | Download the Excel report |
| `POST` | `/tasks/` | Create a scheduled task |
| `GET`  | `/tasks/` | List all scheduled tasks |
| `GET`  | `/tasks/{id}` | Get task details |
| `DELETE` | `/tasks/{id}` | Delete a scheduled task |
| `GET`  | `/health` | Health check |

Full interactive docs: `http://localhost:8000/docs`

### Example — upload via curl

```bash
curl -X POST http://localhost:8000/jobs/upload \
  -F "file=@clients.csv" \
  -F "notify_telegram=true"
```

Response:
```json
{
  "job_id": 1,
  "status": "processing",
  "filename": "clients.csv"
}
```

---

## Data cleaning logic

Given this input:

| name | email | age | score |
|---|---|---|---|
| Alice | alice@example.com | 28 | 9.5 |
| Bob | bob@example.com | 34 | 8.0 |
| Alice | alice@example.com | 28 | 9.5 | ← duplicate |
| Charlie | *(empty)* | 41 | *(empty)* |

The toolkit produces:

| name | email | age | score |
|---|---|---|---|
| Alice | alice@example.com | 28 | 9.5 |
| Bob | bob@example.com | 34 | 8.0 |
| Charlie | N/A | 41 | 0.0 |

Stats returned: `rows_raw=4`, `rows_clean=3`, `duplicates_removed=1`, `nulls_filled=2`

---

## Project structure

```
automation-toolkit/
├── app/
│   ├── main.py              # FastAPI app + lifespan
│   ├── models.py            # SQLAlchemy models (Job, ScheduledTask, Notification)
│   ├── database.py          # Engine + session
│   ├── config.py            # Pydantic Settings (.env)
│   ├── routers/
│   │   ├── jobs.py          # Upload, status, download
│   │   └── tasks.py         # CRUD for scheduled tasks
│   └── services/
│       ├── processor.py     # Polars cleaning + Excel report
│       ├── notifier.py      # Telegram, Email, WhatsApp
│       └── scheduler.py     # APScheduler integration
├── dashboard.py             # Streamlit UI
├── tests/
│   ├── test_api.py          # FastAPI endpoint tests (9 tests)
│   └── test_processor.py    # Processor unit tests (7 tests)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Tests

```bash
pytest tests/ -v
```

```
tests/test_processor.py::test_clean_removes_duplicates    PASSED
tests/test_processor.py::test_clean_fills_nulls           PASSED
tests/test_processor.py::test_clean_strips_whitespace     PASSED
tests/test_processor.py::test_clean_stats_keys            PASSED
tests/test_processor.py::test_generate_report_creates_excel PASSED
tests/test_processor.py::test_process_csv                 PASSED
tests/test_processor.py::test_process_empty_csv           PASSED
tests/test_api.py::test_health                            PASSED
tests/test_api.py::test_root                              PASSED
tests/test_api.py::test_list_jobs_empty                   PASSED
tests/test_api.py::test_upload_csv                        PASSED
tests/test_api.py::test_upload_invalid_type               PASSED
tests/test_api.py::test_get_job_not_found                 PASSED
tests/test_api.py::test_list_tasks_empty                  PASSED
tests/test_api.py::test_create_task_invalid_cron          PASSED
tests/test_api.py::test_get_task_not_found                PASSED

16 passed in 0.97s
```

---

## Notifications

Configure the channels you want in `.env`:

**Telegram**
```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

**Email (Gmail)**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=you@gmail.com
```

**WhatsApp (Twilio)**
```env
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

---

## Scheduled tasks

Create a task via the dashboard or API to run a file automatically:

```json
POST /tasks/
{
  "name": "Weekly sales report",
  "filename": "sales.csv",
  "cron_expr": "0 8 * * 1",
  "notify_telegram": true
}
```

Cron examples:
- `0 9 * * 1-5` — weekdays at 9 am
- `0 8 1 * *` — 1st of every month at 8 am
- `0 8 * * 1` — every Monday at 8 am

---

## Use cases

- **Data teams** — automate weekly/monthly data cleaning pipelines
- **Small businesses** — clean customer or sales CSVs without writing code
- **Freelancers** — offer data cleaning as a service with this backend
- **Developers** — extend with custom cleaning rules or new alert channels

---

## Author

**Bastian Altamirano** — Python Backend Developer  
[GitHub](https://github.com/Arcan17) · [LinkedIn](https://linkedin.com/in/bastian-altamirano)

---

*Built with FastAPI · Streamlit · Polars · APScheduler*
