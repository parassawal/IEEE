#!/usr/bin/env python3
"""
Quick start script - Generates certificates with interactive prompts
"""
import os
import sys
import json
from pathlib import Path


def main():
    print("=" * 70)
    print("Certificate Generator - Quick Start")
    print("=" * 70)
    
    # Check if config exists
    if not os.path.exists('config.json'):
        print("❌ config.json not found!")
        sys.exit(1)
    
    # Load config
    with open('config.json') as f:
        config = json.load(f)
    
    print(f"\n📄 Template: {config.get('template_path', 'Not set')}")
    print(f"📁 Output: {config.get('output_dir', 'Not set')}")
    print(f"📍 Position: ({config.get('x_position', '?')}, {config.get('y_position', '?')})")
    print(f"🔤 Font: {config.get('font_name', '?')} - Size: {config.get('font_size', '?')}")
    
    # Get participant file
    print("\n" + "=" * 70)
    participant_file = input("Enter path to participants CSV/Excel file: ").strip()
    
    if not participant_file:
        print("❌ No file specified!")
        sys.exit(1)
    
    if not os.path.exists(participant_file):
        print(f"❌ File not found: {participant_file}")
        sys.exit(1)
    
    # Confirm
    print("\n" + "=" * 70)
    confirm = input("Generate certificates? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("❌ Cancelled")
        sys.exit(0)
    
    # Run the generator
    print("\n" + "=" * 70)
    os.system(f'./venv/bin/python main.py --participants "{participant_file}"')


if __name__ == '__main__':
    main()
