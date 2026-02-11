import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket

def test_email():
    print("📧 Email Configuration Test")
    print("-" * 30)
    
    # Default values from your app
    default_sender = "mgmcet.ieee@gmail.com"
    default_password = "phj hnn ozr oxr ivub" # CAREFUL: This is hardcoded in your app.py
    
    print(f"Default Sender: {default_sender}")
    
    # Ask for confirmation or new details
    use_default = input(f"Use default credentials? (y/n): ").lower().strip()
    
    if use_default == 'y':
        sender_email = default_sender
        sender_password = default_password
    else:
        sender_email = input("Enter Sender Email: ").strip()
        sender_password = input("Enter Google App Password: ").strip()
        
    recipient_email = input("Enter Recipient Email (to send test to): ").strip()
    
    print("\n🚀 Attempting to send test email...")
    
    try:
        # 1. Test Connectivity
        print("   Resolving smtp.gmail.com...")
        host = 'smtp.gmail.com'
        port = 587
        
        try:
            socket.create_connection((host, port), timeout=5)
            print("   ✅ Server is reachable")
        except OSError as e:
            print(f"   ❌ Network Error: Could not reach {host}:{port}")
            print(f"   Error: {e}")
            return

        # 2. Test Login & Send
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "IEEE Certificate Generator - Test Email"
        
        body = "This is a test email to verify your SMTP configuration."
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(host, port)
        server.set_debuglevel(1) # Show full debug output
        server.starttls()
        
        print("   Logging in...")
        server.login(sender_email, sender_password)
        print("   ✅ Login Successful!")
        
        print("   Sending message...")
        server.send_message(msg)
        print("   ✅ Email Sent Successfully!")
        
        server.quit()
        
    except smtplib.SMTPAuthenticationError as e:
        print("\n❌ Authentication Failed!")
        print(f"   Error: {e}")
        print("   Tip: Check your App Password. It should be 16 chars, no spaces (or with spaces is fine for some clients but try without).")
        print("   Make sure 2-Step Verification is ON and you generated a specific App Password for 'Mail'.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_email()
