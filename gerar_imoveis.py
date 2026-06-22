"""
Scraper and PDF generator for leilão properties.
Combines data from leiloariasmart.com.br with template filling.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
import time
import json
from pathlib import Path
from pypdf import PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
import textwrap

BASE_URL = "https://leiloariasmart.com.br"
MAIN_URL = "https://leiloariasmart.com.br/busca"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
TIMEOUT = 30



class PropertyScraper:
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

    def get_property_data(self, auction_url):
        """Extract all relevant data from property page"""
        try:
            response = self.session.get(auction_url, timeout=TIMEOUT)
            response.encoding = 'utf-8'
            html_text = response.text
            soup = BeautifulSoup(html_text, 'html.parser')

            data = {
                'url': auction_url,
                'praca_unica': False,
                'segunda_praca': False,
                'desconto_pct': None,
                'praca1_valor': None,
                'praca2_valor': None,
                'cidade': None,
                'estado': None,
                'imagem_url': None
            }

            # Extract prices - find praca labels and get following price
            # Look for both "Primeira Praça", "Segunda Praça", and "Praça Única"

            # Find all praca mentions
            for match in re.finditer(r'[Pp]ra[çc]a[^<]{0,100}:', html_text):
                label_text = match.group().lower()
                # Get price within 500 chars after the label
                after_pos = match.end()
                after_text = html_text[after_pos:after_pos+500]
                price_match = re.search(r'R\$\s*([\d.,]+)', after_text)

                if price_match:
                    price_val = f"R$ {price_match.group(1)}"

                    if 'primeira' in label_text:
                        data['praca1_valor'] = price_val
                        data['praca_unica'] = False
                    elif 'segunda' in label_text:
                        data['praca2_valor'] = price_val
                        data['segunda_praca'] = True
                    elif 'nica' in label_text or 'unica' in label_text:
                        data['praca1_valor'] = price_val
                        data['praca_unica'] = True

            # Extract discount percentage
            desconto_match = re.search(r'Desconto:\s*aproximadamente\s*([\d.,]+)%', html_text)
            if desconto_match:
                pct_str = desconto_match.group(1).replace(',', '.')
                try:
                    data['desconto_pct'] = float(pct_str)
                except ValueError:
                    data['desconto_pct'] = None

            # Extract location from description
            description = soup.find('p', class_='texto-p')
            if description:
                desc_text = description.text
                # More flexible pattern for city/state
                local_match = re.search(
                    r'([A-Z][a-záàâãéèêíïóôõöúçñ\s]+?)\s*/\s*([A-Z]{2})',
                    desc_text
                )
                if local_match:
                    data['cidade'] = local_match.group(1).strip()
                    data['estado'] = local_match.group(2).strip()

            # Extract image - first image with "upload" in URL (main property photo)
            img_urls = re.findall(r'src="([^"]*_admin_/upload[^"]*)"', html_text)
            if img_urls:
                # Use the first upload image (main property photo)
                img_url = img_urls[0]
                if not img_url.startswith('http'):
                    img_url = urljoin(BASE_URL, img_url)
                data['imagem_url'] = img_url

            return data
        except Exception as e:
            print(f"[ERROR] Error extracting property data: {e}")
            return None

    def download_image(self, image_url):
        """Download image and return PIL Image object"""
        try:
            response = self.session.get(image_url, timeout=TIMEOUT)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        except Exception as e:
            print(f"[ERROR] Error downloading image: {e}")
        return None


class TemplateAnalyzer:
    """Helper to analyze template PDF and extract structure"""

    @staticmethod
    def extract_template_pages(pdf_path, output_dir):
        """Extract first 4 pages of PDF as images for analysis"""
        try:
            reader = PdfReader(pdf_path)
            os.makedirs(output_dir, exist_ok=True)

            print("[*] Extracting template pages...")
            for i in range(min(4, len(reader.pages))):
                print(f"  Page {i+1}: {reader.pages[i].mediabox}")

            return True
        except Exception as e:
            print(f"[ERROR] Error analyzing templates: {e}")
            return False


class PDFGenerator:
    """Generate final 2-page PDFs with filled templates"""

    # Default positions for text and images on templates (in points)
    # Each template has slightly different layout
    DEFAULT_COORDS = {
        'tipo1': {  # 2a praca + desconto
            'titulo': (50, 750, 500),  # x, y, max_width
            'cidade_estado': (50, 730, 300),
            'praca1_label': (50, 700, 200),
            'praca1_valor': (250, 700, 150),
            'praca2_label': (50, 680, 200),
            'praca2_valor': (250, 680, 150),
            'desconto': (50, 660, 300),
            'imagem': (300, 600, 250, 200),  # x, y, width, height
        },
        'tipo2': {  # praca unica + desconto
            'titulo': (50, 750, 500),
            'cidade_estado': (50, 730, 300),
            'praca1_label': (50, 700, 200),
            'praca1_valor': (250, 700, 150),
            'desconto': (50, 680, 300),
            'imagem': (300, 600, 250, 200),
        },
        'tipo3': {  # 2a praca, sem desconto
            'titulo': (50, 750, 500),
            'cidade_estado': (50, 730, 300),
            'praca1_label': (50, 700, 200),
            'praca1_valor': (250, 700, 150),
            'praca2_label': (50, 680, 200),
            'praca2_valor': (250, 680, 150),
            'imagem': (300, 600, 250, 200),
        },
        'tipo4': {  # praca unica, sem desconto
            'titulo': (50, 750, 500),
            'cidade_estado': (50, 730, 300),
            'praca1_label': (50, 700, 200),
            'praca1_valor': (250, 700, 150),
            'imagem': (300, 600, 250, 200),
        },
    }

    def __init__(self, template_pdf_path):
        self.template_pdf = template_pdf_path

    def determine_template_type(self, property_data):
        """Determine which template to use based on property characteristics"""
        has_segunda = property_data.get('segunda_praca', False)
        has_desconto = property_data.get('desconto_pct') is not None

        if has_segunda and has_desconto:
            return 'tipo1'  # 2a praca + desconto → page 1
        elif not has_segunda and has_desconto:
            return 'tipo2'  # praca unica + desconto → page 2
        elif has_segunda and not has_desconto:
            return 'tipo3'  # 2a praca, sem desconto → page 3
        else:
            return 'tipo4'  # praca unica, sem desconto → page 4

    def _download_image(self, image_url):
        """Download image and return PIL Image"""
        try:
            if not image_url:
                return None
            response = requests.get(image_url, timeout=10, headers=HEADERS)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content)).convert('RGB')
        except Exception as e:
            print(f"    [WARN] Failed to download image: {e}")
        return None

    def _create_filled_page(self, property_data, template_type):
        """Create a filled template page using reportlab"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader

            # A4 size in points (595 x 842)
            width, height = 595, 842

            pdf_bytes = BytesIO()
            c = canvas.Canvas(pdf_bytes, pagesize=(width, height))

            coords = self.DEFAULT_COORDS[template_type]

            # Draw background (light gray)
            c.setFillColorRGB(0.95, 0.95, 0.95)
            c.rect(0, 0, width, height, fill=1)

            c.setFillColorRGB(0, 0, 0)

            # Title
            if property_data.get('title'):
                c.setFont("Helvetica-Bold", 16)
                title_x, title_y, _ = coords['titulo']
                c.drawString(title_x, height - title_y, property_data['title'][:60])

            # Location
            location = f"{property_data.get('cidade', '')}/{property_data.get('estado', '')}"
            if location.strip('/'):
                c.setFont("Helvetica", 12)
                loc_x, loc_y, _ = coords['cidade_estado']
                c.drawString(loc_x, height - loc_y, location)

            # Praca 1
            if property_data.get('praca1_valor'):
                c.setFont("Helvetica-Bold", 14)
                p1_x, p1_y, _ = coords['praca1_valor']
                c.drawString(p1_x, height - p1_y, f"1o Leilao: {property_data['praca1_valor']}")

            # Praca 2 (if applicable)
            if property_data.get('praca2_valor') and 'praca2_valor' in coords:
                c.setFont("Helvetica-Bold", 14)
                p2_x, p2_y, _ = coords['praca2_valor']
                c.drawString(p2_x, height - p2_y, f"2o Leilao: {property_data['praca2_valor']}")

            # Desconto (if applicable)
            if property_data.get('desconto_pct') and 'desconto' in coords:
                c.setFont("Helvetica", 12)
                d_x, d_y, _ = coords['desconto']
                c.drawString(d_x, height - d_y, f"Desconto: {property_data['desconto_pct']:.1f}%")

            # Property image
            if property_data.get('imagem_url') and 'imagem' in coords:
                img = self._download_image(property_data['imagem_url'])
                if img:
                    # Resize image
                    img_w, img_h = coords['imagem'][2:]
                    img.thumbnail((img_w, img_h), Image.Resampling.LANCZOS)

                    # Save image to bytes
                    img_bytes = BytesIO()
                    img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)

                    # Draw on canvas
                    img_x, img_y = coords['imagem'][:2]
                    try:
                        c.drawImage(ImageReader(img_bytes), img_x, height - img_y - img_h, width=img.width, height=img.height)
                    except:
                        pass  # If image fails, just continue

            c.save()
            pdf_bytes.seek(0)
            return PdfReader(pdf_bytes).pages[0]
        except Exception as e:
            print(f"    [WARN] Error creating filled page: {e}")
            return None

    def generate_pdf(self, property_data, title, output_path):
        """Generate final 2-page PDF: filled template + link page"""
        try:
            template_type = self.determine_template_type(property_data)
            print(f"  Template: {template_type}")

            # Store title in property data
            property_data['title'] = title

            # Read template PDF to get link page
            reader = PdfReader(self.template_pdf)
            link_page = reader.pages[-1]

            # Create filled template page
            filled_page = self._create_filled_page(property_data, template_type)
            if filled_page is None:
                print(f"  [WARN] Using blank page")
                filled_page = reader.pages[0]

            # Create output PDF
            writer = PdfWriter()
            writer.add_page(filled_page)
            writer.add_page(link_page)

            # Write output
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                writer.write(f)

            print(f"  [OK] Saved")
            return True

        except Exception as e:
            print(f"  [ERROR] {e}")
            return False


def main():
    print("=" * 60)
    print("Leilao Property PDF Generator")
    print("=" * 60)

    # Ensure output directory exists
    post_dir = Path(__file__).parent
    imoveis_dir = post_dir / "imoveis"
    imoveis_dir.mkdir(exist_ok=True)

    # Analyze templates first
    print("\n[1/3] Analyzing templates...")
    template_pdf = post_dir / "Posts IG.pdf"
    TemplateAnalyzer.extract_template_pages(str(template_pdf), str(post_dir / "templates_extracted"))

    # Scrape properties
    print("\n[2/3] Scraping properties...")
    scraper = PropertyScraper()
    auctions = scraper.get_all_auctions()

    if not auctions:
        print("[ERROR] No properties found. Exiting.")
        return

    # Process each property
    print("\n[3/3] Processing properties...")
    generator = PDFGenerator(str(template_pdf))

    for i, auction in enumerate(auctions[:3], 1):  # Limit to 3 for testing
        print(f"\n[{i}] {auction['title']}")

        property_data = scraper.get_property_data(auction['url'])
        if not property_data:
            print("  Skipped (no data)")
            continue

        # Sanitize filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '', auction['title']).replace('/', ' - ')
        pdf_path = imoveis_dir / f"{safe_title}.pdf"

        # Generate PDF
        generator.generate_pdf(property_data, auction['title'], str(pdf_path))

        time.sleep(0.5)  # Be polite to the server

    print("\n" + "=" * 60)
    print("[OK] Complete!")


if __name__ == "__main__":
    main()
