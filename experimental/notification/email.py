import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .services.service import Service


class Email(Service):
    """Email notification service using SMTP."""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = 587, 
                 username: str = None, password: str = None, 
                 from_email: str = None, to_emails: list = None):
        """Initialize Email service.
        
        Args:
            smtp_server: SMTP server address. Defaults to SMTP_SERVER env var.
            smtp_port: SMTP server port. Defaults to SMTP_PORT env var or 587.
            username: SMTP username. Defaults to SMTP_USERNAME env var.
            password: SMTP password. Defaults to SMTP_PASSWORD env var.
            from_email: Sender email address. Defaults to SMTP_FROM_EMAIL env var.
            to_emails: List of recipient emails. Defaults to SMTP_TO_EMAILS env var (comma-separated).
            
        Raises:
            ValueError: If required configuration is missing.
        """
        self.smtp_server = smtp_server or os.getenv("SMTP_SERVER")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.username = username or os.getenv("SMTP_USERNAME")
        self.password = password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("SMTP_FROM_EMAIL")
        
        if to_emails:
            self.to_emails = to_emails
        else:
            to_emails_str = os.getenv("SMTP_TO_EMAILS", "")
            self.to_emails = [email.strip() for email in to_emails_str.split(",") if email.strip()]
        
        if not all([self.smtp_server, self.username, self.password, self.from_email, self.to_emails]):
            raise ValueError("Email service requires SMTP server, username, password, from_email, and to_emails")

    def send_notification(self, message: str) -> None:
        """Send notification via email.
        
        Args:
            message: The message to send.
            
        Raises:
            Exception: If email sending fails.
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = ", ".join(self.to_emails)
            msg['Subject'] = "PySmle Training Notification"
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
                
        except Exception as err:
            raise Exception(f"Failed to send email notification: {err}")
