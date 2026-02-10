"""
Certificate Generator - Overlay participant names on PDF certificates
"""
import os
from pathlib import Path
from typing import List, Tuple
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from io import BytesIO


class CertificateGenerator:
    """Generate personalized certificates by overlaying names on a PDF template."""
    
    def __init__(self, template_path: str, config: dict):
        """
        Initialize the certificate generator.
        
        Args:
            template_path: Path to the PDF certificate template
            config: Configuration dictionary with positioning and styling
        """
        self.template_path = template_path
        self.config = config
        self.template = PdfReader(template_path)
        
        # Get template dimensions
        page = self.template.pages[0]
        self.page_width = float(page.mediabox.width)
        self.page_height = float(page.mediabox.height)
        
    def create_text_overlay(self, text: str) -> BytesIO:
        """
        Create a transparent PDF with just the text overlay.
        
        Args:
            text: The text to overlay (participant name)
            
        Returns:
            BytesIO object containing the overlay PDF
        """
        packet = BytesIO()
        
        # Create canvas with same dimensions as template
        can = canvas.Canvas(packet, pagesize=(self.page_width, self.page_height))
        
        # Set font
        font_name = self.config.get('font_name', 'Helvetica-Bold')
        font_size = self.config.get('font_size', 36)
        
        # Try to use custom font if specified
        custom_font_path = self.config.get('custom_font_path')
        if custom_font_path and os.path.exists(custom_font_path):
            try:
                pdfmetrics.registerFont(TTFont('CustomFont', custom_font_path))
                font_name = 'CustomFont'
            except Exception as e:
                print(f"Warning: Could not load custom font. Using {font_name}. Error: {e}")
        
        can.setFont(font_name, font_size)
        
        # Set color
        color = self.config.get('font_color', '#000000')
        can.setFillColor(HexColor(color))
        
        # Get position
        x = self.config.get('x_position', self.page_width / 2)
        y = self.config.get('y_position', self.page_height / 2)
        
        # Get alignment
        alignment = self.config.get('alignment', 'center')
        
        # Draw text based on alignment
        if alignment == 'center':
            can.drawCentredString(x, y, text)
        elif alignment == 'right':
            can.drawRightString(x, y, text)
        else:  # left
            can.drawString(x, y, text)
        
        can.save()
        packet.seek(0)
        return packet
    
    def generate_certificate(self, name: str, output_path: str) -> bool:
        """
        Generate a certificate for a single participant.
        
        Args:
            name: Participant's name
            output_path: Where to save the generated certificate
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create text overlay
            overlay_pdf = self.create_text_overlay(name)
            overlay = PdfReader(overlay_pdf)
            
            # Create output PDF
            output = PdfWriter()
            
            # Read a fresh copy of the template page (important: don't reuse the same page object!)
            # This prevents names from accumulating on subsequent certificates
            template = PdfReader(self.template_path)
            page = template.pages[0]
            
            # Merge overlay onto template
            page.merge_page(overlay.pages[0])
            output.add_page(page)
            
            # Write to file
            with open(output_path, 'wb') as output_file:
                output.write(output_file)
            
            return True
            
        except Exception as e:
            print(f"Error generating certificate for {name}: {e}")
            return False
    
    def generate_batch(self, names: List[str], output_dir: str, 
                       filename_template: str = "{name}_certificate.pdf") -> Tuple[int, int]:
        """
        Generate certificates for multiple participants.
        
        Args:
            names: List of participant names
            output_dir: Directory to save certificates
            filename_template: Template for output filenames (use {name} placeholder)
            
        Returns:
            Tuple of (successful_count, failed_count)
        """
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        successful = 0
        failed = 0
        
        for i, name in enumerate(names, 1):
            # Clean name for filename
            clean_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
            filename = filename_template.format(name=clean_name, index=i)
            output_path = os.path.join(output_dir, filename)
            
            print(f"Generating certificate {i}/{len(names)}: {name}")
            
            if self.generate_certificate(name, output_path):
                successful += 1
                print(f"  ✓ Saved to {output_path}")
            else:
                failed += 1
                print(f"  ✗ Failed")
        
        return successful, failed


def sanitize_filename(name: str) -> str:
    """Convert a name into a safe filename."""
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name).strip()
