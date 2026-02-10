#!/usr/bin/env python3
"""
Position Helper - Interactive tool to find the right coordinates for your certificate
"""
import sys
from pypdf import PdfReader
import json


def analyze_pdf(pdf_path: str):
    """Analyze PDF and display helpful information about positioning."""
    try:
        reader = PdfReader(pdf_path)
        page = reader.pages[0]
        
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        
        print("=" * 70)
        print("Certificate Template Analysis")
        print("=" * 70)
        print(f"\nPDF Dimensions:")
        print(f"  Width:  {width:.2f} points")
        print(f"  Height: {height:.2f} points")
        
        print(f"\nCommon Position Reference Points:")
        print(f"  Top-Left Corner:     ({0:.2f}, {height:.2f})")
        print(f"  Top-Center:          ({width/2:.2f}, {height:.2f})")
        print(f"  Top-Right Corner:    ({width:.2f}, {height:.2f})")
        print(f"  Center-Left:         ({0:.2f}, {height/2:.2f})")
        print(f"  Center:              ({width/2:.2f}, {height/2:.2f})")
        print(f"  Center-Right:        ({width:.2f}, {height/2:.2f})")
        print(f"  Bottom-Left Corner:  ({0:.2f}, {0:.2f})")
        print(f"  Bottom-Center:       ({width/2:.2f}, {0:.2f})")
        print(f"  Bottom-Right Corner: ({width:.2f}, {0:.2f})")
        
        print(f"\n📝 Tips for Finding the Right Position:")
        print(f"  • PDF coordinates start from BOTTOM-LEFT corner (0, 0)")
        print(f"  • Y increases as you go UP the page")
        print(f"  • For centered text, use x_position: {width/2:.2f}")
        print(f"  • For middle of page, try y_position: {height/2:.2f}")
        print(f"  • Typical name position: y between {height*0.4:.0f} and {height*0.6:.0f}")
        
        print(f"\n🔧 Suggested Starting Values for config.json:")
        suggestion = {
            "x_position": round(width / 2),
            "y_position": round(height * 0.45),  # Slightly below center
            "alignment": "center"
        }
        print(json.dumps(suggestion, indent=2))
        
        print(f"\n💡 How to Adjust:")
        print(f"  • Name too high? DECREASE y_position")
        print(f"  • Name too low? INCREASE y_position")
        print(f"  • Name too left? INCREASE x_position")
        print(f"  • Name too right? DECREASE x_position")
        print("=" * 70)
        
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python position_helper.py <certificate_template.pdf>")
        sys.exit(1)
    
    analyze_pdf(sys.argv[1])
