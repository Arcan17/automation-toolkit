"""
Translations for the Automation Toolkit dashboard.

Usage (in dashboard.py):
    from app.translations import t, tl, LANGUAGES

    lang = st.session_state.get("lang", "en")
    t("process_btn")              # → "🚀 Process file"  or  "🚀 Procesar archivo"
    t("task_created", name="X")   # → "✅ Task **X** created!"  (with .format())
    tl("how_steps")               # → list of step strings
"""

from __future__ import annotations
import streamlit as st

# ── Available languages ────────────────────────────────────────────────────────
LANGUAGES: dict[str, str] = {
    "English": "en",
    "Español": "es",
}

# ── Full translation table ─────────────────────────────────────────────────────
_T: dict[str, dict] = {
    # ──────────────────────────────────────────────────────── English ──────────
    "en": {
        # Sidebar — header
        "app_tagline": (
            "Upload **CSV or Excel** files to automatically clean data, "
            "remove duplicates, fix missing values, generate downloadable "
            "reports, and send alerts."
        ),
        # Sidebar — demo
        "quick_demo":   "🎯 Quick demo",
        "demo_caption": "Realistic HR data with duplicates and missing values",
        "demo_caption_template": "{rows} rows · {dupes} duplicates · {nulls} missing values · realistic HR data",
        "load_sample":  "⚡ Load sample CSV",
        "sample_loaded": "Sample loaded ✓",
        # Sidebar — upload
        "upload_file":  "📤 Upload your file",
        "upload_help":  "CSV (.csv) or Excel (.xlsx / .xls) — max 10 MB",
        # Sidebar — notifications
        "notifications":   "🔔 Notifications",
        "notif_caption":   "Configure in `.env` to enable real alerts.",
        "no_alerts":       "ℹ️ No alerts — file will be processed silently.",
        "alert_enabled":   "✅ {channel}: enabled",
        "email_label":     "Email address",
        "phone_label":     "Email or phone (+56912345678)",
        # Sidebar — upload label (shown above the file uploader widget)
        # Note: Streamlit's internal "Drag and drop file here" and "Browse files"
        # texts are rendered by the browser/Streamlit and cannot be translated.
        "upload_label": "Upload a CSV or Excel file",
        # Sidebar — process
        "process_btn":  "🚀 Process file",
        "process_hint": "⬆️ Load a file or click **Load sample CSV** above.",
        # Spinner
        "spinner_processing": "Processing **{filename}**…",
        # How it works
        "how_title": "ℹ️ How it works",
        # (list — use tl())
        "how_steps": [
            "Upload a CSV or Excel file <em>(or use the sample)</em>",
            "Duplicate rows are detected and removed automatically",
            "Missing values are filled — <code>0</code> for numbers, <code>N/A</code> for text",
            "A clean Excel report is generated with a <strong>Summary</strong> sheet and a <strong>Clean Data</strong> sheet",
            "Optional alerts sent via Telegram, Email or WhatsApp when complete",
        ],
        # Result box
        "result_title":     "✅ File processed successfully — Job #{job_id}",
        "original_rows":    "📥 Original rows:",
        "clean_rows":       "✨ Clean rows:",
        "pct_of_original":  "({pct}% of original)",
        "dupes_removed":    "🗑️ Duplicates removed:",
        "nulls_fixed":      "🩹 Missing values fixed:",
        "report_ready":     "📊 Report: <strong>Ready to download</strong> (Summary + Clean Data sheets)",
        "alert_sent":       "🔔 Alert sent via {channels}",
        "no_alerts_sent":   "🔕 No alerts configured",
        # Download — label adapts to file type
        "download_section":     "⬇️ Download Reports",
        "download_btn_excel":   "⬇️ Download Excel Report — {filename}",
        "download_btn_csv":     "⬇️ Download cleaned file — {filename}",
        "download_now_excel":   "⬇️ Download Excel report — {filename}",
        "download_now_csv":     "⬇️ Download cleaned file — {filename}",
        # Job history — header & KPIs
        "job_history":        "📋 Job History",
        "kpi_total":          "Total Jobs",
        "kpi_completed":      "Completed",
        "kpi_failed":         "Failed",
        "kpi_rows":           "Rows Processed",
        "kpi_dupes":          "Duplicates Removed",
        "kpi_nulls":          "Missing Values Fixed",
        "kpi_reports":        "Reports Generated",
        # Table columns
        "col_file":           "File",
        "col_status":         "Status",
        "col_original_rows":  "Original Rows",
        "col_clean_rows":     "Clean Rows",
        "col_quality":        "Quality",
        "col_dupes":          "Duplicates Removed",
        "col_nulls":          "Missing Values Fixed",
        "col_date":           "Date",
        # Status values
        "status_done":        "✅ Done",
        "status_failed":      "❌ Failed",
        "status_processing":  "⏳ Processing",
        # Charts
        "chart_impact":       "📊 Data Cleaning Impact per Job",
        "chart_issues":       "🔧 Issues Resolved per Job",
        "chart_original":     "Original Rows",
        "chart_clean":        "Clean Rows",
        "chart_dupes_legend": "Duplicates Removed",
        "chart_nulls_legend": "Missing Values Fixed",
        "chart_issues_unit":  "issues",
        "chart_already_clean": "No issues found — data was already clean ✅",
        "axis_rows":          "Rows",
        "axis_issues":        "Issues",
        # Scheduled tasks
        "scheduled_tasks":    "🗓️ Scheduled Tasks",
        "create_task_exp":    "➕ Create a new scheduled task",
        "task_exp_caption":   "Automatically process a file on a recurring schedule and optionally send alerts.",
        "task_name_lbl":      "Task name",
        "task_name_ph":       "Weekly sales report",
        "task_file_lbl":      "Filename (must already be uploaded)",
        "task_file_ph":       "clients.csv",
        "task_cron_lbl":      "Cron expression",
        "task_cron_ph":       "0 8 * * 1",
        "task_cron_help":     (
            "Examples: `0 8 * * 1` Mon 8am · "
            "`0 9 * * 1-5` weekdays 9am · "
            "`0 8 1 * *` 1st of month"
        ),
        "task_target_lbl":    "Email or phone (if Email/WhatsApp selected)",
        "task_submit":        "✅ Create task",
        "task_required":      "Name, filename and cron expression are required.",
        "task_created":       "✅ Task **{name}** created!",
        "task_api_error":     "Error: {detail}",
        "task_last_run":      "Last run:",
        "task_never":         "Never",
        "task_no_alerts":     "No alerts",
        # Empty states
        "no_jobs_title":  "No jobs yet.",
        "no_jobs_hint":   "Use the sidebar to upload a file or click <strong>⚡ Load sample CSV</strong> for a quick demo.",
        "no_tasks_title": "No scheduled tasks yet",
        "no_tasks_hint":  (
            "Create a scheduled task to automatically process a file on a recurring schedule.<br>"
            "Example: run <strong>sales_report.csv</strong> every Monday at 8 am "
            "and get a Telegram alert when done."
        ),
        # Errors
        "err_api":        "❌ API error {code}: {detail}",
        "err_connect":    "❌ Cannot connect to API. Run: <code>uvicorn app.main:app --reload</code>",
        "err_api_down":   "⚠️ API not reachable. Start the backend: <code>uvicorn app.main:app --reload</code>",
        "err_job_failed": "❌ <strong>Job #{job_id} failed.</strong> {error}",
        "err_unexpected": "❌ Unexpected error: {error}",
        # Footer
        "footer": (
            "Automation Toolkit v1.0 · FastAPI + Streamlit + Polars · "
            "[API Docs](http://localhost:8000/docs) · "
            "[GitHub](https://github.com/Arcan17/automation-toolkit)"
        ),
    },

    # ──────────────────────────────────────────────────────── Español ──────────
    "es": {
        # Sidebar — header
        "app_tagline": (
            "Sube archivos **CSV o Excel** para limpiar datos automáticamente, "
            "eliminar duplicados, corregir valores faltantes, generar reportes "
            "descargables y enviar alertas."
        ),
        # Sidebar — demo
        "quick_demo":   "🎯 Demo rápido",
        "demo_caption": "Datos HR reales con duplicados y valores faltantes",
        "demo_caption_template": "{rows} filas · {dupes} duplicados · {nulls} valores faltantes · datos HR reales",
        "load_sample":  "⚡ Cargar CSV de ejemplo",
        "sample_loaded": "Ejemplo cargado ✓",
        # Sidebar — upload
        "upload_file":   "📤 Subir archivo",
        "upload_label":  "Sube un archivo CSV o Excel",
        "upload_help":   "CSV (.csv) o Excel (.xlsx / .xls) — máx. 10 MB",
        # Sidebar — notifications
        "notifications":   "🔔 Notificaciones",
        "notif_caption":   "Configura en `.env` para activar alertas reales.",
        "no_alerts":       "ℹ️ Sin alertas — el archivo se procesará silenciosamente.",
        "alert_enabled":   "✅ {channel}: activado",
        "email_label":     "Correo electrónico",
        "phone_label":     "Correo o teléfono (+56912345678)",
        # Sidebar — process
        "process_btn":  "🚀 Procesar archivo",
        "process_hint": "⬆️ Carga un archivo o haz clic en **Cargar CSV de ejemplo**.",
        # Spinner
        "spinner_processing": "Procesando **{filename}**…",
        # How it works
        "how_title": "ℹ️ Cómo funciona",
        "how_steps": [
            "Sube un archivo CSV o Excel <em>(o usa el ejemplo)</em>",
            "Las filas duplicadas se detectan y eliminan automáticamente",
            "Los valores faltantes se rellenan — <code>0</code> para números, <code>N/A</code> para texto",
            "Se genera un reporte Excel con una hoja <strong>Summary</strong> y una hoja <strong>Clean Data</strong>",
            "Se envían alertas opcionales por Telegram, Email o WhatsApp al terminar",
        ],
        # Result box
        "result_title":     "✅ Archivo procesado exitosamente — Proceso #{job_id}",
        "original_rows":    "📥 Filas originales:",
        "clean_rows":       "✨ Filas limpias:",
        "pct_of_original":  "({pct}% del original)",
        "dupes_removed":    "🗑️ Duplicados eliminados:",
        "nulls_fixed":      "🩹 Valores faltantes corregidos:",
        "report_ready":     "📊 Reporte: <strong>Listo para descargar</strong> (hojas Summary + Clean Data)",
        "alert_sent":       "🔔 Alerta enviada por {channels}",
        "no_alerts_sent":   "🔕 Sin alertas configuradas",
        # Download — label adapts to file type
        "download_section":     "⬇️ Descargar Reportes",
        "download_btn_excel":   "⬇️ Descargar reporte Excel — {filename}",
        "download_btn_csv":     "⬇️ Descargar archivo limpio — {filename}",
        "download_now_excel":   "⬇️ Descargar reporte Excel — {filename}",
        "download_now_csv":     "⬇️ Descargar archivo limpio — {filename}",
        # Job history — header & KPIs
        "job_history":        "📋 Historial de procesos",
        "kpi_total":          "Procesos totales",
        "kpi_completed":      "Completados",
        "kpi_failed":         "Fallidos",
        "kpi_rows":           "Filas procesadas",
        "kpi_dupes":          "Duplicados eliminados",
        "kpi_nulls":          "Valores faltantes corregidos",
        "kpi_reports":        "Reportes generados",
        # Table columns
        "col_file":           "Archivo",
        "col_status":         "Estado",
        "col_original_rows":  "Filas originales",
        "col_clean_rows":     "Filas limpias",
        "col_quality":        "Calidad",
        "col_dupes":          "Duplicados eliminados",
        "col_nulls":          "Valores faltantes corregidos",
        "col_date":           "Fecha",
        # Status values
        "status_done":        "✅ Completado",
        "status_failed":      "❌ Fallido",
        "status_processing":  "⏳ Procesando",
        # Charts
        "chart_impact":       "📊 Impacto de limpieza por proceso",
        "chart_issues":       "🔧 Problemas resueltos por proceso",
        "chart_original":     "Filas originales",
        "chart_clean":        "Filas limpias",
        "chart_dupes_legend": "Duplicados eliminados",
        "chart_nulls_legend": "Valores faltantes corregidos",
        "chart_issues_unit":  "problemas",
        "chart_already_clean": "Sin problemas — los datos ya estaban limpios ✅",
        "axis_rows":          "Filas",
        "axis_issues":        "Problemas",
        # Scheduled tasks
        "scheduled_tasks":    "🗓️ Tareas Programadas",
        "create_task_exp":    "➕ Crear nueva tarea programada",
        "task_exp_caption":   "Procesa un archivo automáticamente en un horario y envía notificaciones opcionales.",
        "task_name_lbl":      "Nombre de la tarea",
        "task_name_ph":       "Reporte semanal de ventas",
        "task_file_lbl":      "Nombre de archivo (ya debe estar subido)",
        "task_file_ph":       "clientes.csv",
        "task_cron_lbl":      "Expresión Cron",
        "task_cron_ph":       "0 8 * * 1",
        "task_cron_help":     (
            "Ejemplos: `0 8 * * 1` lunes 8am · "
            "`0 9 * * 1-5` días hábiles 9am · "
            "`0 8 1 * *` primero de mes"
        ),
        "task_target_lbl":    "Email o teléfono (si se selecciona Email/WhatsApp)",
        "task_submit":        "✅ Crear tarea",
        "task_required":      "El nombre, archivo y expresión cron son obligatorios.",
        "task_created":       "✅ Tarea **{name}** creada!",
        "task_api_error":     "Error: {detail}",
        "task_last_run":      "Última ejecución:",
        "task_never":         "Nunca",
        "task_no_alerts":     "Sin alertas",
        # Empty states
        "no_jobs_title":  "Aún no hay procesos.",
        "no_jobs_hint":   "Usa el sidebar para subir un archivo o haz clic en <strong>⚡ Cargar CSV de ejemplo</strong>.",
        "no_tasks_title": "Aún no hay tareas programadas",
        "no_tasks_hint":  (
            "Crea una tarea para procesar archivos automáticamente en un horario.<br>"
            "Ejemplo: procesar <strong>ventas.csv</strong> cada lunes a las 8am "
            "y recibir una alerta por Telegram."
        ),
        # Errors
        "err_api":        "❌ Error API {code}: {detail}",
        "err_connect":    "❌ No se puede conectar a la API. Ejecuta: <code>uvicorn app.main:app --reload</code>",
        "err_api_down":   "⚠️ API no disponible. Inicia el backend: <code>uvicorn app.main:app --reload</code>",
        "err_job_failed": "❌ <strong>Proceso #{job_id} falló.</strong> {error}",
        "err_unexpected": "❌ Error inesperado: {error}",
        # Footer
        "footer": (
            "Automation Toolkit v1.0 · FastAPI + Streamlit + Polars · "
            "[API Docs](http://localhost:8000/docs) · "
            "[GitHub](https://github.com/Arcan17/automation-toolkit)"
        ),
    },
}


# ── Public helpers ─────────────────────────────────────────────────────────────

def t(key: str, **kwargs: object) -> str:
    """
    Return the translated string for *key* in the current UI language.

    Falls back to English when:
    - the requested language is not in _T
    - the key is missing from the requested language

    Supports .format()-style placeholders:
        t("task_created", name="My Task")
        → "✅ Task **My Task** created!"
    """
    lang  = st.session_state.get("lang", "en")
    table = _T.get(lang, _T["en"])
    text  = table.get(key) or _T["en"].get(key) or key
    # Only call .format() when kwargs are provided (avoids errors on plain strings)
    if kwargs and isinstance(text, str):
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text  # type: ignore[return-value]


def tl(key: str) -> list[str]:
    """
    Return a translated *list* for *key* (e.g. how_steps).
    Falls back to English if the key is missing.
    """
    lang  = st.session_state.get("lang", "en")
    table = _T.get(lang, _T["en"])
    result = table.get(key) or _T["en"].get(key) or []
    return result  # type: ignore[return-value]


def add_language(code: str, translations: dict) -> None:
    """
    Register a new language at runtime.

    Example — add Portuguese:
        from app.translations import add_language
        add_language("pt", {
            "app_tagline": "Faça upload de ficheiros CSV ou Excel...",
            ...
        })
    Any missing keys will fall back to English automatically.
    """
    _T[code] = translations
    LANGUAGES_REVERSE = {v: k for k, v in LANGUAGES.items()}
    # Caller must also add the display name to LANGUAGES dict if needed
