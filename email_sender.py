"""
Email Sender - Send certificates via email to participants
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Optional


class EmailSender:
    """Send certificates via email with custom templates."""
    
    def __init__(self, config: dict):
        """
        Initialize email sender with SMTP configuration.
        
        Args:
            config: Email configuration dictionary
        """
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.sender_email = config.get('sender_email', '')
        self.sender_password = config.get('sender_password', '')
        self.sender_name = config.get('sender_name', 'IEEE Student Branch')
        self.email_subject = config.get('email_subject', 'Your Participation Certificate')
        self.email_template = config.get('email_template', self._default_template())
        
    def _default_template(self) -> str:
        """Get default email template."""
        return """Dear {name},

Greetings from IEEE!

Thank you for attending the session. We truly appreciate your participation.

Please find attached your Participation Certificate for the event.

Best regards,
IEEE Student Branch"""
    
    def send_certificate(self, recipient_email: str, recipient_name: str, 
                        certificate_path: str) -> bool:
        """
        Send certificate via email to a participant.
        
        Args:
            recipient_email: Recipient's email address
            recipient_name: Recipient's name
            certificate_path: Path to the certificate PDF
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = self.email_subject
            
            # Format email body with recipient name
            body = self.email_template.format(name=recipient_name)
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach certificate PDF
            if os.path.exists(certificate_path):
                with open(certificate_path, 'rb') as f:
                    pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
                    pdf_attachment.add_header(
                        'Content-Disposition', 
                        'attachment', 
                        filename=os.path.basename(certificate_path)
                    )
                    msg.attach(pdf_attachment)
            else:
                print(f"  Warning: Certificate file not found: {certificate_path}")
                return False
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"  Error sending email to {recipient_email}: {e}")
            return False
    
    def send_batch(self, participants: list, certificate_dir: str, 
                   filename_template: str = "{name}_certificate.pdf") -> tuple:
        """
        Send certificates to multiple participants.
        
        Args:
            participants: List of dicts with 'name' and 'email' keys
            certificate_dir: Directory containing certificates
            filename_template: Template for certificate filenames
            
        Returns:
            Tuple of (successful_count, failed_count, failed_list)
        """
        successful = 0
        failed = 0
        failed_list = []
        
        for i, participant in enumerate(participants, 1):
            name = participant.get('name', '')
            email = participant.get('email', '')
            
            if not email or not name:
                print(f"  ✗ Skipping participant {i}: Missing name or email")
                failed += 1
                failed_list.append({'name': name, 'email': email, 'reason': 'Missing name or email'})
                continue
            
            # Clean name for filename
            clean_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
            filename = filename_template.format(name=clean_name, index=i)
            certificate_path = os.path.join(certificate_dir, filename)
            
            print(f"Sending email {i}/{len(participants)}: {name} ({email})")
            
            if self.send_certificate(email, name, certificate_path):
                successful += 1
                print(f"  ✓ Email sent successfully")
            else:
                failed += 1
                failed_list.append({'name': name, 'email': email, 'reason': 'Sending failed'})
                print(f"  ✗ Failed to send email")
        
        return successful, failed, failed_list
