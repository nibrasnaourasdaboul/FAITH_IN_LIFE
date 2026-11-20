import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.core.config import get_settings
from app.core.errors import AppError

logger = logging.getLogger(__name__)


# يختار عنوان المُرسِل، ويفضّل حساب جيميل إذا كان العنوان الافتراضي غير صالح.
def _from_address(settings) -> str:
    sender = settings.smtp_from
    if settings.smtp_user and (not sender or sender.endswith(".local>") or "@" not in sender):
        return settings.smtp_user
    return sender


# يرسل الرسالة عبر خادم البريد بشكل متزامن.
def _send_sync(recipient: str, subject: str, text: str, html: str) -> None:
    settings = get_settings()
    message = EmailMessage()
    message["From"] = _from_address(settings)
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(text)
    message.add_alternative(html, subtype="html")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        if settings.smtp_tls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password.replace(" ", ""))
        smtp.send_message(message)


# يرسل الرسالة في خيط منفصل ويتوقف إذا رفض جيميل الإرسال.
async def send_email(recipient: str, subject: str, text: str, html: str) -> None:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP is not configured. No email was sent to %s.", recipient)
        raise AppError(
            "email_not_configured",
            503,
            "The verification email could not be sent because Gmail is not connected.",
        )
    try:
        await asyncio.to_thread(_send_sync, recipient, subject, text, html)
    except Exception as exc:
        logger.exception("SMTP delivery to %s failed", recipient)
        raise AppError("email_failed", 502, "Gmail refused the verification email.") from exc


# يجهّز نص رسالة رمز التحقق بالعربية أو الإنجليزية.
def otp_copy(locale: str, purpose: str, code: str) -> tuple[str, str, str]:
    minutes = get_settings().otp_minutes
    if locale == "en":
        title = "Verify your email" if purpose == "verify" else "Reset your password"
        text = (
            f"{title}\n\nYour FAITH in LIFE code is {code}. "
            f"It expires in {minutes} minutes. If you did not request this, ignore the message."
        )
    else:
        title = "تأكيد البريد الإلكتروني" if purpose == "verify" else "استعادة كلمة المرور"
        text = (
            f"{title}\n\nرمز إيمان في الحياة هو {code}. "
            f"تنتهي صلاحيته خلال {minutes} دقائق. إذا لم تطلب ذلك، تجاهل الرسالة."
        )
    html = f"""
    <div style="font-family:Tahoma,Arial,sans-serif;background:#f4f1ea;padding:32px">
      <div style="max-width:480px;margin:auto;background:#fff;border-radius:24px;padding:32px">
        <p style="color:#1f6f68;font-weight:700;margin:0">FAITH IN LIFE</p>
        <h1 style="color:#17312f">{title}</h1>
        <p style="font-size:32px;letter-spacing:8px;font-weight:700;color:#1f6f68">{code}</p>
        <p style="color:#5e6f6c">{text.split(chr(10))[-1]}</p>
      </div>
    </div>
    """
    return title, text, html


# يرسل رمز التحقق أو الاستعادة إلى بريد المستخدم.
async def send_otp(recipient: str, locale: str, purpose: str, code: str) -> None:
    subject, text, html = otp_copy(locale, purpose, code)
    await send_email(recipient, subject, text, html)
