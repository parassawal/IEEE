#!/usr/bin/env python3
"""
Main entry point for Certificate Generator
"""
import argparse
import json
import sys
import os
from pathlib import Path
import pandas as pd
from certificate_generator import CertificateGenerator
from email_sender import EmailSender


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file '{config_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def load_participants(file_path: str, include_emails: bool = False) -> list:
    """
    Load participant data from CSV or Excel file.
    
    Args:
        file_path: Path to participants file
        include_emails: If True, return list of dicts with name and email
    
    Expected format: Columns named 'Name' and 'Email' (case-insensitive).
    """
    file_ext = Path(file_path).suffix.lower()
    
    try:
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            print(f"Error: Unsupported file format '{file_ext}'. Use CSV or Excel.")
            sys.exit(1)
        
        # Find the name column (case-insensitive search)
        name_column = None
        email_column = None
        
        for col in df.columns:
            if 'name' in col.lower():
                name_column = col
            if 'email' in col.lower() or 'mail' in col.lower():
                email_column = col
        
        if name_column is None:
            print(f"Error: No 'Name' column found in {file_path}")
            print(f"Available columns: {', '.join(df.columns)}")
            sys.exit(1)
        
        if include_emails:
            if email_column is None:
                print(f"Error: No 'Email' column found in {file_path}")
                print(f"Available columns: {', '.join(df.columns)}")
                print("Hint: For email sending, your CSV must have both 'Name' and 'Email' columns.")
                sys.exit(1)
            
            # Return list of dicts with name and email
            participants = []
            for _, row in df.iterrows():
                name = str(row[name_column]) if pd.notna(row[name_column]) else None
                email = str(row[email_column]) if pd.notna(row[email_column]) else None
                if name and email:
                    participants.append({'name': name, 'email': email})
            
            if not participants:
                print("Error: No valid participant data found in the file.")
                sys.exit(1)
            
            return participants
        else:
            # Return list of names only
            names = df[name_column].dropna().astype(str).tolist()
            
            if not names:
                print("Error: No participant names found in the file.")
                sys.exit(1)
            
            return names
        
    except Exception as e:
        print(f"Error loading participants from {file_path}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Generate participation certificates with custom names',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --config config.json --participants participants.csv
  python main.py -c config.json -p participants.xlsx -o ./output
        """
    )
    
    parser.add_argument(
        '-c', '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    parser.add_argument(
        '-p', '--participants',
        required=True,
        help='Path to participants file (CSV or Excel)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output directory (overrides config file)'
    )
    
    parser.add_argument(
        '-t', '--template',
        help='Certificate template PDF path (overrides config file)'
    )
    
    parser.add_argument(
        '--send-email',
        action='store_true',
        help='Send certificates via email to participants'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    print(f"Loading configuration from {args.config}...")
    config = load_config(args.config)
    
    # Override with command line arguments
    if args.template:
        config['template_path'] = args.template
    if args.output:
        config['output_dir'] = args.output
    
    # Validate required config
    if 'template_path' not in config:
        print("Error: 'template_path' not specified in config or command line.")
        sys.exit(1)
    
    if not Path(config['template_path']).exists():
        print(f"Error: Template file '{config['template_path']}' not found.")
        sys.exit(1)
    
    output_dir = config.get('output_dir', './output')
    
    # Load participants
    print(f"Loading participants from {args.participants}...")
    if args.send_email:
        participants = load_participants(args.participants, include_emails=True)
        print(f"Found {len(participants)} participants with emails.")
        names = [p['name'] for p in participants]
    else:
        names = load_participants(args.participants, include_emails=False)
        print(f"Found {len(names)} participants.")
        participants = None
    
    # Initialize generator
    print(f"Initializing certificate generator with template: {config['template_path']}")
    generator = CertificateGenerator(config['template_path'], config)
    
    # Generate certificates
    print(f"\nGenerating certificates...")
    print("=" * 60)
    
    filename_template = config.get('filename_template', '{name}_certificate.pdf')
    successful, failed = generator.generate_batch(names, output_dir, filename_template)
    
    print("=" * 60)
    print(f"\n✓ Successfully generated: {successful}")
    if failed > 0:
        print(f"✗ Failed: {failed}")
    print(f"\nCertificates saved to: {Path(output_dir).absolute()}")
    
    # Send emails if requested
    if args.send_email:
        print(f"\n" + "=" * 60)
        print("Sending certificates via email...")
        print("=" * 60)
        
        # Load email config
        email_config = config.get('email', {})
        
        # Load email template if specified
        template_file = email_config.get('email_template_file')
        if template_file and os.path.exists(template_file):
            with open(template_file, 'r') as f:
                email_config['email_template'] = f.read()
        
        # Validate email config
        if not email_config.get('sender_email') or not email_config.get('sender_password'):
            print("\n❌ Error: Email credentials not configured!")
            print("Please update 'email.sender_email' and 'email.sender_password' in config.json")
            print("\nFor Gmail, use an App Password: https://support.google.com/accounts/answer/185833")
            sys.exit(1)
        
        # Initialize email sender
        email_sender = EmailSender(email_config)
        
        # Send emails
        email_successful, email_failed = email_sender.send_batch(
            participants, output_dir, filename_template
        )
        
        print("=" * 60)
        print(f"\n✓ Emails sent successfully: {email_successful}")
        if email_failed > 0:
            print(f"✗ Emails failed: {email_failed}")
        print(f"\n🎉 Process complete!")


if __name__ == '__main__':
    main()
