---
name: dashboard-polish
description: Use this skill when working on dashboards, Streamlit apps, admin panels, data apps, SaaS tools, portfolio dashboards, metrics pages, charts, tables, upload flows, job history views, or report download interfaces. Focus on making the interface look professional, clear, and portfolio-ready without breaking backend logic.
---

# Dashboard Polish Skill

## Goal
Make this Streamlit dashboard look like a real SaaS product — clean, clear, and presentable for GitHub, LinkedIn, and freelance clients.

## Files
- `dashboard.py` — Streamlit UI (the only file to modify for visual changes)
- `app/` — FastAPI backend (do NOT modify unless explicitly asked)

## Stack
- Streamlit + Plotly for UI
- FastAPI backend at `http://localhost:8000`
- SQLite via SQLAlchemy

## Polish checklist

1. **Value prop in 5 seconds** — sidebar must explain what the tool does before the user touches anything
2. **Visual hierarchy** — sections clearly separated, headers meaningful
3. **Metrics** — show business impact: rows processed, duplicates removed, values fixed, reports generated
4. **Labels & microcopy** — no raw technical names; use user-friendly labels
5. **States** — empty state, loading state, success state, error state all handled
6. **Disabled states** — explain *why* a button is disabled, not just grey it out
7. **Download buttons** — label must say what the user gets: "Download cleaned report — filename"
8. **Charts** — axis labels, legend, title must tell a story ("Original vs Clean Rows per Job")
9. **Table columns** — "Original Rows", "Clean Rows", "Duplicates Removed", "Missing Values Fixed"
10. **Theme consistency** — custom CSS must use rgba() on dark backgrounds, not hardcoded white
11. **Demo mode** — "Load sample CSV" button so anyone can test without a real file
12. **How it works** — numbered steps showing the full automation flow
13. **Notification status** — show which channels are active before processing
14. **Result summary** — after processing show: filename, original rows, clean rows, duplicates, nulls, report status, alert status

## CSS rules
- Background: `rgba(255,255,255,0.04)` for dark cards
- Border: `rgba(255,255,255,0.12)` subtle separator
- Success color: `rgba(34,197,94,0.1)` background, `#4ade80` text
- Text: `#cbd5e1` body, `#94a3b8` labels/captions
- Never use `#ffffff` or `#f8fafc` as background — it breaks dark mode

## Before touching code
1. Read `dashboard.py` fully
2. State which sections need changes and why
3. List what will NOT be changed

## After changes
1. Restart Streamlit: `pkill -f "streamlit run"; cd /Users/bastian/Documents/automation-toolkit && source .venv/bin/activate && streamlit run dashboard.py --server.port 8501 --server.headless true &`
2. Verify it loads: `curl -s http://localhost:8501/_stcore/health`
3. Commit: `git add dashboard.py && git commit -m "style: <description>"`
