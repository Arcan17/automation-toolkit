"""
Streamlit dashboard for Automation Toolkit.
Upload CSV/Excel → Clean → Report → Alert

Supports English and Español via the Language selector in the sidebar.
"""

import time
from pathlib import Path

import plotly.graph_objects as go
import requests
import streamlit as st

from app.translations import LANGUAGES, t, tl

API_URL         = "http://localhost:8000"
SAMPLE_CSV_PATH = Path("data/sample_demo.csv")

st.set_page_config(
    page_title="Automation Toolkit",
    page_icon="⚙️",
    layout="wide",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
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
.result-box {
    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.35);
    border-radius: 10px;
    padding: 18px 22px;
    margin: 14px 0;
}
.result-box h4 { color: #4ade80; margin: 0 0 10px 0; font-size: 1rem; }
.result-box p  { margin: 4px 0; color: #d1fae5; font-size: 0.9rem; }
.error-box {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 10px;
    padding: 16px 20px;
    margin: 12px 0;
}
.error-box p { color: #fca5a5; margin: 0; font-size: 0.9rem; }
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
.kpi-divider { margin: 10px 0 4px 0; }
section[data-testid="stMain"] > div:first-child { max-width: 1200px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:

    # ── Language selector — always first ──────────────────────────────────────
    lang_labels = list(LANGUAGES.keys())          # ["English", "Español"]
    default_idx = 0                                # English first

    # Restore previously selected label (survives reruns)
    if "lang_label" not in st.session_state:
        st.session_state["lang_label"] = lang_labels[default_idx]
        st.session_state["lang"]       = LANGUAGES[lang_labels[default_idx]]

    selected_label = st.selectbox(
        "🌐 Language / Idioma",
        lang_labels,
        index=lang_labels.index(st.session_state["lang_label"]),
        key="_lang_selectbox",
    )
    # Sync session state without triggering extra reruns
    if selected_label != st.session_state.get("lang_label"):
        st.session_state["lang_label"] = selected_label
        st.session_state["lang"]       = LANGUAGES[selected_label]
        st.rerun()

    st.markdown("---")

    # ── App description ───────────────────────────────────────────────────────
    st.markdown("## ⚙️ Automation Toolkit")
    st.markdown(t("app_tagline"))
    st.markdown("---")

    # ── Demo file ─────────────────────────────────────────────────────────────
    st.subheader(t("quick_demo"))
    st.caption(t("demo_caption"))
    if st.button(t("load_sample"), use_container_width=True):
        if SAMPLE_CSV_PATH.exists():
            st.session_state["demo_bytes"] = SAMPLE_CSV_PATH.read_bytes()
            st.session_state["demo_name"]  = "sample_demo.csv"
        else:
            # Inline fallback if file is missing
            fallback = (
                "name,email,department,age,salary,performance_score\n"
                "Alice,alice@co.com,Engineering,28,75000,9.2\n"
                "Bob,bob@co.com,Marketing,34,62000,8.5\n"
                "Alice,alice@co.com,Engineering,28,75000,9.2\n"
                "Charlie,,Operations,41,,7.8\n"
                "Diana,diana@co.com,Engineering,,88000,9.7\n"
            )
            st.session_state["demo_bytes"] = fallback.encode()
            st.session_state["demo_name"]  = "sample_demo.csv"
        st.success(t("sample_loaded"))

    st.markdown("---")

    # ── Upload ────────────────────────────────────────────────────────────────
    st.subheader(t("upload_file"))
    # Visible translated label above the uploader.
    # Note: Streamlit's internal "Drag and drop file here" and "Browse files"
    # texts are rendered by the browser and cannot be overridden via Python.
    st.caption(t("upload_label"))
    uploaded = st.file_uploader(
        "file",
        type=["csv", "xlsx", "xls"],
        label_visibility="collapsed",
        help=t("upload_help"),
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
    st.subheader(t("notifications"))
    st.caption(t("notif_caption"))

    notify_telegram = st.checkbox("Telegram")
    notify_email    = st.checkbox("Email")
    notify_whatsapp = st.checkbox("WhatsApp")
    notify_target   = ""
    if notify_email or notify_whatsapp:
        notify_target = st.text_input(
            t("phone_label") if notify_whatsapp else t("email_label")
        )

    active_channels = [
        ch for ch, on in [
            ("Telegram", notify_telegram),
            ("Email",    notify_email),
            ("WhatsApp", notify_whatsapp),
        ]
        if on
    ]
    if active_channels:
        for ch in active_channels:
            st.caption(t("alert_enabled", channel=ch))
    else:
        st.caption(t("no_alerts"))

    st.markdown("---")

    process_clicked = st.button(
        t("process_btn"),
        type="primary",
        disabled=file_bytes is None,
        use_container_width=True,
    )
    if file_bytes is None:
        st.caption(t("process_hint"))


# ─────────────────────────────────────────────────────────────────────────────
# How it works
# ─────────────────────────────────────────────────────────────────────────────
steps_html = "".join(f"<li>{s}</li>" for s in tl("how_steps"))
st.markdown(f"""
<div class="card">
  <h4>{t("how_title")}</h4>
  <ol style="margin:0; padding-left:20px; color:#cbd5e1; font-size:0.92rem; line-height:1.9">
    {steps_html}
  </ol>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Process action
# ─────────────────────────────────────────────────────────────────────────────
if process_clicked and file_bytes:
    with st.spinner(t("spinner_processing", filename=file_name)):
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
                job    = {}
                for _ in range(30):
                    time.sleep(0.5)
                    poll = requests.get(f"{API_URL}/jobs/{job_id}", timeout=5)
                    if poll.status_code == 200:
                        job = poll.json()
                        if job["status"] in ("done", "failed"):
                            break

                if job.get("status") == "done":
                    rows_raw  = job.get("rows_raw") or 0
                    rows_clean= job.get("rows_clean") or 0
                    dupes     = job.get("duplicates_removed") or 0
                    nulls     = job.get("nulls_filled") or 0
                    pct       = round(rows_clean / rows_raw * 100, 1) if rows_raw else 100
                    notif_line = (
                        t("alert_sent", channels=", ".join(active_channels))
                        if active_channels
                        else t("no_alerts_sent")
                    )
                    st.markdown(f"""
<div class="result-box">
  <h4>{t("result_title", job_id=job_id)}</h4>
  <p>📄 <strong>{file_name}</strong></p>
  <p>{t("original_rows")} <strong>{rows_raw}</strong></p>
  <p>{t("clean_rows")} <strong>{rows_clean}</strong> {t("pct_of_original", pct=pct)}</p>
  <p>{t("dupes_removed")} <strong>{dupes}</strong></p>
  <p>{t("nulls_fixed")} <strong>{nulls}</strong></p>
  <p>{t("report_ready")}</p>
  <p>{notif_line}</p>
</div>
""", unsafe_allow_html=True)

                    dl = requests.get(f"{API_URL}/jobs/{job_id}/download", timeout=10)
                    if dl.status_code == 200:
                        fname_base   = file_name.rsplit(".", 1)[0]
                        out_filename = f"cleaned_{fname_base}_job{job_id}.xlsx"
                        # Reports are always .xlsx — use excel key
                        dl_key = "download_now_excel"
                        st.download_button(
                            t(dl_key, filename=file_name),
                            data=dl.content,
                            file_name=out_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            type="primary",
                        )

                elif job.get("status") == "failed":
                    st.markdown(
                        f'<div class="error-box"><p>'
                        f'{t("err_job_failed", job_id=job_id, error=job.get("error", ""))}'
                        f'</p></div>',
                        unsafe_allow_html=True,
                    )
            else:
                body   = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
                detail = body.get("detail", resp.text)
                st.markdown(
                    f'<div class="error-box"><p>'
                    f'{t("err_api", code=resp.status_code, detail=detail)}'
                    f'</p></div>',
                    unsafe_allow_html=True,
                )

        except requests.exceptions.ConnectionError:
            st.markdown(
                f'<div class="error-box"><p>{t("err_connect")}</p></div>',
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.markdown(
                f'<div class="error-box"><p>{t("err_unexpected", error=e)}</p></div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────────────────────────────────────
# Job history
# ─────────────────────────────────────────────────────────────────────────────
st.header(t("job_history"))

api_ok = True
try:
    resp = requests.get(f"{API_URL}/jobs/", timeout=4)
    jobs = resp.json() if resp.status_code == 200 else []
except Exception:
    jobs   = []
    api_ok = False

if not api_ok:
    st.markdown(
        f'<div class="error-box"><p>{t("err_api_down")}</p></div>',
        unsafe_allow_html=True,
    )

elif jobs:
    import polars as pl

    done_jobs   = [j for j in jobs if j["status"] == "done"]
    total       = len(jobs)
    failed      = sum(1 for j in jobs if j["status"] == "failed")
    total_rows  = sum(j.get("rows_raw") or 0 for j in done_jobs)
    total_dupes = sum(j.get("duplicates_removed") or 0 for j in done_jobs)
    total_nulls = sum(j.get("nulls_filled") or 0 for j in done_jobs)
    reports     = sum(1 for j in done_jobs if j.get("report_path"))

    # ── KPI row 1 — job status ─────────────────────────────────────────────
    c1, c2, c3, _p = st.columns([1, 1, 1, 1])
    c1.metric(t("kpi_total"),     total)
    c2.metric(t("kpi_completed"), len(done_jobs))
    c3.metric(t("kpi_failed"),    failed,
              delta=f"+{failed}" if failed else None, delta_color="inverse")

    st.markdown('<div class="kpi-divider"></div>', unsafe_allow_html=True)

    # ── KPI row 2 — data impact ────────────────────────────────────────────
    c4, c5, c6, c7 = st.columns(4)
    c4.metric(t("kpi_rows"),    f"{total_rows:,}")
    c5.metric(t("kpi_dupes"),   f"{total_dupes:,}")
    c6.metric(t("kpi_nulls"),   f"{total_nulls:,}")
    c7.metric(t("kpi_reports"), reports)

    # ── Jobs table ─────────────────────────────────────────────────────────
    status_map = {
        "done":       t("status_done"),
        "failed":     t("status_failed"),
        "processing": t("status_processing"),
    }
    rows = []
    for j in jobs:
        raw   = j.get("rows_raw") or 0
        clean = j.get("rows_clean") or 0
        pct   = f"{round(clean / raw * 100)}%" if raw else "—"
        rows.append({
            "#":                   j["id"],
            t("col_file"):         j["original_name"],
            t("col_status"):       status_map.get(j["status"], j["status"]),
            t("col_original_rows"):raw,
            t("col_clean_rows"):   clean,
            t("col_quality"):      pct,
            t("col_dupes"):        j.get("duplicates_removed") or 0,
            t("col_nulls"):        j.get("nulls_filled") or 0,
            t("col_date"):         j.get("created_at", "")[:19].replace("T", " "),
        })
    st.dataframe(pl.DataFrame(rows).to_pandas(), use_container_width=True, hide_index=True)

    # ── Download buttons ───────────────────────────────────────────────────
    reportable = [j for j in done_jobs if j.get("report_path")]
    if reportable:
        st.subheader(t("download_section"))
        cols = st.columns(min(len(reportable), 4))
        for i, j in enumerate(reportable):
            with cols[i % 4]:
                dl = requests.get(f"{API_URL}/jobs/{j['id']}/download", timeout=10)
                if dl.status_code == 200:
                    fname_base   = j["original_name"].rsplit(".", 1)[0]
                    out_filename = f"cleaned_{fname_base}_job{j['id']}.xlsx"
                    # Report is always .xlsx regardless of original file type
                    dl_key = "download_btn_excel"
                    st.download_button(
                        t(dl_key, filename=j["original_name"]),
                        data=dl.content,
                        file_name=out_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"dl_{j['id']}",
                        use_container_width=True,
                    )

    # ── Charts ─────────────────────────────────────────────────────────────
    chart_jobs = [j for j in done_jobs if j.get("rows_raw")]
    if chart_jobs:
        _LAYOUT = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=0, r=0, t=36, b=0),
            font=dict(color="#cbd5e1"),
        )
        _AXIS = dict(color="#94a3b8", gridcolor="rgba(255,255,255,0.07)")

        col_left, col_right = st.columns(2)

        # Chart 1 — rows before vs after
        with col_left:
            st.subheader(t("chart_impact"))
            labels = [f"#{j['id']} {j['original_name'][:18]}" for j in chart_jobs]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name=t("chart_original"), x=labels,
                y=[j["rows_raw"]   for j in chart_jobs],
                marker_color="#ef4444",
            ))
            fig.add_trace(go.Bar(
                name=t("chart_clean"),   x=labels,
                y=[j["rows_clean"] for j in chart_jobs],
                marker_color="#22c55e",
            ))
            fig.update_layout(
                barmode="group",
                xaxis=dict(title="", **_AXIS),
                yaxis=dict(title=t("axis_rows"), **_AXIS),
                **_LAYOUT,
            )
            st.plotly_chart(fig, use_container_width=True)

        # Chart 2 — issues breakdown
        with col_right:
            st.subheader(t("chart_issues"))
            total_d = sum(j.get("duplicates_removed") or 0 for j in chart_jobs)
            total_n = sum(j.get("nulls_filled") or 0 for j in chart_jobs)

            if len(chart_jobs) == 1 and (total_d + total_n) > 0:
                # Donut — cleaner for a single job
                j0 = chart_jobs[0]
                d  = j0.get("duplicates_removed") or 0
                n  = j0.get("nulls_filled") or 0
                fig2 = go.Figure(go.Pie(
                    labels=[t("chart_dupes_legend"), t("chart_nulls_legend")],
                    values=[d, n],
                    hole=0.55,
                    marker_colors=["#f59e0b", "#6366f1"],
                    textinfo="label+value",
                    hovertemplate="%{label}: %{value}<extra></extra>",
                ))
                fig2.add_annotation(
                    text=(
                        f"<b>{d + n}</b><br>"
                        f"<span style='font-size:11px'>{t('chart_issues_unit')}</span>"
                    ),
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=18, color="#cbd5e1"),
                )
                fig2.update_layout(**_LAYOUT)
                st.plotly_chart(fig2, use_container_width=True)

            elif len(chart_jobs) > 1:
                labels2 = [f"#{j['id']} {j['original_name'][:18]}" for j in chart_jobs]
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    name=t("chart_dupes_legend"), x=labels2,
                    y=[j.get("duplicates_removed") or 0 for j in chart_jobs],
                    marker_color="#f59e0b",
                ))
                fig2.add_trace(go.Bar(
                    name=t("chart_nulls_legend"), x=labels2,
                    y=[j.get("nulls_filled") or 0 for j in chart_jobs],
                    marker_color="#6366f1",
                ))
                fig2.update_layout(
                    barmode="stack",
                    xaxis=dict(title="", **_AXIS),
                    yaxis=dict(title=t("axis_issues"), **_AXIS),
                    **_LAYOUT,
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.markdown(
                    f'<div class="card" style="text-align:center;padding:48px 24px;">'
                    f'<p style="color:#64748b;margin:0">{t("chart_already_clean")}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

else:
    st.markdown(f"""
<div class="card" style="text-align:center; padding:32px;">
  <p style="color:#64748b; font-size:1.1rem; margin:0">
    {t("no_jobs_title")}<br>
    <span style="font-size:0.9rem">{t("no_jobs_hint")}</span>
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Scheduled tasks
# ─────────────────────────────────────────────────────────────────────────────
st.header(t("scheduled_tasks"))

try:
    resp      = requests.get(f"{API_URL}/tasks/", timeout=4)
    scheduled = resp.json() if resp.status_code == 200 else []
except Exception:
    scheduled = []

with st.expander(t("create_task_exp")):
    st.caption(t("task_exp_caption"))
    with st.form("new_task"):
        col1, col2 = st.columns(2)
        with col1:
            t_name = st.text_input(t("task_name_lbl"), placeholder=t("task_name_ph"))
            t_file = st.text_input(t("task_file_lbl"), placeholder=t("task_file_ph"))
        with col2:
            t_cron = st.text_input(t("task_cron_lbl"), placeholder=t("task_cron_ph"))
            st.caption(t("task_cron_help"))
        tc1, tc2, tc3 = st.columns(3)
        t_telegram  = tc1.checkbox("Telegram")
        t_email     = tc2.checkbox("Email")
        t_whatsapp  = tc3.checkbox("WhatsApp")
        t_target    = st.text_input(t("task_target_lbl"))

        if st.form_submit_button(t("task_submit"), type="primary"):
            if not (t_name and t_file and t_cron):
                st.warning(t("task_required"))
            else:
                try:
                    r = requests.post(f"{API_URL}/tasks/", json={
                        "name": t_name, "filename": t_file, "cron_expr": t_cron,
                        "notify_telegram": t_telegram, "notify_email": t_email,
                        "notify_whatsapp": t_whatsapp, "notify_target": t_target or None,
                    }, timeout=10)
                    if r.status_code == 200:
                        st.success(t("task_created", name=t_name))
                        st.rerun()
                    else:
                        detail = r.json().get("detail", r.text)
                        st.error(t("task_api_error", detail=detail))
                except Exception as e:
                    st.error(str(e))

if scheduled:
    for task in scheduled:
        icon    = "🟢" if task["is_active"] else "🔴"
        notifs  = ", ".join(filter(None, [
            "Telegram"  if task.get("notify_telegram")  else "",
            "Email"     if task.get("notify_email")     else "",
            "WhatsApp"  if task.get("notify_whatsapp")  else "",
        ])) or t("task_no_alerts")
        raw_run = task.get("last_run")
        last_run = raw_run[:19].replace("T", " ") if raw_run else t("task_never")
        st.markdown(
            f"{icon} **#{task['id']} {task['name']}** — "
            f"`{task['cron_expr']}` — 🔔 {notifs} — "
            f"{t('task_last_run')} {last_run}"
        )
else:
    st.markdown(f"""
<div class="card" style="padding:24px 28px;">
  <p style="color:#94a3b8; font-weight:600; margin:0 0 6px 0">{t("no_tasks_title")}</p>
  <p style="color:#64748b; margin:0; font-size:0.88rem; line-height:1.6">
    {t("no_tasks_hint")}
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(t("footer"))
