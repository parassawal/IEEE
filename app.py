#!/usr/bin/env python3
"""
Streamlit Web App for Certificate Generator
Deploy to Streamlit Cloud: https://streamlit.io/cloud
"""
import streamlit as st
import os
import json
import tempfile
import zipfile
import shutil
from pathlib import Path
from io import BytesIO
import pandas as pd
from certificate_generator import CertificateGenerator
from email_sender import EmailSender
from pypdf import PdfReader
from pdf2image import convert_from_bytes
from PIL import Image
import qrcode
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Certificate Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for IEEE branding
st.markdown("""
<style>
    /* IEEE Blue Color Palette */
    :root {
        --ieee-blue: #00629B;
        --ieee-dark-blue: #003D5C;
        --ieee-light-blue: #0077C8;
        --ieee-gold: #FFB81C;
    }
    
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00629B 0%, #003D5C 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        color: #003D5C;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        text-align: center;
        font-weight: 500;
    }
    
    /* IEEE-styled buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #00629B 0%, #0077C8 100%);
        color: white;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        box-shadow: 0 4px 6px rgba(0, 98, 155, 0.2);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #003D5C 0%, #00629B 100%);
        box-shadow: 0 6px 12px rgba(0, 98, 155, 0.3);
        transform: translateY(-2px);
    }
    
    /* Primary button styling */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #FFB81C 0%, #FFA500 100%);
        color: #003D5C;
        font-weight: 700;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #FFA500 0%, #FFB81C 100%);
    }
    
    /* IEEE accent borders */
    .success-box {
        padding: 1rem;
        background-color: #E8F4F8;
        border-left: 5px solid #00629B;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1rem;
        background-color: #FFF8E1;
        border-left: 5px solid #FFB81C;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #00629B 0%, #003D5C 100%);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    
    /* File uploader styling */
    .stFileUploader {
        border: 2px dashed #00629B;
        border-radius: 8px;
        padding: 1rem;
        background: #F8FBFD;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00629B 0%, #FFB81C 100%);
    }
    
    /* Headers accent */
    h1, h2, h3 {
        color: #003D5C !important;
    }
    
    /* Divider styling */
    hr {
        border-top: 2px solid #00629B;
        opacity: 0.3;
    }
    
    /* Hide GitHub and deployment menu items */
    [data-testid="stToolbar"] {
        display: none;
    }
    
    header[data-testid="stHeader"] {
        display: none;
    }
    
    .viewerBadge_container__1QSob {
        display: none;
    }
    
    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'config' not in st.session_state:
    st.session_state.config = {
        'x_position': 421,
        'y_position': 268,
        'font_name': 'Helvetica-Bold',
        'font_size': 36,
        'font_color': '#000000',
        'alignment': 'center',
        'filename_template': '{name}_Certificate.pdf'
    }

if 'template_file' not in st.session_state:
    st.session_state.template_file = None

if 'participants_data' not in st.session_state:
    st.session_state.participants_data = None

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'send_emails_enabled' not in st.session_state:
    st.session_state.send_emails_enabled = False

# Registration file path
REGISTRATIONS_FILE = "registrations.json"

# Helper functions for registration management
def load_registrations():
    """Load all registrations from JSON file"""
    if os.path.exists(REGISTRATIONS_FILE):
        try:
            with open(REGISTRATIONS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def save_registration(name, email):
    """Save a new registration"""
    registrations = load_registrations()
    
    # Check for duplicate email
    if any(r['email'].lower() == email.lower() for r in registrations):
        return False, "Email already registered!"
    
    # Add new registration
    new_registration = {
        'name': name,
        'email': email,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    registrations.append(new_registration)
    
    # Save to file
    with open(REGISTRATIONS_FILE, 'w') as f:
        json.dump(registrations, f, indent=2)
    
    return True, "Registration successful!"

def delete_registration(email):
    """Delete a registration by email"""
    registrations = load_registrations()
    registrations = [r for r in registrations if r['email'].lower() != email.lower()]
    with open(REGISTRATIONS_FILE, 'w') as f:
        json.dump(registrations, f, indent=2)

def generate_qr_code(url):
    """Generate QR code for a URL"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#00629B", back_color="white")
    return img

# Static credentials
ADMIN_EMAIL = "mgmcet.ieee@gmail.com"
ADMIN_PASSWORD = "earthling-plasma5-overstock-explain"

def login_page():
    """Display login page"""
    st.markdown('<h1 class="main-header">⚡ IEEE Certificate Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Secure Login | IEEE Student Branch MGMCET</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            email = st.text_input("📧 Email", placeholder="Enter your email")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            
            submit = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submit:
                if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid email or password. Please try again.")

def convert_pdf_to_image(pdf_bytes):
    """Convert first page of PDF to image for preview"""
    try:
        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=150)
        return images[0] if images else None
    except Exception as e:
        st.error(f"Error converting PDF to image: {e}")
        return None

def load_participants_from_csv(uploaded_file, include_emails=False):
    """Load participants from uploaded CSV file"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Find name column
        name_column = None
        email_column = None
        
        for col in df.columns:
            if 'name' in col.lower():
                name_column = col
            if 'email' in col.lower() or 'mail' in col.lower():
                email_column = col
        
        if name_column is None:
            st.error(f"No 'Name' column found. Available columns: {', '.join(df.columns)}")
            return None
        
        if include_emails:
            if email_column is None:
                st.error(f"No 'Email' column found. Available columns: {', '.join(df.columns)}")
                st.info("For email sending, your CSV must have both 'Name' and 'Email' columns.")
                return None
            
            # Return list of dicts with name and email
            participants = []
            for _, row in df.iterrows():
                name = str(row[name_column]) if pd.notna(row[name_column]) else None
                email = str(row[email_column]) if pd.notna(row[email_column]) else None
                if name and email:
                    participants.append({'name': name, 'email': email})
            
            if not participants:
                st.error("No valid participant data found in the file.")
                return None
            
            return participants
        else:
            # Extract names only
            names = df[name_column].dropna().astype(str).tolist()
            
            if not names:
                st.error("No participant names found in the file.")
                return None
            
            return names
        
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None

def generate_certificates_zip(generator, names, config):
    """Generate all certificates and return as ZIP file"""
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, name in enumerate(names):
            status_text.text(f"Generating certificate {i+1}/{len(names)}: {name}")
            
            # Generate certificate to temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            try:
                if generator.generate_certificate(name, tmp_path):
                    # Add to ZIP
                    clean_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
                    filename = config.get('filename_template', '{name}_Certificate.pdf').format(name=clean_name)
                    zip_file.write(tmp_path, filename)
            finally:
                # Clean up temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            
            # Update progress
            progress_bar.progress((i + 1) / len(names))
        
        status_text.text("✅ All certificates generated successfully!")
    
    zip_buffer.seek(0)
    return zip_buffer

def registration_page():
    """Public registration page - no login required"""
    st.markdown('<h1 class="main-header">⚡ IEEE Event Registration</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Register for our event | IEEE Student Branch MGMCET</p>', unsafe_allow_html=True)
    
    st.info("📝 Fill out the form below to register for the event. You'll receive your certificate after the event!")
    
    with st.form("registration_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            name = st.text_input("📛 Full Name *", placeholder="Enter your full name")
            email = st.text_input("📧 Email Address *", placeholder="Enter your email")
            
            submit = st.form_submit_button("🚀 Register Now", use_container_width=True)
            
            if submit:
                if not name or not email:
                    st.error("❌ Please fill in all fields!")
                elif "@" not in email or "." not in email:
                    st.error("❌ Please enter a valid email address!")
                else:
                    success, message = save_registration(name.strip(), email.strip())
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.info("🎓 You're registered! You'll receive your certificate after the event.")
                    else:
                        st.warning(f"⚠️ {message}")
    
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem 0;">
        <p style="font-size: 0.9rem;">Powered by IEEE Student Branch MGMCET</p>
    </div>
    """, unsafe_allow_html=True)

def view_responses_page():
    """Admin page to view and manage registrations"""
    st.markdown('<h2 class="main-header">📊 Registration Responses</h2>', unsafe_allow_html=True)
    
    registrations = load_registrations()
    
    # Display registration link and QR code
    st.subheader("🔗 Share Registration Link")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get current URL and create registration link
        try:
            registration_url = f"{st.query_params.get('url', 'https://your-app.streamlit.app')}?page=register"
        except:
            registration_url = "https://your-app.streamlit.app?page=register"
        
        st.text_input("Registration Link", value=registration_url, key="reg_link")
        if st.button("📋 Copy Link"):
            st.success("Link copied! (Use browser copy button)")
    
    with col2:
        st.write("**QR Code**")
        if st.button("📥 Generate & Download QR Code"):
            try:
                qr_img = generate_qr_code(registration_url)
                buf = BytesIO()
                qr_img.save(buf, format='PNG')
                buf.seek(0)
                
                st.image(buf, width=200)
                st.download_button(
                    label="💾 Download QR Code",
                    data=buf.getvalue(),
                    file_name="event_registration_qr.png",
                    mime="image/png"
                )
            except Exception as e:
                st.error(f"Error generating QR code: {e}")
    
    st.divider()
    
    # Statistics
    st.subheader("📈 Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Registrations", len(registrations))
    with col2:
        if registrations:
            latest = registrations[-1]['timestamp']
            st.metric("Latest Registration", latest.split()[0])
    with col3:
        st.metric("Status", "🟢 Active")
    
    st.divider()
    
    # Responses table
    st.subheader("👥 All Registrations")
    
    if registrations:
        df = pd.DataFrame(registrations)
        st.dataframe(df, use_container_width=True)
        
        # Export options
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Export to CSV",
                data=csv,
                file_name="registrations.csv",
                mime="text/csv"
            )
        
        with col2:
            if st.button("🎓 Use for Certificates"):
                st.session_state.participants_data = [
                    {'name': r['name'], 'email': r['email']} 
                    for r in registrations
                ]
                st.success(f"✅ Loaded {len(registrations)} participants for certificate generation!")
                st.info("👉 Go to the main tab to generate certificates")
        
        # Delete option
        st.divider()
        st.subheader("🗑️ Manage Registrations")
        email_to_delete = st.selectbox(
            "Select email to delete",
            [r['email'] for r in registrations]
        )
        if st.button("❌ Delete Selected", type="secondary"):
            delete_registration(email_to_delete)
            st.success("Registration deleted!")
            st.rerun()
    else:
        st.info("📭 No registrations yet. Share the registration link to start collecting responses!")

# Check if we're on the registration page (public access)
try:
    page = st.query_params.get("page", "")
except:
    page = ""

if page == "register":
    # Public registration page - no authentication needed
    registration_page()
elif not st.session_state.authenticated:
    # Admin login required
    login_page()
else:
    # Main app layout (only shown when authenticated)
    st.markdown('<h1 class="main-header">⚡ IEEE Certificate Generator</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Advancing Technology for Humanity | IEEE Student Branch MGMCET</p>', unsafe_allow_html=True)

    # Add tabs for navigation
    tab1, tab2 = st.tabs(["🎓 Certificate Generator", "📊 View Responses"])
    
    with tab1:
        # Original certificate generation code (sidebar + main content)
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Font settings
            st.subheader("Font Settings")
            st.session_state.config['font_name'] = st.selectbox(
                "Font",
                ['Helvetica-Bold', 'Helvetica', 'Times-Bold', 'Times-Roman', 'Courier-Bold', 'Courier'],
                index=0
            )
            
            st.session_state.config['font_size'] = st.slider(
                "Font Size",
                min_value=12,
                max_value=72,
                value=st.session_state.config['font_size']
            )
            
            st.session_state.config['font_color'] = st.color_picker(
                "Font Color",
                value=st.session_state.config['font_color']
            )
            
            # Alignment
            st.session_state.config['alignment'] = st.selectbox(
                "Alignment",
                ['center', 'left', 'right'],
                index=0
            )
            
            st.divider()
            
            # Position settings
            st.subheader("Position Settings")
            st.session_state.config['x_position'] = st.number_input(
                "X Position",
                min_value=0,
                max_value=1000,
                value=st.session_state.config['x_position'],
                help="Horizontal position of the text"
            )
            
            st.session_state.config['y_position'] = st.number_input(
                "Y Position",
                min_value=0,
                max_value=1000,
                value=st.session_state.config['y_position'],
                help="Vertical position of the text"
            )
            
            st.divider()
            
            # Save/Load configuration
            st.subheader("💾 Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Save Config"):
                    config_json = json.dumps(st.session_state.config, indent=2)
                    st.download_button(
                        label="Download",
                        data=config_json,
                        file_name="config.json",
                        mime="application/json"
                    )
            
            with col2:
                uploaded_config = st.file_uploader("Load Config", type=['json'], key='config_upload')
                if uploaded_config:
                    try:
                        config_data = json.load(uploaded_config)
                        st.session_state.config.update(config_data)
                        st.success("Config loaded!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading config: {e}")
            
            # Logout button at bottom
            st.divider()
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()

        # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📄 Step 1: Upload Certificate Template")
        template_file = st.file_uploader(
            "Upload PDF Template",
            type=['pdf'],
            help="Upload your certificate template PDF file"
        )
        
        if template_file:
            st.session_state.template_file = template_file
            st.success("✅ Template uploaded successfully!")
            
            # Show template preview
            st.subheader("📋 Template Preview")
            pdf_bytes = template_file.getvalue()
            preview_image = convert_pdf_to_image(pdf_bytes)
            
            if preview_image:
                st.image(preview_image, caption="Certificate Template", use_container_width=True)

    with col2:
        st.subheader("📊 Step 2: Upload Participants CSV")
        csv_file = st.file_uploader(
            "Upload CSV File",
            type=['csv'],
            help="CSV file with 'Name' column (and optionally 'Email')"
        )
        
        # Email sending toggle
        send_emails = st.checkbox("📧 Send certificates via email", value=False)
        st.session_state.send_emails_enabled = send_emails
        
        if csv_file:
            participants = load_participants_from_csv(csv_file, include_emails=send_emails)
            if participants:
                st.session_state.participants_data = participants
                
                if send_emails:
                    st.success(f"✅ Loaded {len(participants)} participants with emails")
                    # Show sample participants with emails
                    st.subheader("👥 Sample Participants")
                    sample_df = pd.DataFrame(participants[:5])
                    st.dataframe(sample_df, use_container_width=True)
                else:
                    st.success(f"✅ Loaded {len(participants)} participants")
                    # Show sample participants
                    st.subheader("👥 Sample Participants")
                    sample_df = pd.DataFrame({'Name': participants[:5]})
                    st.dataframe(sample_df, use_container_width=True)
                
                if len(participants) > 5:
                    st.info(f"... and {len(participants) - 5} more")

    # Preview and Generation Section
    st.divider()

    if st.session_state.template_file and st.session_state.participants_data:
        st.subheader("👁️ Step 3: Preview & Generate")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("**Preview with First Participant**")
            
            # Generate preview
            if st.button("🔄 Generate Preview", type="secondary"):
                with st.spinner("Generating preview..."):
                    try:
                        # Save template to temp file
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_template:
                            tmp_template.write(st.session_state.template_file.getvalue())
                            template_path = tmp_template.name
                        
                        # Generate preview certificate
                        generator = CertificateGenerator(template_path, st.session_state.config)
                        
                        # Use first participant (handle both list of strings and list of dicts)
                        first_participant = st.session_state.participants_data[0]
                        if isinstance(first_participant, dict):
                            first_name = first_participant['name']
                        else:
                            first_name = first_participant
                        
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_cert:
                            cert_path = tmp_cert.name
                        
                        if generator.generate_certificate(first_name, cert_path):
                            # Show preview
                            with open(cert_path, 'rb') as f:
                                cert_bytes = f.read()
                            
                            preview_image = convert_pdf_to_image(cert_bytes)
                            if preview_image:
                                st.image(preview_image, caption=f"Preview: {first_name}", use_container_width=True)
                            
                            # Download button for preview
                            st.download_button(
                                label="📥 Download Preview",
                                data=cert_bytes,
                                file_name=f"preview_{first_name}.pdf",
                                mime="application/pdf"
                            )
                        
                        # Cleanup
                        os.remove(template_path)
                        os.remove(cert_path)
                        
                    except Exception as e:
                        st.error(f"Error generating preview: {e}")
        
        with col2:
            st.write("**Generate All Certificates**")
            
            # Check if we have email data
            has_emails = isinstance(st.session_state.participants_data[0], dict) if st.session_state.participants_data else False
            
            st.info(f"📊 Ready to generate **{len(st.session_state.participants_data)}** certificates")
            
            if st.button("🚀 Generate All Certificates", type="primary"):
                with st.spinner("Generating all certificates..."):
                    try:
                        # Save template to temp file
                        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_template:
                            tmp_template.write(st.session_state.template_file.getvalue())
                            template_path = tmp_template.name
                        
                        # Get names list (extract from dicts if needed)
                        if has_emails:
                            names = [p['name'] for p in st.session_state.participants_data]
                        else:
                            names = st.session_state.participants_data
                        
                        # Generate all certificates
                        generator = CertificateGenerator(template_path, st.session_state.config)
                        zip_buffer = generate_certificates_zip(
                            generator,
                            names,
                            st.session_state.config
                        )
                        
                        # Cleanup temp template
                        os.remove(template_path)
                        
                        st.success(f"🎉 Successfully generated {len(names)} certificates!")
                        
                        # Download ZIP
                        st.download_button(
                            label="📦 Download All Certificates (ZIP)",
                            data=zip_buffer.getvalue(),
                            file_name="certificates.zip",
                            mime="application/zip",
                            type="primary"
                        )
                        
                    except Exception as e:
                        st.error(f"Error generating certificates: {e}")
                        st.exception(e)
        
        # Email sending section (only if emails are available)
        if st.session_state.send_emails_enabled and has_emails:
            st.divider()
            st.subheader("📧 Step 4: Send Certificates via Email")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("**Email Configuration**")
                
                # Load default config
                default_sender = "mgmcet.ieee@gmail.com"
                default_password = "phj hnn ozr oxr ivub"
                
                sender_email = st.text_input(
                    "Sender Email",
                    value=default_sender,
                    help="Your Gmail address"
                )
                
                sender_password = st.text_input(
                    "App Password",
                    value="",
                    type="password",
                    help="Gmail App Password (not your regular password)"
                )
                
                sender_name = st.text_input(
                    "Sender Name",
                    value="IEEE Student Branch MGMCET"
                )
                
                email_subject = st.text_input(
                    "Email Subject",
                    value="Your IEEE Event Participation Certificate"
                )
            
            with col2:
                st.write("**Email Template**")
                
                default_template = """Dear {name},

Greetings from IEEE Student Branch MGMCET!

Thank you for attending our event. We truly appreciate your participation.

Please find attached your Participation Certificate.

Best regards,
IEEE Student Branch MGMCET"""
                
                email_template = st.text_area(
                    "Email Message",
                    value=default_template,
                    height=200,
                    help="Use {name} as placeholder"
                )
            
            st.divider()
            
            if st.button("📨 Send All Certificates via Email", type="primary"):
                if not sender_email or not sender_password:
                    st.error("❌ Please provide email and password!")
                else:
                    with st.spinner("Sending emails..."):
                        try:
                            # Create temp directory
                            temp_cert_dir = tempfile.mkdtemp()
                            
                            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_template:
                                tmp_template.write(st.session_state.template_file.getvalue())
                                template_path = tmp_template.name
                            
                            # Generate certificates
                            generator = CertificateGenerator(template_path, st.session_state.config)
                            names = [p['name'] for p in st.session_state.participants_data]
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Generate all first
                            status_text.text("Generating certificates...")
                            for i, name in enumerate(names):
                                clean_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
                                filename = st.session_state.config.get('filename_template', '{name}_Certificate.pdf').format(name=clean_name)
                                cert_path = os.path.join(temp_cert_dir, filename)
                                generator.generate_certificate(name, cert_path)
                                progress_bar.progress((i + 1) / (len(names) * 2))
                            
                            # Send emails
                            email_config = {
                                'smtp_server': 'smtp.gmail.com',
                                'smtp_port': 587,
                                'sender_email': sender_email,
                                'sender_password': sender_password,
                                'sender_name': sender_name,
                                'email_subject': email_subject,
                                'email_template': email_template
                            }
                            
                            email_sender = EmailSender(email_config)
                            
                            status_text.text("Sending emails...")
                            successful, failed = email_sender.send_batch(
                                st.session_state.participants_data,
                                temp_cert_dir,
                                st.session_state.config.get('filename_template', '{name}_Certificate.pdf')
                            )
                            
                            progress_bar.progress(1.0)
                            
                            # Cleanup
                            os.remove(template_path)
                            shutil.rmtree(temp_cert_dir)
                            
                            # Results
                            if failed == 0:
                                st.success(f"🎉 Successfully sent {successful} emails!")
                            else:
                                st.warning(f"✅ Sent {successful} emails\n❌ Failed: {failed}")
                            
                            status_text.empty()
                            progress_bar.empty()
                            
                        except Exception as e:
                            st.error(f"Error: {e}")
                            st.exception(e)

        else:
            st.info("👆 Please upload both a template PDF and participants CSV to continue")

        # Footer
        st.divider()
        st.markdown("""
        <div style="text-align: center; color: #003D5C; padding: 2rem 0;">
            <p style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">⚡ IEEE Student Branch MGMCET</p>
            <p style="font-size: 0.95rem; color: #00629B; margin-bottom: 1rem;">Advancing Technology for Humanity</p>
            <p style="font-size: 0.85rem; color: #666;">Certificate Generator • Built with Streamlit</p>
            <p style="font-size: 0.8rem; color: #888; margin-top: 1rem;">Need help? Check the sidebar for configuration options</p>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        # View Responses tab
        view_responses_page()

