"""
Streamlit dashboard for Automation Toolkit.
"""

import json
from pathlib import Path

import plotly.express as px
import polars as pl
import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Automation Toolkit",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Automation Toolkit")
st.caption("Upload CSV/Excel → Clean → Report → Alert via Telegram, Email or WhatsApp")

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("📤 Upload File")

uploaded = st.sidebar.file_uploader("Choose CSV or Excel", type=["csv", "xlsx", "xls"])

st.sidebar.markdown("---")
st.sidebar.subheader("🔔 Notifications")
notify_telegram = st.sidebar.checkbox("Telegram")
notify_email = st.sidebar.checkbox("Email")
notify_whatsapp = st.sidebar.checkbox("WhatsApp")
notify_target = ""
if notify_email or notify_whatsapp:
    notify_target = st.sidebar.text_input(
        "Email or phone (+56912345678)" if notify_whatsapp else "Email address"
    )

if st.sidebar.button("🚀 Process", type="primary", disabled=uploaded is None):
    with st.spinner("Processing..."):
        try:
            files = {"file": (uploaded.name, uploaded.getvalue())}
            data = {
                "notify_telegram": notify_telegram,
                "notify_email": notify_email,
                "notify_whatsapp": notify_whatsapp,
                "notify_target": notify_target,
            }
            resp = requests.post(f"{API_URL}/jobs/upload", files=files, data=data, timeout=60)
            if resp.status_code == 200:
                job = resp.json()
                st.sidebar.success(f"✅ Job #{job['job_id']} started!")
            else:
                st.sidebar.error(f"Error: {resp.text}")
        except Exception as e:
            st.sidebar.error(f"Cannot connect to API: {e}")

# ── Job history ───────────────────────────────────────────────────────────────
st.header("📋 Job History")

try:
    resp = requests.get(f"{API_URL}/jobs/", timeout=5)
    jobs = resp.json() if resp.status_code == 200 else []
except Exception:
    jobs = []
    st.warning("⚠️ API not running. Start it with: `uvicorn app.main:app --reload`")

if jobs:
    # Summary metrics
    total = len(jobs)
    done = sum(1 for j in jobs if j["status"] == "done")
    failed = sum(1 for j in jobs if j["status"] == "failed")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total jobs", total)
    c2.metric("Completed", done)
    c3.metric("Failed", failed)

    # Jobs table
    rows = []
    for j in jobs:
        rows.append({
            "ID": j["id"],
            "File": j["original_name"],
            "Status": j["status"],
            "Rows raw": j.get("rows_raw") or 0,
            "Rows clean": j.get("rows_clean") or 0,
            "Duplicates removed": j.get("duplicates_removed") or 0,
            "Nulls filled": j.get("nulls_filled") or 0,
            "Created": j.get("created_at", "")[:19],
        })
    df = pl.DataFrame(rows)
    st.dataframe(df.to_pandas(), use_container_width=True)

    # Chart: rows processed per job
    if done > 0:
        st.subheader("📊 Rows Processed per Job")
        done_jobs = [j for j in jobs if j["status"] == "done" and j.get("rows_raw")]
        if done_jobs:
            chart_data = {
                "Job": [f"#{j['id']} {j['original_name'][:20]}" for j in done_jobs],
                "Raw": [j["rows_raw"] for j in done_jobs],
                "Clean": [j["rows_clean"] for j in done_jobs],
            }
            fig = px.bar(
                chart_data, x="Job", y=["Raw", "Clean"],
                barmode="group",
                color_discrete_map={"Raw": "#ef4444", "Clean": "#22c55e"},
            )
            st.plotly_chart(fig, use_container_width=True)

    # Download report
    st.subheader("⬇️ Download Report")
    job_ids = [j["id"] for j in jobs if j["status"] == "done" and j.get("report_path")]
    if job_ids:
        selected = st.selectbox("Select job", job_ids, format_func=lambda x: f"Job #{x}")
        if st.button("Download Excel Report"):
            resp = requests.get(f"{API_URL}/jobs/{selected}/download", timeout=10)
            if resp.status_code == 200:
                st.download_button(
                    "📥 Save report",
                    data=resp.content,
                    file_name=f"report_job_{selected}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
else:
    st.info("No jobs yet. Upload a CSV or Excel file to get started.")

# ── Scheduled tasks ───────────────────────────────────────────────────────────
st.header("🗓️ Scheduled Tasks")

try:
    resp = requests.get(f"{API_URL}/tasks/", timeout=5)
    scheduled = resp.json() if resp.status_code == 200 else []
except Exception:
    scheduled = []

with st.expander("➕ Create new scheduled task"):
    with st.form("new_task"):
        t_name = st.text_input("Task name", placeholder="Weekly report")
        t_file = st.text_input("Filename (already uploaded)", placeholder="clients.csv")
        t_cron = st.text_input("Cron expression", placeholder="0 8 * * 1  (every Monday 8am)")
        t_telegram = st.checkbox("Notify Telegram")
        t_email = st.checkbox("Notify Email")
        t_whatsapp = st.checkbox("Notify WhatsApp")
        t_target = st.text_input("Email or phone (if email/whatsapp selected)")
        submitted = st.form_submit_button("Create task")
        if submitted and t_name and t_file and t_cron:
            try:
                payload = {
                    "name": t_name, "filename": t_file, "cron_expr": t_cron,
                    "notify_telegram": t_telegram, "notify_email": t_email,
                    "notify_whatsapp": t_whatsapp, "notify_target": t_target or None,
                }
                r = requests.post(f"{API_URL}/tasks/", json=payload, timeout=10)
                if r.status_code == 200:
                    st.success(f"✅ Task '{t_name}' created!")
                else:
                    st.error(r.text)
            except Exception as e:
                st.error(str(e))

if scheduled:
    for task in scheduled:
        status = "🟢 Active" if task["is_active"] else "🔴 Inactive"
        st.write(f"**#{task['id']} {task['name']}** — `{task['cron_expr']}` — {status}")
else:
    st.info("No scheduled tasks yet.")
