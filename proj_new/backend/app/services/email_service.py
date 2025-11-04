"""
Email Service
可在日誌模式（預設）或 SMTP 模式下發送郵件。

環境變數 / Flask config 支援：
  SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD,
  SMTP_USE_TLS (bool), SMTP_USE_SSL (bool), SMTP_FROM

若未配置 SMTP_HOST，會退回到僅記錄日誌與列印行為（與原先行為相容）。
"""
import smtplib
from email.message import EmailMessage
from flask import current_app


class EmailService:
    """郵件服務，支持真實 SMTP 發送或回退到日誌打印。"""

    def _send_via_smtp(self, subject: str, to_email: str, body: str, html: str | None = None) -> bool:
        cfg = current_app.config
        host = cfg.get('SMTP_HOST')
        if not host:
            # SMTP 未配置，回退到日誌模式
            current_app.logger.warning('[EMAIL - STUB MODE] SMTP not configured, printing message')
            current_app.logger.warning(body)
            print(body)
            return True

        port = int(cfg.get('SMTP_PORT', 587))
        user = cfg.get('SMTP_USER')
        password = cfg.get('SMTP_PASSWORD')
        use_ssl = bool(cfg.get('SMTP_USE_SSL', False))
        use_tls = bool(cfg.get('SMTP_USE_TLS', True))
        from_addr = cfg.get('SMTP_FROM', cfg.get('MAIL_DEFAULT_SENDER', 'no-reply@example.com'))

        # Log the SMTP configuration (avoid logging passwords)
        try:
            # use WARNING so it appears in default logs (INFO may be filtered)
            current_app.logger.warning(
                f"SMTP config: host={host!r}, port={port!r}, user_present={bool(user)}, use_ssl={use_ssl}, use_tls={use_tls}, from={from_addr!r}"
            )
        except Exception:
            # best-effort logging; do not fail sending if logging fails
            pass

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = to_email
        msg.set_content(body)
        if html:
            msg.add_alternative(html, subtype='html')

        try:
            if use_ssl:
                server = smtplib.SMTP_SSL(host, port, timeout=10)
            else:
                server = smtplib.SMTP(host, port, timeout=10)

            server.ehlo()
            if use_tls and not use_ssl:
                server.starttls()
                server.ehlo()

            if user and password:
                server.login(user, password)

            server.send_message(msg)
            server.quit()
            # log at WARNING so it's visible in container logs
            current_app.logger.warning(f"Sent email to {to_email} via SMTP {host}:{port}")
            return True
        except Exception as e:
            current_app.logger.error(f"Failed to send email via SMTP to {to_email}: {e}")
            # fallback to logging the message body so tests/dev can still find codes
            current_app.logger.warning('[EMAIL - FALLBACK]')
            current_app.logger.warning(body)
            print(body)
            return False

    def send_verification_email(self, user_email: str, username: str, token: str) -> bool:
        verify_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={token}"
        subject = f"[{current_app.config.get('APP_NAME','App')}] 驗證您的 Email"
        body = f"請點擊以下連結以驗證您的 Email:\n\n{verify_url}\n\n或在前端輸入 token: {token}\n\n此 token 24 小時內有效。"
        return self._send_via_smtp(subject, user_email, body)

    def send_password_reset_email(self, user_email: str, username: str, token: str) -> bool:
        reset_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"
        subject = f"[{current_app.config.get('APP_NAME','App')}] 重置密碼"
        body = f"請點擊以下連結以重置密碼:\n\n{reset_url}\n\n或在前端輸入 token: {token}\n\n此 token 1 小時內有效。"
        return self._send_via_smtp(subject, user_email, body)

    def send_registration_code_email(self, user_email: str, username: str, code: str, expires_minutes: int = 15) -> bool:
        subject = f"[{current_app.config.get('APP_NAME','App')}] 註冊驗證碼"
        body = f"您的註冊驗證碼為： {code}\n此驗證碼於 {expires_minutes} 分鐘後失效。如非您本人操作，請忽略本信。"
        return self._send_via_smtp(subject, user_email, body)


# 創建單例
email_service = EmailService()
