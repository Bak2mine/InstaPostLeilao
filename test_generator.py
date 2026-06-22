"""
Test Generator - Create PDF with exact template data for comparison
"""

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from pathlib import Path

class TestTemplateFiller:
    """Test filler with same logic as main generator"""

    def __init__(self, template_dir, link_pdf_path):
        self.template_dir = template_dir
        self.link_pdf_path = link_pdf_path
        self.try_load_fonts()
        self.calculate_coordinates()

    def try_load_fonts(self):
        """Load system fonts"""
        font_variants = [
            ("C:\\Windows\\Fonts\\montserrat-black.ttf", "C:\\Windows\\Fonts\\montserrat-bold.ttf", "C:\\Windows\\Fonts\\montserrat.ttf"),
            ("C:\\Windows\\Fonts\\Montserrat-Black.ttf", "C:\\Windows\\Fonts\\Montserrat-Bold.ttf", "C:\\Windows\\Fonts\\Montserrat-Regular.ttf"),
            ("C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\arial.ttf"),
            ("arialbd.ttf", "arialbd.ttf", "arial.ttf"),
        ]

        loaded = False
        for extra_bold_large, bold_medium, regular_small in font_variants:
            try:
                self.font_large = ImageFont.truetype(extra_bold_large, 52)
                self.font_medium = ImageFont.truetype(bold_medium, 52)
                self.font_small = ImageFont.truetype(regular_small, 28)
                loaded = True
                break
            except:
                continue

        if not loaded:
            self.font_large = self.font_medium = self.font_small = ImageFont.load_default()

    def calculate_coordinates(self):
        """Calculate coordinates"""
        template_file = f"{self.template_dir}/praca2desconto.png"
        img = Image.open(template_file)
        width, height = img.size

        center_x = width / 2
        third_x_left = width / 3
        third_x_right = 2 * width / 3

        self.COORDINATES = {
            'praca2desconto': {
                'titulo': (center_x, int(height * 0.31) + 345, int(width * 0.9), 42),
                'cidade_estado': (center_x, int(height * 0.355) + 345, int(width * 0.85), 32),
                'discount': (center_x, int(height * 0.265) + 200, int(width * 0.42), 36),
                'praca1_valor': (third_x_left, int(height * 0.525) + 50, int(width * 0.3), 40),
                'praca2_valor': (third_x_right, int(height * 0.525) + 50, int(width * 0.3), 40),
                'praca1_data': (third_x_left, int(height * 0.58) + 50, int(width * 0.28), 24),
                'praca2_data': (third_x_right, int(height * 0.58) + 50, int(width * 0.28), 24),
            }
        }

    def _draw_centered_text(self, draw, text, x, y, font, fill=(0, 0, 0), stroke_width=0):
        """Draw centered text with optional minimal stroke (corners only)"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        centered_x = x - (text_width / 2)

        if stroke_width > 0:
            # Draw stroke only in 4 corners for minimal girth effect
            corners = [(-stroke_width, -stroke_width), (stroke_width, -stroke_width),
                      (-stroke_width, stroke_width), (stroke_width, stroke_width)]
            for adj_x, adj_y in corners:
                draw.text((centered_x + adj_x, y + adj_y), text, fill=fill, font=font)

        draw.text((centered_x, y), text, fill=fill, font=font)

    def _draw_thirds_text(self, draw, text, third_x, y, font, fill=(0, 0, 0)):
        """Draw text centered within thirds"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        centered_x = third_x - (text_width / 2)
        draw.text((centered_x, y), text, fill=fill, font=font)

    def fill_template(self, property_data, output_png_path):
        """Fill template with data"""
        template_file = f"{self.template_dir}/praca2desconto.png"
        img = Image.open(template_file).convert('RGB')
        draw = ImageDraw.Draw(img)
        coords = self.COORDINATES['praca2desconto']

        # Title with minimal stroke for two-layer effect
        if property_data.get('titulo'):
            x, y, mw, fs = coords['titulo']
            self._draw_centered_text(draw, property_data['titulo'], x, y,
                                     self.font_large, fill=(0, 194, 255), stroke_width=1)

        # Location
        if property_data.get('cidade') and property_data.get('estado'):
            x, y, mw, fs = coords['cidade_estado']
            loc = f"{property_data['cidade']}/{property_data['estado']}"
            self._draw_centered_text(draw, loc, x, y, self.font_medium, fill=(0, 194, 255))

        # Discount
        if property_data.get('desconto_pct'):
            x, y, mw, fs = coords['discount']
            disc_text = f"{property_data['desconto_pct']}% DE DESCONTO!"
            self._draw_centered_text(draw, disc_text, x, y, self.font_medium, fill=(255, 255, 255))

        # Prices
        if property_data.get('praca1_valor'):
            x, y, mw, fs = coords['praca1_valor']
            self._draw_thirds_text(draw, property_data['praca1_valor'], x, y,
                                   self.font_medium, fill=(255, 255, 255))

        if property_data.get('praca2_valor'):
            x, y, mw, fs = coords['praca2_valor']
            self._draw_thirds_text(draw, property_data['praca2_valor'], x, y,
                                   self.font_medium, fill=(255, 255, 255))

        # Dates
        if property_data.get('praca1_data'):
            x, y, mw, fs = coords['praca1_data']
            self._draw_thirds_text(draw, property_data['praca1_data'], x, y,
                                   self.font_small, fill=(255, 255, 255))

        if property_data.get('praca2_data'):
            x, y, mw, fs = coords['praca2_data']
            self._draw_thirds_text(draw, property_data['praca2_data'], x, y,
                                   self.font_small, fill=(255, 255, 255))

        img.save(output_png_path)
        return output_png_path

    def png_to_pdf(self, png_path, pdf_path):
        """Convert PNG to high-quality PDF"""
        img = Image.open(png_path).convert('RGB')
        img.save(pdf_path, 'PDF', quality=95, dpi=(300, 300))
        return pdf_path

    def add_link_page(self, pdf_path):
        """Append link page"""
        try:
            reader = PdfReader(self.link_pdf_path)
            link_page = reader.pages[-1]

            pdf_reader = PdfReader(pdf_path)
            writer = PdfWriter()

            writer.add_page(pdf_reader.pages[0])
            writer.add_page(link_page)

            with open(pdf_path, 'wb') as f:
                writer.write(f)

            return pdf_path
        except Exception as e:
            print(f"[WARN] Could not add link page: {e}")
            return pdf_path


def main():
    print("=" * 60)
    print("Test Generator - Exact Template Data")
    print("=" * 60)

    post_dir = Path("C:\\Users\\andre\\Desktop\\Leiloaria\\Post")
    output_dir = post_dir / "test_output"
    output_dir.mkdir(exist_ok=True)

    # Exact data from your original image
    test_data = {
        'titulo': 'Lote de Terreno 300m²',
        'cidade': 'NOVA ODESSA',
        'estado': 'SP',
        'praca1_valor': 'R$ 255.056,73',
        'praca2_valor': 'R$ 245.848,12',
        'praca1_data': '15/06/2026',
        'praca2_data': '30/06/2026',
        'praca1_hora': '14:00hs',
        'praca2_hora': '14:00hs',
        'desconto_pct': '20',
        'segunda_praca': True,
        'tipo': 'praca2desconto',
    }

    print("\n[*] Filling template with test data...")
    print(f"    Title: {test_data['titulo']}")
    print(f"    Location: {test_data['cidade']}/{test_data['estado']}")
    print(f"    Discount: {test_data['desconto_pct']}%")
    print(f"    Prices: {test_data['praca1_valor']} / {test_data['praca2_valor']}")

    filler = TestTemplateFiller(str(post_dir), str(post_dir / "Posts IG.pdf"))

    png_path = output_dir / "test_filled.png"
    pdf_path = output_dir / "TEST_ORIGINAL.pdf"

    filler.fill_template(test_data, str(png_path))
    filler.png_to_pdf(str(png_path), str(pdf_path))
    filler.add_link_page(str(pdf_path))

    # Cleanup PNG
    png_path.unlink(missing_ok=True)

    print("\n[OK] Test PDF created!")
    print(f"Saved to: {pdf_path}")
    print("\nNow compare this with your generated PDFs to check alignment!")


if __name__ == "__main__":
    main()
