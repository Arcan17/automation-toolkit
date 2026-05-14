"""
Streamlit dashboard for Automation Toolkit.
Upload CSV/Excel → Clean → Report → Alert
"""

import time
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

API_URL = "http://localhost:8000"
SAMPLE_CSV_PATH = Path("data/sample_demo.csv")

st.set_page_config(
    page_title="Automation Toolkit",
    page_icon="⚙️",
    layout="wide",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Dark-theme cards */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 18px;
}
.card h4 {
    color: #94a3b8;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 10px 0;
}
/* Success result box */
.result-box {
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.35);
    border-radius: 10px;
    padding: 18px 22px;
    margin: 14px 0;
}
.result-box h4 { color: #4ade80; margin: 0 0 10px 0; font-size: 1rem; }
.result-box p  { margin: 4px 0; color: #d1fae5; font-size: 0.9rem; }
/* Error box */
.error-box {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 10px;
    padding: 16px 20px;
    margin: 12px 0;
}
.error-box p { color: #fca5a5; margin: 0; font-size: 0.9rem; }
/* Demo badge */
.demo-badge {
    display: inline-block;
    background: rgba(251,191,36,0.15);
    border: 1px solid rgba(251,191,36,0.4);
    color: #fbbf24;
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.05em;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Automation Toolkit")
    st.markdown(
        "Upload **CSV or Excel** files to automatically clean data, "
        "remove duplicates, fix missing values, generate downloadable "
        "reports, and send alerts."
    )
    st.markdown("---")

    # ── Demo file ─────────────────────────────────────────────────────────────
    st.subheader("🎯 Quick demo")
    st.caption("13 rows · 2 duplicates · 5 missing values · realistic data")
    if st.button("⚡ Load sample CSV", use_container_width=True):
        if SAMPLE_CSV_PATH.exists():
            st.session_state["demo_bytes"] = SAMPLE_CSV_PATH.read_bytes()
            st.session_state["demo_name"]  = "sample_demo.csv"
        else:
            # Inline fallback
            sample = (
                "name,email,department,age,salary,score\n"
                "Alice,alice@co.com,Engineering,28,75000,9.2\n"
                "Bob,bob@co.com,Marketing,34,62000,8.5\n"
                "Alice,alice@co.com,Engineering,28,75000,9.2\n"
                "Charlie,,Operations,41,,7.8\n"
                "Diana,diana@co.com,Engineering,,88000,9.7\n"
            )
            st.session_state["demo_bytes"] = sample.encode()
            st.session_state["demo_name"]  = "sample_demo.csv"
        st.success("Sample loaded ✓")

    st.markdown("---")

    # ── Upload ────────────────────────────────────────────────────────────────
    st.subheader("📤 Upload your file")
    uploaded = st.file_uploader(
        "CSV or Excel",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
        help="CSV (.csv) or Excel (.xlsx / .xls) — max 10 MB",
    )

    file_bytes, file_name = None, None
    if uploaded:
        file_bytes = uploaded.getvalue()
        file_name  = uploaded.name
        st.session_state.pop("demo_bytes", None)
    elif "demo_bytes" in st.session_state:
        file_bytes = st.session_state["demo_bytes"]
        file_name  = st.session_state["demo_name"]

    if file_bytes:
        is_demo = "demo_bytes" in st.session_state and not uploaded
        badge   = ' <span class="demo-badge">DEMO</span>' if is_demo else ""
        st.markdown(f"📄 **{file_name}**{badge}", unsafe_allow_html=True)

    st.markdown("---")

    # ── Notifications ─────────────────────────────────────────────────────────
    st.subheader("🔔 Notifications")
    st.caption("Configure in `.env` to enable real alerts.")

    notify_telegram = st.checkbox("Telegram")
    notify_email    = st.checkbox("Email")
    notify_whatsapp = st.checkbox("WhatsApp")
    notify_target   = ""
    if notify_email or notify_whatsapp:
        notify_target = st.text_input(
            "Email or phone (+56912345678)" if notify_whatsapp else "Email address"
        )

    # Notification status preview
    active = [
        ch for ch, on in [("Telegram", notify_telegram), ("Email", notify_email), ("WhatsApp", notify_whatsapp)]
        if on
    ]
    if active:
        for ch in active:
            st.caption(f"✅ {ch}: enabled")
    else:
        st.caption("ℹ️ No alerts — file will be processed silently.")

    st.markdown("---")

    process_clicked = st.button(
        "🚀 Process file",
        type="primary",
        disabled=file_bytes is None,
        use_container_width=True,
    )
    if file_bytes is None:
        st.caption("⬆️ Load a file or click **Load sample CSV** above.")


# ─────────────────────────────────────────────────────────────────────────────
# Hero / How it works
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="card">
  <h4>ℹ️ How it works</h4>
  <ol style="margin:0; padding-left:20px; color:#cbd5e1; font-size:0.92rem; line-height:1.9">
    <li>Upload a CSV or Excel file <em>(or use the sample)</em></li>
    <li>Duplicate rows are detected and removed automatically</li>
    <li>Missing values are filled — <code>0</code> for numbers, <code>N/A</code> for text</li>
    <li>A clean Excel report is generated with a <strong>Summary</strong> sheet and a <strong>Clean Data</strong> sheet</li>
    <li>Optional alerts sent via Telegram, Email or WhatsApp when complete</li>
  </ol>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Process action
# ─────────────────────────────────────────────────────────────────────────────
if process_clicked and file_bytes:
    with st.spinner(f"Processing **{file_name}**…"):
        try:
            resp = requests.post(
                f"{API_URL}/jobs/upload",
                files={"file": (file_name, file_bytes)},
                data={
                    "notify_telegram":  str(notify_telegram).lower(),
                    "notify_email":     str(notify_email).lower(),
                    "notify_whatsapp":  str(notify_whatsapp).lower(),
                    "notify_target":    notify_target,
                },
                timeout=60,
            )

            if resp.status_code == 200:
                job_id = resp.json()["job_id"]
                job = {}
                for _ in range(30):
                    time.sleep(0.5)
                    poll = requests.get(f"{API_URL}/jobs/{job_id}", timeout=5)
                    if poll.status_code == 200:
                        job = poll.json()
                        if job["status"] in ("done", "failed"):
                            break

                if job.get("status") == "done":
                    rows_raw   = job.get("rows_raw") or 0
                    rows_clean = job.get("rows_clean") or 0
                    dupes      = job.get("duplicates_removed") or 0
                    nulls      = job.get("nulls_filled") or 0
                    pct_clean  = round(rows_clean / rows_raw * 100, 1) if rows_raw else 100

                    notif_line = (
                        "🔔 Alert sent via " + ", ".join(active)
                        if active else "🔕 No alerts configured"
                    )

                    st.markdown(f"""
<div class="result-box">
  <h4>✅ File processed successfully — Job #{job_id}</h4>
  <p>📄 <strong>{file_name}</strong></p>
  <p>📥 Original rows: <strong>{rows_raw}</strong></p>
  <p>✨ Clean rows: <strong>{rows_clean}</strong> ({pct_clean}% of original)</p>
  <p>🗑️ Duplicates removed: <strong>{dupes}</strong></p>
  <p>🩹 Missing values fixed: <strong>{nulls}</strong></p>
  <p>📊 Report: <strong>Ready to download</strong> (Summary + Clean Data sheets)</p>
  <p>{notif_line}</p>
</div>
""", unsafe_allow_html=True)

                    dl = requests.get(f"{API_URL}/jobs/{job_id}/download", timeout=10)
                    if dl.status_code == 200:
                        fname_out = file_name.rsplit(".", 1)[0]
                        st.download_button(
                            f"⬇️ Download cleaned report — {file_name}",
                            data=dl.content,
                            file_name=f"cleaned_{fname_out}_job{job_id}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                        )
                elif job.get("status") == "failed":
                    st.markdown(f"""
<div class="error-box">
  <p>❌ <strong>Job #{job_id} failed.</strong> {job.get('error', 'Unknown error.')}</p>
</div>
""", unsafe_allow_html=True)
            else:
                body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                detail = body.get("detail", resp.text)
                st.markdown(f'<div class="error-box"><p>❌ API error {resp.status_code}: {detail}</p></div>',
                            unsafe_allow_html=True)
        except requests.exceptions.ConnectionError:
            st.markdown('<div class="error-box"><p>❌ Cannot connect to API. Run: <code>uvicorn app.main:app --reload</code></p></div>',
                        unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box"><p>❌ Unexpected error: {e}</p></div>',
                        unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Job history
# ─────────────────────────────────────────────────────────────────────────────
st.header("📋 Job History")

api_ok = True
try:
    resp = requests.get(f"{API_URL}/jobs/", timeout=4)
    jobs = resp.json() if resp.status_code == 200 else []
except Exception:
    jobs = []
    api_ok = False

if not api_ok:
    st.markdown('<div class="error-box"><p>⚠️ API not reachable. Start the backend: <code>uvicorn app.main:app --reload</code></p></div>',
                unsafe_allow_html=True)
elif jobs:
    done_jobs    = [j for j in jobs if j["status"] == "done"]
    total        = len(jobs)
    failed       = sum(1 for j in jobs if j["status"] == "failed")
    total_rows   = sum(j.get("rows_raw") or 0 for j in done_jobs)
    total_dupes  = sum(j.get("duplicates_removed") or 0 for j in done_jobs)
    total_nulls  = sum(j.get("nulls_filled") or 0 for j in done_jobs)
    reports      = sum(1 for j in done_jobs if j.get("report_path"))

    # KPI row 1
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Jobs",  total)
    c2.metric("Completed",   len(done_jobs))
    c3.metric("Failed",      failed,
              delta=f"+{failed}" if failed else None, delta_color="inverse")

    # KPI row 2
    c4, c5, c6, c7 = st.columns(4)
    c4.metric("Rows Processed",       total_rows)
    c5.metric("Duplicates Removed",   total_dupes)
    c6.metric("Missing Values Fixed", total_nulls)
    c7.metric("Reports Generated",    reports)

    # Table
    import polars as pl
    rows = []
    for j in jobs:
        raw   = j.get("rows_raw") or 0
        clean = j.get("rows_clean") or 0
        pct   = f"{round(clean/raw*100)}%" if raw else "—"
        rows.append({
            "#":                    j["id"],
            "File":                 j["original_name"],
            "Status": {
                "done":       "✅ Done",
                "failed":     "❌ Failed",
                "processing": "⏳ Processing",
            }.get(j["status"], j["status"]),
            "Original Rows":        raw,
            "Clean Rows":           clean,
            "Quality":              pct,
            "Duplicates Removed":   j.get("duplicates_removed") or 0,
            "Missing Values Fixed": j.get("nulls_filled") or 0,
            "Date":                 j.get("created_at", "")[:19].replace("T", " "),
        })
    st.dataframe(pl.DataFrame(rows).to_pandas(), use_container_width=True, hide_index=True)

    # Download buttons
    reportable = [j for j in done_jobs if j.get("report_path")]
    if reportable:
        st.subheader("⬇️ Download Reports")
        cols = st.columns(min(len(reportable), 4))
        for i, j in enumerate(reportable):
            with cols[i % 4]:
                dl = requests.get(f"{API_URL}/jobs/{j['id']}/download", timeout=10)
                if dl.status_code == 200:
                    fname_base = j["original_name"].rsplit(".", 1)[0]
                    st.download_button(
                        f"⬇️ {j['original_name']} (Job #{j['id']})",
                        data=dl.content,
                        file_name=f"cleaned_{fname_base}_job{j['id']}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{j['id']}",
                        use_container_width=True,
                    )

    # ── Charts ────────────────────────────────────────────────────────────────
    chart_jobs = [j for j in done_jobs if j.get("rows_raw")]
    if chart_jobs:
        col_left, col_right = st.columns(2)

        # Chart 1: Rows before vs after
        with col_left:
            st.subheader("📊 Data Cleaning Impact per Job")
            labels = [f"#{j['id']} {j['original_name'][:16]}" for j in chart_jobs]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name="Original Rows", x=labels,
                y=[j["rows_raw"]  for j in chart_jobs],
                marker_color="#ef4444",
            ))
            fig.add_trace(go.Bar(
                name="Clean Rows", x=labels,
                y=[j["rows_clean"] for j in chart_jobs],
                marker_color="#22c55e",
            ))
            fig.update_layout(
                barmode="group", paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(title="", color="#94a3b8"),
                yaxis=dict(title="Rows", color="#94a3b8", gridcolor="rgba(255,255,255,0.07)"),
                font=dict(color="#cbd5e1"),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Chart 2: Issues resolved per job (stacked)
        with col_right:
            st.subheader("🔧 Issues Resolved per Job")
            labels2 = [f"#{j['id']} {j['original_name'][:16]}" for j in chart_jobs]
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                name="Duplicates Removed",
                x=labels2,
                y=[j.get("duplicates_removed") or 0 for j in chart_jobs],
                marker_color="#f59e0b",
            ))
            fig2.add_trace(go.Bar(
                name="Missing Values Fixed",
                x=labels2,
                y=[j.get("nulls_filled") or 0 for j in chart_jobs],
                marker_color="#6366f1",
            ))
            fig2.update_layout(
                barmode="stack", paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(title="", color="#94a3b8"),
                yaxis=dict(title="Issues", color="#94a3b8", gridcolor="rgba(255,255,255,0.07)"),
                font=dict(color="#cbd5e1"),
            )
            st.plotly_chart(fig2, use_container_width=True)

else:
    st.markdown("""
<div class="card" style="text-align:center; padding:32px;">
  <p style="color:#64748b; font-size:1.1rem; margin:0">
    No jobs yet.<br>
    <span style="font-size:0.9rem">Use the sidebar to upload a file or click
    <strong>⚡ Load sample CSV</strong> for a quick demo.</span>
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Scheduled tasks
# ─────────────────────────────────────────────────────────────────────────────
st.header("🗓️ Scheduled Tasks")

try:
    resp      = requests.get(f"{API_URL}/tasks/", timeout=4)
    scheduled = resp.json() if resp.status_code == 200 else []
except Exception:
    scheduled = []

with st.expander("➕ Create a new scheduled task"):
    st.caption(
        "Automatically process a file on a recurring schedule and optionally send alerts."
    )
    with st.form("new_task"):
        col1, col2 = st.columns(2)
        with col1:
            t_name = st.text_input("Task name", placeholder="Weekly sales report")
            t_file = st.text_input("Filename (must already be uploaded)", placeholder="clients.csv")
        with col2:
            t_cron = st.text_input("Cron expression", placeholder="0 8 * * 1")
            st.caption(
                "Examples: `0 8 * * 1` Mon 8am · "
                "`0 9 * * 1-5` weekdays 9am · "
                "`0 8 1 * *` 1st of month"
            )
        tc1, tc2, tc3 = st.columns(3)
        t_telegram  = tc1.checkbox("Telegram")
        t_email     = tc2.checkbox("Email")
        t_whatsapp  = tc3.checkbox("WhatsApp")
        t_target    = st.text_input("Email or phone (if Email/WhatsApp selected)")

        if st.form_submit_button("✅ Create task", type="primary"):
            if not (t_name and t_file and t_cron):
                st.warning("Name, filename and cron expression are required.")
            else:
                try:
                    r = requests.post(f"{API_URL}/tasks/", json={
                        "name": t_name, "filename": t_file, "cron_expr": t_cron,
                        "notify_telegram": t_telegram, "notify_email": t_email,
                        "notify_whatsapp": t_whatsapp, "notify_target": t_target or None,
                    }, timeout=10)
                    if r.status_code == 200:
                        st.success(f"✅ Task **{t_name}** created!")
                        st.rerun()
                    else:
                        detail = r.json().get("detail", r.text)
                        st.error(f"Error: {detail}")
                except Exception as e:
                    st.error(str(e))

if scheduled:
    for task in scheduled:
        icon   = "🟢" if task["is_active"] else "🔴"
        notifs = ", ".join(filter(None, [
            "Telegram"  if task.get("notify_telegram")  else "",
            "Email"     if task.get("notify_email")     else "",
            "WhatsApp"  if task.get("notify_whatsapp")  else "",
        ])) or "No alerts"
        last_run = task.get("last_run", "Never")[:19].replace("T", " ") if task.get("last_run") else "Never"
        st.markdown(
            f"{icon} **#{task['id']} {task['name']}** — "
            f"`{task['cron_expr']}` — 🔔 {notifs} — Last run: {last_run}"
        )
else:
    st.markdown("""
<div class="card" style="text-align:center; padding:24px;">
  <p style="color:#64748b; margin:0; font-size:0.9rem">
    No scheduled tasks yet. Use the form above to automate recurring processing.
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "Automation Toolkit v1.0 · FastAPI + Streamlit + Polars · "
    "[API Docs](http://localhost:8000/docs) · "
    "[GitHub](https://github.com/Arcan17/automation-toolkit)"
)
