# Email Setup Guide 📧

This guide will help you set up email functionality to automatically send certificates to participants.

## Quick Setup

### Step 1: Update Your Participants File

Your CSV/Excel file must have both `Name` and `Email` columns:

```csv
Name,Email
John Doe,john.doe@example.com
Jane Smith,jane.smith@example.com
```

### Step 2: Configure Email Settings

Edit `config.json` and fill in the email section:

```json
"email": {
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@gmail.com",
  "sender_password": "your-app-password",
  "sender_name": "IEEE Student Branch MGMCET",
  "email_subject": "Your IEEE Event Participation Certificate",
  "email_template_file": "email_template.txt"
}
```

### Step 3: Get Gmail App Password (Recommended)

For Gmail users:

1. **Enable 2-Step Verification** on your Google Account
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Create App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it "Certificate Generator"
   - Copy the 16-character password

3. **Update config.json**
   ```json
   "sender_email": "your-email@gmail.com",
   "sender_password": "xxxx xxxx xxxx xxxx"
   ```

⚠️ **IMPORTANT**: Use App Password, NOT your regular Gmail password!

### Step 4: Customize Email Template

Edit `email_template.txt` to customize your message:

```
Dear {name},

Greetings from IEEE!

Your custom message here...

Best regards,
IEEE Student Branch
```

The `{name}` placeholder will be replaced with each participant's name.

### Step 5: Send Certificates via Email

```bash
./venv/bin/python main.py --participants participants.csv --send-email
```

## Usage Examples

### Generate Only (No Email)
```bash
./venv/bin/python main.py --participants participants.csv
```

### Generate + Send Emails
```bash
./venv/bin/python main.py --participants participants.csv --send-email
```

### Use Different Config
```bash
./venv/bin/python main.py -c custom_config.json -p participants.csv --send-email
```

## Alternative Email Providers

### Outlook/Hotmail
```json
"smtp_server": "smtp-mail.outlook.com",
"smtp_port": 587
```

### Yahoo Mail
```json
"smtp_server": "smtp.mail.yahoo.com",
"smtp_port": 587
```

### Custom SMTP Server
```json
"smtp_server": "mail.yourdomain.com",
"smtp_port": 587
```

## Troubleshooting

### "Username and Password not accepted"

**Gmail Users:**
- Make sure you're using an App Password, not your regular password
- Verify 2-Step Verification is enabled
- Check that you copied the App Password correctly (remove spaces)

**Other Providers:**
- Enable "Less secure app access" if required
- Check if your email provider requires app-specific passwords
- Verify SMTP server and port are correct

### "Connection refused" or "Timeout"

- Check your internet connection
- Verify firewall isn't blocking port 587
- Try using port 465 with SSL instead
- Check SMTP server address is correct

### Emails Not Received

- Check spam/junk folders
- Verify recipient email addresses are correct
- Check sender email is verified/not blocked
- Test with your own email first

### SSL/TLS Errors

Try changing the port:
- Port 587: STARTTLS (most common)
- Port 465: SSL/TLS
- Port 25: Plain/STARTTLS (often blocked)

## Testing Email Setup

Create a test CSV with just your own email:

```csv
Name,Email
Test User,your-email@gmail.com
```

Then run:
```bash
./venv/bin/python main.py -p test.csv --send-email
```

Check if you received the email before sending to all participants.

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use App Passwords** instead of account passwords
3. **Keep config.json private** - add to `.gitignore`
4. **Use environment variables** for production (optional):
   ```bash
   export EMAIL_PASSWORD="your-app-password"
   ```

## Email Template Variables

Available placeholders in `email_template.txt`:
- `{name}` - Participant's name (required)

The template supports plain text only (no HTML).

## Rate Limiting

- Gmail: ~500 emails/day limit
- For large batches, consider:
  - Splitting into smaller groups
  - Using a dedicated email service (SendGrid, Mailgun)
  - Adding delays between emails

---

**Need Help?** Check the main README.md or raise an issue.
