"""
Complete PDF Generator for Leiloaria Properties
Scrapes website → Extracts data → Fills templates → Generates PDFs
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
import os
import re
import time
from pathlib import Path

BASE_URL = "https://leiloariasmart.com.br"
MAIN_URL = "https://leiloariasmart.com.br/busca"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
TIMEOUT = 30

class PropertyScraper:
    """Scrapes and extracts property data from leiloariasmart.com.br"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def get_all_auctions(self):
        """Get all auctions from search page"""
        try:
            response = self.session.get(MAIN_URL, timeout=TIMEOUT)
            soup = BeautifulSoup(response.text, 'html.parser')
            auctions = []
            for card in soup.find_all('div', class_='caixa-imoveis'):
                title_tag = card.find('div', class_='info-imovel-2')
                if not title_tag:
                    continue
                link_tag = title_tag.find('a', href=True)
                if not link_tag:
                    continue
                title = link_tag.text.strip()
                url = urljoin(BASE_URL, link_tag['href'])
                auctions.append({'title': title, 'url': url})
            print(f"[OK] Found {len(auctions)} properties")
            return auctions
        except Exception as e:
            print(f"[ERROR] Error fetching auctions: {e}")
            return []

    def get_property_data(self, auction_url, auction_title):
        """Extract all relevant data from property page"""
        try:
            response = self.session.get(auction_url, timeout=TIMEOUT)
            response.encoding = 'utf-8'
            html_text = response.text

            # Extract location from auction title: "Casa 147m² – Uberlândia/MG"
            # Try em-dash and hyphen variations
            loc_match = re.search(r'[–-]\s*([^/\n]+)/([A-Z]{2})', auction_title)
            if loc_match:
                cidade = loc_match.group(1).strip()
                estado = loc_match.group(2).strip()
                # Remove state from title for display
                titulo_clean = re.sub(r'\s*[–-].*$', '', auction_title).strip()
            else:
                # Try to extract from anywhere in the title
                loc_match = re.search(r'([A-Z][a-záàâãéèêíïóôõöúçñ\s]+)/([A-Z]{2})', auction_title)
                if loc_match:
                    cidade = loc_match.group(1).strip()
                    estado = loc_match.group(2).strip()
                    titulo_clean = re.sub(r'\s*[–-].*$', '', auction_title).strip()
                else:
                    cidade = None
                    estado = None
                    titulo_clean = auction_title

            data = {
                'titulo': titulo_clean,  # Title without state
                'cidade': cidade,
                'estado': estado,
                'praca1_valor': None,
                'praca2_valor': None,
                'praca1_data': None,
                'praca2_data': None,
                'praca1_hora': None,
                'praca2_hora': None,
                'desconto_pct': None,
                'segunda_praca': False,
                'tipo': None,
            }

            # Extract discount percentage
            desconto_match = re.search(r'Desconto:\s*aproximadamente\s*([\d.,]+)%', html_text)
            if desconto_match:
                pct_str = desconto_match.group(1).replace(',', '.')
                try:
                    data['desconto_pct'] = float(pct_str)
                except ValueError:
                    pass

            # Extract Primeira praça OR Praça Única - more flexible pattern
            primeira_pattern = r'(?:Primeira\s+pra[çc]a|Pra[çc]a\s+[ÚU]nica):.*?(?=Segunda\s+pra[çc]a:|Desconto:|$)'
            primeira_section = re.search(primeira_pattern, html_text, re.IGNORECASE | re.DOTALL)

            if primeira_section:
                seção = primeira_section.group(0)
                # Get all prices and dates in this section
                prices = re.findall(r'R\$\s*([\d.,]+)', seção)
                dates = re.findall(r'(\d{2})/(\d{2})/(\d{4})\s+às\s+(\d{2}):(\d{2})', seção)

                # Use first price (after any "Último lance" or header info)
                if prices:
                    # Skip if all prices are 0 or very small (likely Ultimo lance)
                    for price in prices:
                        price_float = float(price.replace('.', '').replace(',', '.'))
                        if price_float > 1000:  # Only take prices > 1000
                            data['praca1_valor'] = f"R$ {price}"
                            break
                    if not data['praca1_valor'] and prices:  # If no price > 1000, take first
                        data['praca1_valor'] = f"R$ {prices[-1]}"

                if dates:
                    d = dates[0]
                    data['praca1_data'] = f"{d[0]}/{d[1]}/{d[2]}"
                    data['praca1_hora'] = f"{d[3]}:{d[4]}"

            # Extract Segunda praça
            segunda_pattern = r'Segunda\s+pra[çc]a:.*?(?=Desconto:|Abaixo Avaliado|$)'
            segunda_section = re.search(segunda_pattern, html_text, re.IGNORECASE | re.DOTALL)

            if segunda_section:
                seção = segunda_section.group(0)
                prices = re.findall(r'R\$\s*([\d.,]+)', seção)
                dates = re.findall(r'(\d{2})/(\d{2})/(\d{4})\s+às\s+(\d{2}):(\d{2})', seção)

                if prices:
                    data['praca2_valor'] = f"R$ {prices[-1]}"  # Take last price
                    data['segunda_praca'] = True

                if dates:
                    d = dates[0]
                    data['praca2_data'] = f"{d[0]}/{d[1]}/{d[2]}"
                    data['praca2_hora'] = f"{d[3]}:{d[4]}"

            # Determine template type
            has_segunda = data['segunda_praca']
            has_desconto = data['desconto_pct'] is not None

            if has_segunda and has_desconto:
                data['tipo'] = 'praca2desconto'
            elif not has_segunda and has_desconto:
                data['tipo'] = 'praca1desconto'
            elif has_segunda and not has_desconto:
                data['tipo'] = 'praca2'
            else:
                data['tipo'] = 'praca1'

            return data
        except Exception as e:
            print(f"[ERROR] Error extracting data: {e}")
            return None


class TemplateFiller:
    """Fills PNG templates with property data and creates PDFs"""

    def __init__(self, template_dir, link_pdf_path):
        self.template_dir = template_dir
        self.link_pdf_path = link_pdf_path
        self.try_load_fonts()
        self.calculate_coordinates()

    def calculate_coordinates(self):
        """Calculate coordinates dynamically based on template dimensions"""
        # Load template to get dimensions
        template_file = f"{self.template_dir}/praca2desconto.png"
        img = Image.open(template_file)
        width, height = img.size

        # Center positions (x = width/2)
        center_x = width / 2

        # Third positions (for dual items on left/right)
        third_x_left = width / 3
        third_x_right = 2 * width / 3

        # Vertical positions (percentages of height + pixel offsets)
        self.COORDINATES = {
            'praca2desconto': {
                'titulo': (center_x, int(height * 0.31) + 345, int(width * 0.9), 42),       # -500px up
                'cidade_estado': (center_x, int(height * 0.355) + 345, int(width * 0.85), 32),  # -500px up
                'discount': (center_x, int(height * 0.265) - 200, int(width * 0.42), 36),   # -200px up
                'praca1_valor': (third_x_left, int(height * 0.525) + 50, int(width * 0.3), 40),   # +150px down (net adjustment)
                'praca2_valor': (third_x_right, int(height * 0.525) + 50, int(width * 0.3), 40),  # +150px down (net adjustment)
                'praca1_data': (third_x_left, int(height * 0.58) + 50, int(width * 0.28), 24),    # +150px down (net adjustment)
                'praca2_data': (third_x_right, int(height * 0.58) + 50, int(width * 0.28), 24),   # +150px down (net adjustment)
            }
        }

    def try_load_fonts(self):
        """Load system fonts - Extra Bold for title, Bold for text, Regular for dates"""
        # Try to load fonts in order of preference
        font_variants = [
            # Montserrat variants (extra bold/black for title, bold for medium, regular for small)
            ("C:\\Windows\\Fonts\\montserrat-black.ttf", "C:\\Windows\\Fonts\\montserrat-bold.ttf", "C:\\Windows\\Fonts\\montserrat.ttf"),
            ("C:\\Windows\\Fonts\\Montserrat-Black.ttf", "C:\\Windows\\Fonts\\Montserrat-Bold.ttf", "C:\\Windows\\Fonts\\Montserrat-Regular.ttf"),
            ("C:\\Windows\\Fonts\\montserrat-extrabold.ttf", "C:\\Windows\\Fonts\\montserrat-bold.ttf", "C:\\Windows\\Fonts\\montserrat.ttf"),
            ("C:\\Windows\\Fonts\\Montserrat-ExtraBold.ttf", "C:\\Windows\\Fonts\\Montserrat-Bold.ttf", "C:\\Windows\\Fonts\\Montserrat-Regular.ttf"),
            ("montserrat-black.ttf", "montserrat-bold.ttf", "montserrat.ttf"),
            # Arial fallback (bold for title, bold for medium, regular for small)
            ("C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\arial.ttf"),
            ("arialbd.ttf", "arialbd.ttf", "arial.ttf"),
        ]

        loaded = False
        for extra_bold_large, bold_medium, regular_small in font_variants:
            try:
                self.font_large = ImageFont.truetype(extra_bold_large, 52)   # Extra Bold/Black for title
                self.font_medium = ImageFont.truetype(bold_medium, 38)       # Bold for location/prices/discount
                self.font_small = ImageFont.truetype(regular_small, 28)      # Regular for dates
                loaded = True
                break
            except:
                continue

        if not loaded:
            self.font_large = self.font_medium = self.font_small = ImageFont.load_default()

    def _draw_centered_text(self, draw, text, x, y, font, fill=(0, 0, 0), stroke_width=0):
        """Draw text centered horizontally at position (x, y) with optional minimal stroke"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        centered_x = x - (text_width / 2)

        # Draw stroke only in 4 corners for minimal girth effect
        if stroke_width > 0:
            corners = [(-stroke_width, -stroke_width), (stroke_width, -stroke_width),
                      (-stroke_width, stroke_width), (stroke_width, stroke_width)]
            for adj_x, adj_y in corners:
                draw.text((centered_x + adj_x, y + adj_y), text, fill=fill, font=font)

        # Draw main text on top
        draw.text((centered_x, y), text, fill=fill, font=font)

    def _draw_thirds_text(self, draw, text, third_x, y, font, fill=(0, 0, 0)):
        """Draw text centered within a third (left/right section)"""
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        centered_x = third_x - (text_width / 2)
        draw.text((centered_x, y), text, fill=fill, font=font)

    def fill_template(self, property_data, output_png_path):
        """Fill PNG template with property data"""
        template_type = property_data['tipo']
        template_file = f"{self.template_dir}/praca2desconto.png"

        img = Image.open(template_file).convert('RGB')
        draw = ImageDraw.Draw(img)
        coords = self.COORDINATES['praca2desconto']

        # Title (centered) - #00C2FF cyan with minimal stroke for depth
        if property_data.get('titulo'):
            x, y, mw, fs = coords['titulo']
            self._draw_centered_text(draw, property_data['titulo'][:50], x, y,
                                     self.font_large, fill=(0, 194, 255), stroke_width=1)

        # Location (centered) - #00C2FF cyan color
        if property_data.get('cidade') and property_data.get('estado'):
            x, y, mw, fs = coords['cidade_estado']
            loc = f"{property_data['cidade']}/{property_data['estado']}"
            self._draw_centered_text(draw, loc, x, y, self.font_medium, fill=(0, 194, 255))

        # Discount (centered)
        if property_data.get('desconto_pct'):
            x, y, mw, fs = coords['discount']
            disc_text = f"{int(property_data['desconto_pct'])}% DE DESCONTO!"
            self._draw_centered_text(draw, disc_text, x, y, self.font_medium, fill=(255, 255, 255))

        # Prices (left/right thirds)
        if property_data.get('praca1_valor'):
            x, y, mw, fs = coords['praca1_valor']
            self._draw_thirds_text(draw, property_data['praca1_valor'], x, y,
                                   self.font_medium, fill=(255, 255, 255))

        if property_data.get('praca2_valor'):
            x, y, mw, fs = coords['praca2_valor']
            self._draw_thirds_text(draw, property_data['praca2_valor'], x, y,
                                   self.font_medium, fill=(255, 255, 255))

        # Dates (left/right thirds)
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
        """Convert PNG to PDF at high quality - preserve original resolution"""
        img = Image.open(png_path).convert('RGB')

        # Save at high quality without downscaling
        # Use 300 DPI quality for crisp output
        img.save(pdf_path, 'PDF', quality=95, dpi=(300, 300))
        return pdf_path

    def add_link_page(self, pdf_path):
        """Append link page from template PDF"""
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
    print("Leilao PDF Generator - Complete")
    print("=" * 60)

    post_dir = Path("C:\\Users\\andre\\Desktop\\Leiloaria\\Post")
    imoveis_dir = post_dir / "imoveis"
    imoveis_dir.mkdir(exist_ok=True)

    print("\n[1/3] Scraping properties...")
    scraper = PropertyScraper()
    auctions = scraper.get_all_auctions()

    if not auctions:
        print("[ERROR] No properties found")
        return

    print("\n[2/3] Generating PDFs...")
    filler = TemplateFiller(str(post_dir), str(post_dir / "Posts IG.pdf"))

    success_count = 0
    for i, auction in enumerate(auctions, 1):
        # Test with first 3
        if i > 3:
            break
        print(f"\n[{i}/3] {auction['title']}")

        property_data = scraper.get_property_data(auction['url'], auction['title'])
        if not property_data:
            print("  Skipped (no data)")
            continue

        # Validate required fields
        required_fields = ['titulo', 'cidade', 'estado', 'praca1_valor', 'praca1_data']
        missing = [f for f in required_fields if not property_data.get(f)]

        if missing:
            print(f"  Skipped (missing: {', '.join(missing)})")
            continue

        # Sanitize filename - remove state (everything after em-dash)
        title_for_file = re.sub(r'\s*[–-].*$', '', auction['title']).strip()  # Remove em-dash and after, trim spaces
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title_for_file).replace('/', ' - ').strip()

        # Generate PDFs
        png_path = imoveis_dir / f"{safe_title}_temp.png"
        pdf_path = imoveis_dir / f"{safe_title}.pdf"

        try:
            temp_pdf = imoveis_dir / f"{safe_title}_temp.pdf"
            filler.fill_template(property_data, str(png_path))
            filler.png_to_pdf(str(png_path), str(temp_pdf))
            filler.add_link_page(str(temp_pdf))

            # Rename final PDF
            import shutil
            shutil.move(str(temp_pdf), str(pdf_path))

            # Cleanup PNG
            png_path.unlink(missing_ok=True)

            success_count += 1
            print(f"  [OK] Generated PDF")
        except Exception as e:
            print(f"  [ERROR] {e}")

        time.sleep(0.5)

    print("\n" + "=" * 60)
    print(f"[OK] Complete! Generated {success_count}/{len(auctions)} PDFs")
    print(f"Saved to: {imoveis_dir}")


if __name__ == "__main__":
    main()
