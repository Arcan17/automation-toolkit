"""
Streamlit dashboard for Automation Toolkit.
"""

import time
import requests
import streamlit as st
import plotly.express as px
import polars as pl

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Automation Toolkit",
    page_icon="⚙️",
    layout="wide",
)

st.markdown("""
<style>
.result-box {
    background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.4);
    border-radius: 8px; padding: 16px 20px; margin: 12px 0;
}
.result-box h4 { color: #4ade80; margin: 0 0 8px 0; }
.result-box p  { margin: 3px 0; color: #d1fae5; font-size: 0.92rem; }
.how-box {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 8px; padding: 16px 20px; margin-bottom: 24px;
}
.how-box h4 { color: #94a3b8; margin: 0 0 10px 0; font-size: 1rem; letter-spacing: 0.02em; }
.how-box ol { margin: 0; padding-left: 20px; color: #cbd5e1; font-size: 0.9rem; }
.how-box li { margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Automation Toolkit")
    st.markdown("""
Upload **CSV or Excel** files to automatically:
- 🧹 Remove duplicate rows
- 🩹 Fill missing values
- 📊 Generate a clean Excel report
- 🔔 Send alerts via Telegram, Email or WhatsApp
""")
    st.markdown("---")

    # Demo CSV
    st.subheader("🎯 Try a demo file")
    if st.button("Load sample CSV", use_container_width=True):
        sample = (
            "name,email,age,score\n"
            "Alice,alice@example.com,28,9.5\n"
            "Bob,bob@example.com,34,8.0\n"
            "Alice,alice@example.com,28,9.5\n"
            "Charlie,,41,\n"
            "Diana,diana@example.com,,7.2\n"
            "Eve,eve@example.com,25,\n"
        )
        st.session_state["demo_bytes"] = sample.encode()
        st.session_state["demo_name"]  = "sample_demo.csv"
        st.success("Sample CSV loaded ✓")

    st.markdown("---")

    # Upload
    st.subheader("📤 Upload your file")
    uploaded = st.file_uploader(
        "CSV or Excel", type=["csv", "xlsx", "xls"], label_visibility="collapsed"
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
        st.caption(f"📄 Ready: **{file_name}**")

    st.markdown("---")

    # Notifications
    st.subheader("🔔 Notifications")
    notify_telegram = st.checkbox("Telegram")
    notify_email    = st.checkbox("Email")
    notify_whatsapp = st.checkbox("WhatsApp")
    notify_target   = ""
    if notify_email or notify_whatsapp:
        notify_target = st.text_input(
            "Email or phone (+56912345678)" if notify_whatsapp else "Email address"
        )

    # Notification status preview
    channels = []
    if notify_telegram:  channels.append("✅ Telegram: enabled")
    if notify_email:     channels.append("✅ Email: enabled")
    if notify_whatsapp:  channels.append("✅ WhatsApp: enabled")
    if not channels:
        st.caption("ℹ️ No alerts selected — file will be processed silently.")
    else:
        for ch in channels:
            st.caption(ch)

    st.markdown("---")
    process_clicked = st.button(
        "🚀 Process file",
        type="primary",
        disabled=file_bytes is None,
        use_container_width=True,
    )
    if file_bytes is None:
        st.caption("⬆️ Upload a file or load the sample CSV to enable processing.")

# ─────────────────────────────────────────────────────────────────────────────
# How it works — top of main area
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="how-box">
  <h4>ℹ️ How it works</h4>
  <ol>
    <li>Upload a CSV or Excel file using the sidebar (or load the demo)</li>
    <li>The system removes duplicate rows automatically</li>
    <li>Missing values are filled: <code>0</code> for numbers, <code>N/A</code> for text</li>
    <li>A clean Excel report is generated and ready to download</li>
    <li>Optional alerts are sent through Telegram, Email or WhatsApp</li>
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
                # Poll until done (max 15 s)
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
                    notif_line = (
                        "🔔 Alert sent via " + ", ".join(filter(None, [
                            "Telegram"  if notify_telegram  else "",
                            "Email"     if notify_email     else "",
                            "WhatsApp"  if notify_whatsapp  else "",
                        ]))
                        if any([notify_telegram, notify_email, notify_whatsapp])
                        else "🔕 No alert configured"
                    )
                    st.markdown(f"""
<div class="result-box">
  <h4>✅ File processed successfully — Job #{job_id}</h4>
  <p>📄 <strong>{file_name}</strong></p>
  <p>📥 Original rows: <strong>{rows_raw}</strong></p>
  <p>✨ Clean rows: <strong>{rows_clean}</strong></p>
  <p>🗑️ Duplicates removed: <strong>{dupes}</strong></p>
  <p>🩹 Missing values fixed: <strong>{nulls}</strong></p>
  <p>📊 Report generated: <strong>Yes</strong></p>
  <p>{notif_line}</p>
</div>
""", unsafe_allow_html=True)

                    # Inline download
                    dl = requests.get(f"{API_URL}/jobs/{job_id}/download", timeout=10)
                    if dl.status_code == 200:
                        st.download_button(
                            f"⬇️ Download cleaned report — {file_name.replace('.csv','').replace('.xlsx','')}",
                            data=dl.content,
                            file_name=f"report_job_{job_id}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                        )
                else:
                    st.error(f"❌ Job #{job_id} failed. Check API logs.")
            else:
                st.error(f"API error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Cannot connect to API: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# Job history
# ─────────────────────────────────────────────────────────────────────────────
st.header("📋 Job History")

try:
    resp = requests.get(f"{API_URL}/jobs/", timeout=5)
    jobs = resp.json() if resp.status_code == 200 else []
except Exception:
    jobs = []
    st.warning("⚠️ API not running. Start with: `uvicorn app.main:app --reload`")

if jobs:
    total      = len(jobs)
    done_jobs  = [j for j in jobs if j["status"] == "done"]
    failed     = sum(1 for j in jobs if j["status"] == "failed")
    total_rows = sum(j.get("rows_raw") or 0 for j in done_jobs)
    total_dupes = sum(j.get("duplicates_removed") or 0 for j in done_jobs)
    total_nulls = sum(j.get("nulls_filled") or 0 for j in done_jobs)
    reports     = sum(1 for j in done_jobs if j.get("report_path"))

    # Metrics row 1
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Jobs",  total)
    c2.metric("Completed",   len(done_jobs))
    c3.metric("Failed",      failed,
              delta=f"+{failed}" if failed else None, delta_color="inverse")

    # Metrics row 2
    c4, c5, c6, c7 = st.columns(4)
    c4.metric("Rows Processed",     total_rows)
    c5.metric("Duplicates Removed", total_dupes)
    c6.metric("Missing Values Fixed", total_nulls)
    c7.metric("Reports Generated",  reports)

    # Table
    rows = []
    for j in jobs:
        status_icon = {
            "done":       "✅ Done",
            "failed":     "❌ Failed",
            "processing": "⏳ Processing",
        }.get(j["status"], j["status"])
        rows.append({
            "#":                    j["id"],
            "File":                 j["original_name"],
            "Status":               status_icon,
            "Original Rows":        j.get("rows_raw") or 0,
            "Clean Rows":           j.get("rows_clean") or 0,
            "Duplicates Removed":   j.get("duplicates_removed") or 0,
            "Missing Values Fixed": j.get("nulls_filled") or 0,
            "Date":                 j.get("created_at", "")[:19].replace("T", " "),
        })
    st.dataframe(pl.DataFrame(rows).to_pandas(), use_container_width=True, hide_index=True)

    # Download buttons (one per done job)
    reportable = [j for j in done_jobs if j.get("report_path")]
    if reportable:
        st.subheader("⬇️ Download Reports")
        cols = st.columns(min(len(reportable), 4))
        for i, j in enumerate(reportable):
            with cols[i % 4]:
                dl = requests.get(f"{API_URL}/jobs/{j['id']}/download", timeout=10)
                if dl.status_code == 200:
                    st.download_button(
                        f"⬇️ Download cleaned report — {j['original_name'][:22]}",
                        data=dl.content,
                        file_name=f"report_job_{j['id']}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{j['id']}",
                        use_container_width=True,
                    )

    # Chart
    if done_jobs:
        st.subheader("📊 Original vs Clean Rows per Job")
        chart = [j for j in done_jobs if j.get("rows_raw")]
        if chart:
            fig = px.bar(
                {
                    "Job":           [f"#{j['id']} {j['original_name'][:20]}" for j in chart],
                    "Original Rows": [j["rows_raw"]  for j in chart],
                    "Clean Rows":    [j["rows_clean"] for j in chart],
                },
                x="Job", y=["Original Rows", "Clean Rows"],
                barmode="group",
                color_discrete_map={"Original Rows": "#ef4444", "Clean Rows": "#22c55e"},
            )
            fig.update_layout(legend_title_text="", xaxis_title="", yaxis_title="Rows")
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No jobs yet — upload a CSV/Excel file or click **Load sample CSV** in the sidebar.")

# ─────────────────────────────────────────────────────────────────────────────
# Scheduled tasks
# ─────────────────────────────────────────────────────────────────────────────
st.header("🗓️ Scheduled Tasks")

try:
    resp      = requests.get(f"{API_URL}/tasks/", timeout=5)
    scheduled = resp.json() if resp.status_code == 200 else []
except Exception:
    scheduled = []

with st.expander("➕ Create new scheduled task"):
    st.caption("Automatically process a file on a recurring schedule and send notifications.")
    with st.form("new_task"):
        col1, col2 = st.columns(2)
        with col1:
            t_name = st.text_input("Task name", placeholder="Weekly sales report")
            t_file = st.text_input("Filename (must be already uploaded)", placeholder="clients.csv")
        with col2:
            t_cron = st.text_input("Cron expression", placeholder="0 8 * * 1")
            st.caption("`0 9 * * 1-5` → weekdays 9 am · `0 8 1 * *` → 1st of month · `0 8 * * 1` → every Monday")
        tc1, tc2, tc3 = st.columns(3)
        t_telegram  = tc1.checkbox("Telegram")
        t_email     = tc2.checkbox("Email")
        t_whatsapp  = tc3.checkbox("WhatsApp")
        t_target    = st.text_input("Email or phone (if Email / WhatsApp selected)")
        if st.form_submit_button("✅ Create task", type="primary"):
            if not (t_name and t_file and t_cron):
                st.warning("Fill in name, filename and cron expression.")
            else:
                try:
                    r = requests.post(f"{API_URL}/tasks/", json={
                        "name": t_name, "filename": t_file, "cron_expr": t_cron,
                        "notify_telegram": t_telegram, "notify_email": t_email,
                        "notify_whatsapp": t_whatsapp, "notify_target": t_target or None,
                    }, timeout=10)
                    if r.status_code == 200:
                        st.success(f"✅ Task **{t_name}** created!")
                    else:
                        st.error(r.text)
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
        st.markdown(
            f"{icon} **#{task['id']} {task['name']}** — "
            f"`{task['cron_expr']}` — 🔔 {notifs}"
        )
else:
    st.info("No scheduled tasks yet.")

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Automation Toolkit · FastAPI + Streamlit · [API Docs](http://localhost:8000/docs)")
