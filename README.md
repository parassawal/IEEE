# Certificate Generator 📜

Automatically generate participation certificates by overlaying participant names on a PDF template, and optionally send them via email.

---

## 🌐 Web App (Streamlit) - NEW!

**Try it online:** [Deploy to Streamlit Cloud](https://share.streamlit.io) *(Free!)*

### Features
- 📤 **Upload Template**: Drag and drop your certificate PDF
- 📊 **Upload CSV**: Batch upload participant names
- 🎨 **Visual Positioning**: Interactive controls to position text
- 👁️ **Live Preview**: See changes in real-time
- 📦 **Bulk Download**: Download all certificates as ZIP
- ⚙️ **Customize**: Font, size, color, and alignment
- 💾 **Save Config**: Export/import configuration

### Quick Start (Web)
1. Run locally: `streamlit run app.py`
2. Upload your certificate template PDF
3. Adjust text position using the sidebar controls
4. Upload your participants CSV (must have a 'Name' column)
5. Preview with the first participant
6. Generate all certificates and download ZIP

### Deploy to Streamlit Cloud (Free!)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Streamlit web app"
   git push
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Click "Deploy"!

3. **Your app will be live** at: `https://[your-username]-certificate-generator.streamlit.app`

---


## Features ✨

- **Batch Processing**: Generate certificates for hundreds of participants in seconds
- **Email Integration**: Automatically send certificates via email 📧
- **Flexible Input**: Support for CSV and Excel files  
- **Customizable**: Configure position, font, size, color, and alignment
- **Easy to Use**: Simple command-line interface
- **Position Helper**: Tool to help you find the right coordinates

## Installation 🚀

1. **Install Python** (3.8 or higher)

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start 🎯

### Step 1: Prepare Your Files

1. **Certificate Template**: Your PDF certificate with a blank space for the name
2. **Participants List**: A CSV or Excel file with participant names (and emails if sending via email)

Example CSV (`participants.csv`):
```csv
Name,Email
John Smith,john@example.com
Jane Doe,jane@example.com
```

### Step 2: Find the Right Position

Use the position helper to analyze your certificate:

```bash
./venv/bin/python position_helper.py "../_Certificate of Appreciation.pdf"
```

This will show you the PDF dimensions and suggest starting coordinates.

### Step 3: Configure Settings

Edit `config.json` with the suggested coordinates and email settings (if using email).

### Step 4: Generate Certificates

**Without Email:**
```bash
./venv/bin/python main.py --participants participants.csv
```

**With Email:**
```bash
./venv/bin/python main.py --participants participants.csv --send-email
```

Your certificates will be in the `output/` folder!

## Email Setup 📧

To send certificates via email:

1. **Add Email column** to your CSV:
   ```csv
   Name,Email
   John Doe,john@example.com
   ```

2. **Configure email settings** in `config.json`:
   ```json
   "email": {
     "sender_email": "your-email@gmail.com",
     "sender_password": "your-app-password",
     "sender_name": "IEEE Student Branch MGMCET"
   }
   ```

3. **Get Gmail App Password**: See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed instructions

4. **Customize email message** in `email_template.txt`

5. **Send certificates**:
   ```bash
   ./venv/bin/python main.py --participants participants.csv --send-email
   ```

📖 **Full email setup guide**: [EMAIL_SETUP.md](EMAIL_SETUP.md)

## Configuration Guide ⚙️

### Position Settings

- **x_position**: Horizontal position (0 = left edge)
- **y_position**: Vertical position (0 = bottom edge, increases upward)
- **alignment**: `"left"`, `"center"`, or `"right"`

### Font Settings

- **font_name**: Built-in options:
  - `"Helvetica"`, `"Helvetica-Bold"`
  - `"Times-Roman"`, `"Times-Bold"`
  - `"Courier"`, `"Courier-Bold"`
- **font_size**: Size in points (e.g., 36, 48, 72)
- **font_color**: Hex color code (e.g., `"#000000"` for black)
- **custom_font_path**: Path to a custom TTF font file (optional)

### Output Settings

- **output_dir**: Where to save generated certificates
- **filename_template**: Pattern for output filenames
  - Use `{name}` for participant name
  - Example: `"{name}_Certificate.pdf"` → `John_Smith_Certificate.pdf`

### Email Settings

See [EMAIL_SETUP.md](EMAIL_SETUP.md) for complete email configuration guide.

## Usage Examples 📖

### Basic Usage (No Email)
```bash
./venv/bin/python main.py --participants participants.csv
```

### Generate + Send Emails
```bash
./venv/bin/python main.py --participants participants.csv --send-email
```

### Custom Output Directory
```bash
./venv/bin/python main.py --participants participants.csv -o ./my_certificates
```

### Use Different Template
```bash
./venv/bin/python main.py --participants participants.csv -t ./my_template.pdf
```

### Use Different Config File
```bash
./venv/bin/python main.py -c custom_config.json -p participants.csv
```

### Test with Sample Data
```bash
./venv/bin/python main.py --participants examples/sample_participants.csv
```

## Troubleshooting 🔧

### Names Not Positioned Correctly

1. Run the position helper:
   ```bash
   ./venv/bin/python position_helper.py "your_template.pdf"
   ```

2. Generate a test certificate with one name

3. Adjust `x_position` and `y_position` in `config.json`:
   - **Name too high?** → DECREASE `y_position`
   - **Name too low?** → INCREASE `y_position`
   - **Name too left?** → INCREASE `x_position`
   - **Name too right?** → DECREASE `x_position`

4. Repeat until perfect!

### Email Issues

See [EMAIL_SETUP.md](EMAIL_SETUP.md) for comprehensive email troubleshooting.

Common issues:
- **"Username and Password not accepted"**: Use App Password for Gmail
- **"Connection refused"**: Check firewall and SMTP settings
- **Emails not received**: Check spam folder

### CSV/Excel Errors

- Ensure your file has a column with "Name" in the header
- For email sending, also include an "Email" column
- Check for empty rows or cells
- Save Excel files in `.xlsx` format

## File Structure 📁

```
certificate-generator/
├── certificate_generator.py  # Core generator class
├── email_sender.py           # Email sending module
├── main.py                   # Command-line interface
├── position_helper.py        # Tool to find coordinates
├── config.json               # Configuration file
├── email_template.txt        # Email message template
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── EMAIL_SETUP.md           # Email setup guide
├── examples/
│   └── sample_participants.csv
└── output/                   # Generated certificates
```

## Tips for Best Results 💡

1. **High-Quality Template**: Use a high-resolution PDF for best results
2. **Test First**: Generate 1-2 certificates first to verify positioning
3. **Backup**: Keep a copy of your original template
4. **Font Matching**: Try to match the font on your certificate
5. **Email Testing**: Test email with your own address first
6. **Batch Processing**: For large lists, generate certificates first, verify them, then send emails

## Support 🤝

Having issues? Check:
1. All file paths in `config.json` are correct
2. Your participants file has a `Name` column (and `Email` if sending emails)
3. The template PDF exists and is readable
4. All dependencies are installed: `pip install -r requirements.txt`
5. Email credentials are correct (see EMAIL_SETUP.md)

---

**Happy Certificate Generating! 🎉**
