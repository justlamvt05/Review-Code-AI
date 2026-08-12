import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import settings
from core.logger import logger


class EmailService:
    """Gửi email thông qua SMTP."""

    @staticmethod
    def send_email(to_email: str, subject: str, html_body: str) -> bool:
        """
        Gửi email HTML.

        Args:
            to_email: Địa chỉ email người nhận.
            subject: Tiêu đề email.
            html_body: Nội dung email (HTML).

        Returns:
            True nếu gửi thành công, False nếu thất bại.
        """
        if not settings.email_enabled:
            logger.info(f"Email disabled. Skipping email to {to_email}: {subject}")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(html_body, "html", "utf-8"))

            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    def build_comment_notification_html(
        commenter_name: str,
        review_content: str,
        comment_content: str,
    ) -> str:
        """Build HTML template cho comment notification."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #333;">💬 New Comment on Your Review</h2>
            <p><strong>{commenter_name}</strong> commented on your review:</p>
            <blockquote style="border-left: 4px solid #4A90D9; padding: 10px 15px; background: #f5f5f5; margin: 10px 0;">
                {comment_content}
            </blockquote>
            <p style="color: #666;">Review: <em>{review_content[:200]}...</em></p>
            <hr style="border: none; border-top: 1px solid #eee;">
            <p style="color: #999; font-size: 12px;">
                This is an automated notification from ReviewCodeWeb.
            </p>
        </body>
        </html>
        """

    @staticmethod
    def build_reply_notification_html(
        replier_name: str,
        original_comment: str,
        reply_content: str,
    ) -> str:
        """Build HTML template cho reply notification."""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #333;">↩️ New Reply to Your Comment</h2>
            <p><strong>{replier_name}</strong> replied to your comment:</p>
            <div style="margin: 10px 0;">
                <p style="color: #666;">Your comment:</p>
                <blockquote style="border-left: 4px solid #ccc; padding: 10px 15px; background: #fafafa;">
                    {original_comment}
                </blockquote>
            </div>
            <div style="margin: 10px 0;">
                <p style="color: #666;">Reply:</p>
                <blockquote style="border-left: 4px solid #4A90D9; padding: 10px 15px; background: #f5f5f5;">
                    {reply_content}
                </blockquote>
            </div>
            <hr style="border: none; border-top: 1px solid #eee;">
            <p style="color: #999; font-size: 12px;">
                This is an automated notification from ReviewCodeWeb.
            </p>
        </body>
        </html>
        """
