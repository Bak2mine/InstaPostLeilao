"""
Template Filler - Fill PNG templates with property data and convert to PDF
"""

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from pypdf import PdfReader, PdfWriter
import re

class TemplateFiller:
    # Estimated coordinates based on visual template (1414x2000px)
    COORDINATES = {
        'tipo1': {  # 2 praças + desconto
            'titulo': (150, 620, 1264, 42),  # x, y, max_width, font_size
            'cidade_estado': (200, 710, 1200, 32),
            'discount': (400, 530, 600, 36),
            'praca1_valor': (280, 1050, 500, 40),
            'praca2_valor': (900, 1050, 500, 40),
            'praca1_data': (220, 1160, 400, 24),
            'praca2_data': (850, 1160, 400, 24),
            'praca1_hora': (300, 1260, 350, 24),
            'praca2_hora': (950, 1260, 350, 24),
        }
    }

    def __init__(self, template_png_path, link_pdf_path=None):
        self.template_png_path = template_png_path
        self.link_pdf_path = link_pdf_path
        self.try_load_fonts()

    def try_load_fonts(self):
        """Load system fonts, fallback to default"""
        try:
            self.font_large = ImageFont.truetype("arial.ttf", 50)
            self.font_medium = ImageFont.truetype("arial.ttf", 38)
            self.font_small = ImageFont.truetype("arial.ttf", 28)
        except:
            try:
                self.font_large = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 50)
                self.font_medium = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 38)
                self.font_small = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 28)
            except:
                self.font_large = self.font_medium = self.font_small = ImageFont.load_default()

    def fill_template(self, property_data, output_png_path):
        """Fill PNG template with property data"""
        print(f"  Loading template: {self.template_png_path}")
        img = Image.open(self.template_png_path).convert('RGB')
        draw = ImageDraw.Draw(img)

        coords = self.COORDINATES['tipo1']

        # Title
        if property_data.get('titulo'):
            x, y, mw, fs = coords['titulo']
            title = property_data['titulo'][:50]
            draw.text((x, y), title, fill=(0, 150, 200), font=self.font_large)
            print(f"    Title: {title}")

        # Location
        if property_data.get('cidade') and property_data.get('estado'):
            x, y, mw, fs = coords['cidade_estado']
            loc = f"{property_data['cidade']}/{property_data['estado']}"
            draw.text((x, y), loc, fill=(0, 150, 200), font=self.font_medium)
            print(f"    Location: {loc}")

        # Discount
        if property_data.get('desconto_pct'):
            x, y, mw, fs = coords['discount']
            disc_text = f"{int(property_data['desconto_pct'])}% DE DESCONTO!"
            draw.text((x, y), disc_text, fill=(255, 255, 255), font=self.font_medium)
            print(f"    Discount: {disc_text}")

        # Price 1
        if property_data.get('praca1_valor'):
            x, y, mw, fs = coords['praca1_valor']
            draw.text((x, y), property_data['praca1_valor'], fill=(255, 255, 255), font=self.font_medium)
            print(f"    Price 1: {property_data['praca1_valor']}")

        # Price 2
        if property_data.get('praca2_valor'):
            x, y, mw, fs = coords['praca2_valor']
            draw.text((x, y), property_data['praca2_valor'], fill=(255, 255, 255), font=self.font_medium)
            print(f"    Price 2: {property_data['praca2_valor']}")

        # Date 1
        if property_data.get('praca1_data'):
            x, y, mw, fs = coords['praca1_data']
            draw.text((x, y), property_data['praca1_data'], fill=(255, 255, 255), font=self.font_small)

        # Date 2
        if property_data.get('praca2_data'):
            x, y, mw, fs = coords['praca2_data']
            draw.text((x, y), property_data['praca2_data'], fill=(255, 255, 255), font=self.font_small)

        # Save filled PNG
        img.save(output_png_path)
        print(f"    Saved PNG: {output_png_path}")
        return output_png_path

    def png_to_pdf(self, png_path, pdf_path):
        """Convert PNG to PDF"""
        print(f"  Converting PNG to PDF...")
        img = Image.open(png_path).convert('RGB')

        # Scale to A4 if needed (595x842 points)
        img.save(pdf_path, 'PDF')
        print(f"    Saved PDF: {pdf_path}")
        return pdf_path

    def add_link_page(self, pdf_path):
        """Append link page from template PDF"""
        if not self.link_pdf_path:
            print("    No link PDF provided, skipping link page")
            return pdf_path

        try:
            print(f"  Appending link page...")
            reader = PdfReader(self.link_pdf_path)
            link_page = reader.pages[-1]

            # Read generated PDF and append link
            pdf_reader = PdfReader(pdf_path)
            writer = PdfWriter()

            # Add filled template page
            writer.add_page(pdf_reader.pages[0])

            # Add link page
            writer.add_page(link_page)

            # Save final PDF
            with open(pdf_path, 'wb') as f:
                writer.write(f)

            print(f"    Final PDF (2 pages): {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"    Warning: Could not add link page: {e}")
            return pdf_path


# Example usage
if __name__ == "__main__":
    # Property data extracted from HTML
    property_data = {
        'titulo': 'Casa 147m² – Uberlândia/MG',
        'cidade': 'Uberlândia',
        'estado': 'MG',
        'praca1_valor': 'R$ 320.418,61',
        'praca2_valor': 'R$ 320.418,61',
        'praca1_data': '15/06/2026',
        'praca2_data': '29/06/2026',
        'praca1_hora': '14:00',
        'praca2_hora': '14:00',
        'desconto_pct': 36.0,
    }

    # Initialize filler
    filler = TemplateFiller(
        template_png_path='C:\\Users\\andre\\Desktop\\Leiloaria\\Post\\praca2desconto.png',
        link_pdf_path='C:\\Users\\andre\\Desktop\\Leiloaria\\Post\\Posts IG.pdf'
    )

    # Fill template
    output_png = 'C:\\Users\\Andre\\Desktop\\Leiloaria\\Post\\imoveis\\test_filled.png'
    output_pdf = 'C:\\Users\\Andre\\Desktop\\Leiloaria\\Post\\imoveis\\Casa 147m - Uberlandia-MG.pdf'

    print("[*] Filling template...")
    filler.fill_template(property_data, output_png)

    print("[*] Converting to PDF...")
    filler.png_to_pdf(output_png, output_pdf.replace('.pdf', '_temp.pdf'))

    print("[*] Adding link page...")
    filler.add_link_page(output_pdf.replace('.pdf', '_temp.pdf'))

    print("\n[OK] Complete!")
