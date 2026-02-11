import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import sys

# Mock st.secrets for local testing if running as script
try:
    import toml
    secrets = toml.load(".streamlit/secrets.toml")
    st.secrets = secrets
except:
    pass

def test_connection():
    print("1. Testing Connection...")
    try:
        if "gsheets" not in st.secrets:
            print("❌ Secrets not found!")
            return None

        secret_dict = {
            "type": st.secrets["gsheets"]["type"],
            "project_id": st.secrets["gsheets"]["project_id"],
            "private_key_id": st.secrets["gsheets"]["private_key_id"],
            "private_key": st.secrets["gsheets"]["private_key"],
            "client_email": st.secrets["gsheets"]["client_email"],
            "client_id": st.secrets["gsheets"]["client_id"],
            "auth_uri": st.secrets["gsheets"]["auth_uri"],
            "token_uri": st.secrets["gsheets"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["gsheets"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["gsheets"]["client_x509_cert_url"]
        }
        
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        credentials = Credentials.from_service_account_info(secret_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        print("✅ Connection Successful!")
        return client
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return None

def test_master_sheet(client):
    print("\n2. Testing Master Sheet Access...")
    try:
        # Check if URL is configured
        if "sheet_url" not in st.secrets["gsheets"] or "YOUR_SHEET_ID" in st.secrets["gsheets"]["sheet_url"]:
            print("❌ 'sheet_url' is missing or set to placeholder in secrets.toml")
            print("   Please add your Google Sheet URL!")
            return

        sheet_url = st.secrets["gsheets"]["sheet_url"]
        print(f"   Opening sheet: {sheet_url}")
        
        try:
            sheet = client.open_by_url(sheet_url)
            print(f"   ✅ Successfully opened: '{sheet.title}'")
            print(f"   Tabs found: {[ws.title for ws in sheet.worksheets()]}")
            
            # Try adding a test tab
            try:
                test_title = "Connection_Test"
                if test_title not in [ws.title for ws in sheet.worksheets()]:
                    sheet.add_worksheet(title=test_title, rows=10, cols=10)
                    print(f"   ✅ Successfully added test tab '{test_title}'")
                    # Cleanup
                    ws = sheet.worksheet(test_title)
                    sheet.del_worksheet(ws)
                    print(f"   ✅ Successfully deleted test tab")
                else:
                    print(f"   ℹ️ Test tab '{test_title}' already exists")
            except Exception as e:
                 print(f"   ❌ Could not edit sheet: {e}")
                 print("   Are you sure you shared it with 'Editor' access?")

        except Exception as e:
             print(f"   ❌ Could not open sheet: {e}")
             print("   Make sure you shared the sheet with the client_email!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    client = test_connection()
    if client:
        test_master_sheet(client)
