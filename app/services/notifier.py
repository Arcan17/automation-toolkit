"""
Multi-channel notification service.
Supports Telegram, Email (SMTP), and WhatsApp (Twilio).
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


def _build_message(job_id: int, filename: str, stats: dict) -> str:
    return (
        f"✅ *Automation Toolkit — Job #{job_id} Complete*\n\n"
        f"📄 File: `{filename}`\n"
        f"📊 Rows processed: {stats.get('rows_raw', 0):,}\n"
        f"🧹 Duplicates removed: {stats.get('duplicates_removed', 0):,}\n"
        f"🔧 Nulls filled: {stats.get('nulls_filled', 0):,}\n"
        f"✔️ Clean rows: {stats.get('rows_clean', 0):,}\n"
        f"🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )


async def send_telegram(job_id: int, filename: str, stats: dict) -> bool:
    """Send Telegram notification using python-telegram-bot."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.warning("Telegram not configured — skipping")
        return False
    try:
        from telegram import Bot
        bot = Bot(token=settings.telegram_bot_token)
        text = _build_message(job_id, filename, stats)
        await bot.send_message(
            chat_id=settings.telegram_chat_id,
            text=text,
            parse_mode="Markdown",
        )
        logger.info(f"Telegram notification sent for job {job_id}")
        return True
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return False


def send_email(job_id: int, filename: str, stats: dict, to_email: str) -> bool:
    """Send Email notification via SMTP."""
    if not all([settings.smtp_user, settings.smtp_password, settings.smtp_from]):
        logger.warning("Email not configured — skipping")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"✅ Job #{job_id} complete — {filename}"
        msg["From"] = settings.smtp_from
        msg["To"] = to_email

        body = _build_message(job_id, filename, stats).replace("*", "").replace("`", "")
        html = f"<pre style='font-family:monospace'>{body}</pre>"

        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_from, to_email, msg.as_string())

        logger.info(f"Email sent to {to_email} for job {job_id}")
        return True
    except Exception as e:
        logger.error(f"Email error: {e}")
        return False


def send_whatsapp(job_id: int, filename: str, stats: dict, to_number: str) -> bool:
    """Send WhatsApp notification via Twilio."""
    if not all([settings.twilio_account_sid, settings.twilio_auth_token]):
        logger.warning("Twilio not configured — skipping")
        return False
    try:
        from twilio.rest import Client
        client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        body = _build_message(job_id, filename, stats).replace("*", "").replace("`", "")
        client.messages.create(
            body=body,
            from_=settings.twilio_whatsapp_from,
            to=f"whatsapp:{to_number}",
        )
        logger.info(f"WhatsApp sent to {to_number} for job {job_id}")
        return True
    except Exception as e:
        logger.error(f"WhatsApp error: {e}")
        return False
