"""
Leilao Property PDF Generator - HTML Template Version
Scrapes property data and fills HTML templates, then converts to PDF
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
import time
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

BASE_URL = "https://leiloariasmart.com.br"
MAIN_URL = "https://leiloariasmart.com.br/busca"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
TIMEOUT = 30


class PropertyScraper:
    """Scrapes property data from leiloariasmart.com.br"""

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

            # Extract prices using regex patterns
            primeira_match = re.search(
                r'Primeira\s+Pra[çc]a[^R]*?R\$\s*([\d.,]+)',
                html_text, re.IGNORECASE | re.DOTALL
            )
            segunda_match = re.search(
                r'Segunda\s+Pra[çc]a[^R]*?R\$\s*([\d.,]+)',
                html_text, re.IGNORECASE | re.DOTALL
            )
            unica_match = re.search(
                r'Pra[çc]a\s+[ÚU]nica[^R]*?R\$\s*([\d.,]+)',
                html_text, re.IGNORECASE | re.DOTALL
            )

            if primeira_match:
                data['praca1_valor'] = f"R$ {primeira_match.group(1)}"
                data['praca_unica'] = False

            if segunda_match:
                data['praca2_valor'] = f"R$ {segunda_match.group(1)}"
                data['segunda_praca'] = True
            elif unica_match and not primeira_match:
                data['praca1_valor'] = f"R$ {unica_match.group(1)}"
                data['praca_unica'] = True
                data['segunda_praca'] = False

            # Extract discount percentage
            desconto_match = re.search(r'Desconto:\s*aproximadamente\s*([\d.,]+)%', html_text)
            if desconto_match:
                pct_str = desconto_match.group(1).replace(',', '.')
                try:
                    data['desconto_pct'] = float(pct_str)
                except ValueError:
                    data['desconto_pct'] = None

            # Extract location
            description = BeautifulSoup(html_text, 'html.parser').find('p', class_='texto-p')
            if description:
                desc_text = description.text
                local_match = re.search(
                    r'([A-Z][a-záàâãéèêíïóôõöúçñ\s]+?)\s*/\s*([A-Z]{2})',
                    desc_text
                )
                if local_match:
                    data['cidade'] = local_match.group(1).strip()
                    data['estado'] = local_match.group(2).strip()

            # Extract image
            img_urls = re.findall(r'src="([^"]*_admin_/upload[^"]*)"', html_text)
            if img_urls:
                img_url = img_urls[0]
                if not img_url.startswith('http'):
                    img_url = urljoin(BASE_URL, img_url)
                data['imagem_url'] = img_url

            return data
        except Exception as e:
            print(f"[ERROR] Error extracting property data: {e}")
            return None


class PDFGenerator:
    """Generates PDFs from HTML templates"""

    def __init__(self, template_dir, link_pdf_path):
        self.template_dir = template_dir
        self.link_pdf = link_pdf_path
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def determine_template_type(self, property_data):
        """Determine which template to use based on property characteristics"""
        # All types use the same base template now
        return 'base'

    def _html_to_pdf_with_playwright(self, html_path, pdf_path):
        """Convert HTML file to PDF using Playwright"""
        try:
            import asyncio
            from playwright.async_api import async_playwright

            async def convert():
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page()
                    # Use file:// URL to load local HTML
                    await page.goto(f'file://{os.path.abspath(html_path)}', wait_until='networkidle')
                    await page.pdf(path=pdf_path, format='A4', margin={'top': '0.5in', 'bottom': '0.5in', 'left': '0.5in', 'right': '0.5in'})
                    await browser.close()

            asyncio.run(convert())
            return True
        except Exception as e:
            print(f"[DEBUG] Playwright error: {e}")
            return False

    def _get_link_page(self):
        """Extract link page from template PDF"""
        try:
            reader = PdfReader(self.link_pdf)
            return reader.pages[-1]
        except Exception as e:
            print(f"[WARN] Could not extract link page: {e}")
            return None

    def generate_pdf(self, property_data, title, output_path):
        """Generate PDF from HTML template"""
        try:
            template_type = self.determine_template_type(property_data)
            print(f"  Template: {template_type}", end='')

            # Add title to data
            property_data['titulo'] = title

            # Load and render template
            template = self.jinja_env.get_template(f'{template_type}.html')
            html_content = template.render(**property_data)

            # Save HTML file
            html_path = output_path.replace('.pdf', '.html')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Try converting HTML to PDF with Playwright
            if self._html_to_pdf_with_playwright(html_path, output_path):
                # Append LINK page from template
                try:
                    link_page = self._get_link_page()
                    if link_page:
                        reader = PdfReader(output_path)
                        writer = PdfWriter()
                        for page in reader.pages:
                            writer.add_page(page)
                        writer.add_page(link_page)
                        with open(output_path, 'wb') as f:
                            writer.write(f)
                except Exception as e:
                    pass  # Continue even if link page append fails

                print(" -> [OK] PDF (2 pages)")
                return True

            # If Playwright fails, try wkhtmltopdf
            try:
                import subprocess
                subprocess.run(
                    ['wkhtmltopdf', html_path, output_path],
                    check=True,
                    capture_output=True,
                    timeout=30
                )
                print(" -> [OK] PDF (wkhtmltopdf)")
                return True
            except Exception as e:
                print(f" -> [WARN] Could not convert to PDF")
                print(f"    HTML saved: {os.path.basename(html_path)}")
                return False

        except Exception as e:
            print(f"  [ERROR] {e}")
            return False


def main():
    print("=" * 60)
    print("Leilao Property Generator - HTML Template Version")
    print("=" * 60)

    # Setup paths
    post_dir = Path(__file__).parent
    template_dir = post_dir / "templates"
    imoveis_dir = post_dir / "imoveis"
    template_pdf = post_dir / "Posts IG.pdf"

    imoveis_dir.mkdir(exist_ok=True)

    # Verify templates exist
    if not template_dir.exists():
        print(f"[ERROR] Template directory not found: {template_dir}")
        return

    print(f"\n[1/3] Found {len(list(template_dir.glob('*.html')))} HTML templates")

    # Scrape properties
    print("\n[2/3] Scraping properties...")
    scraper = PropertyScraper()
    auctions = scraper.get_all_auctions()

    if not auctions:
        print("[ERROR] No properties found")
        return

    # Generate PDFs
    print("\n[3/3] Generating documents...\n")
    generator = PDFGenerator(str(template_dir), str(template_pdf))

    for i, auction in enumerate(auctions, 1):  # Process all properties
        print(f"[{i}] {auction['title']}")

        property_data = scraper.get_property_data(auction['url'])
        if not property_data:
            print("  Skipped (no data)")
            continue

        # Sanitize filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '', auction['title']).replace('/', ' - ')
        pdf_path = imoveis_dir / f"{safe_title}.pdf"

        generator.generate_pdf(property_data, auction['title'], str(pdf_path))
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("[OK] Complete!")
    print(f"\nHTML files saved in: {imoveis_dir}/")
    print("\nTo convert HTML to PDF, install wkhtmltopdf:")
    print("  https://wkhtmltopdf.org/")


if __name__ == "__main__":
    main()
