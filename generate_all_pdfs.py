"""
Final Production Script - Generate PDFs for all 46 properties
Scrape → Extract data → Generate PPTX with text + images → Convert to PDF
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pptx_generator_final import PropertyPDFGenerator
import re
import time
from pathlib import Path

BASE_URL = "https://leiloariasmart.com.br"
MAIN_URL = "https://leiloariasmart.com.br/busca"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
TIMEOUT = 30

class PropertyScraper:
    """Scrape property data from website"""

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
        """Extract all property data from page"""
        try:
            response = self.session.get(auction_url, timeout=TIMEOUT)
            response.encoding = 'utf-8'
            html_text = response.text

            # Extract location from title
            # Pattern: "DASH CITY/STATECODE" at end, where STATECODE = 2 uppercase letters
            cidade = None
            estado = None
            titulo_clean = auction_title

            # Match: optional dash/space, then anything, then /, then 2 uppercase letters at end
            match = re.search(r'[–\-]\s*(.+)/([A-Z]{2})\s*$', auction_title)
            if match:
                potential_city = match.group(1).strip()
                potential_state = match.group(2).strip()

                # City should not be empty or just numbers/symbols
                if potential_city and re.search(r'[A-Za-z]', potential_city):
                    cidade = potential_city
                    estado = potential_state
                    # Remove from the LAST dash onwards
                    titulo_clean = re.sub(r'\s*[–\-].+/[A-Z]{2}\s*$', '', auction_title).strip()

            # Fallback: if no dash found, try just city/state pattern
            if not cidade:
                match = re.search(r'(.+)/([A-Z]{2})\s*$', auction_title)
                if match:
                    potential_city = match.group(1).strip()
                    potential_state = match.group(2).strip()
                    if potential_city and len(potential_city) > 2:
                        # Make sure this looks like a real city (not just 1-2 chars or all numbers)
                        if re.search(r'[A-Za-z]{3}', potential_city):
                            cidade = potential_city
                            estado = potential_state
                            titulo_clean = re.sub(r'\s*[–\-]?\s*.+/[A-Z]{2}\s*$', '', auction_title).strip()

            data = {
                'titulo': titulo_clean,
                'cidade': cidade,
                'estado': estado,
                'praca1_valor': None,
                'praca2_valor': None,
                'praca1_data': None,
                'praca2_data': None,
                'desconto_pct': None,
                'segunda_praca': False,
            }

            # Extract discount
            desconto_match = re.search(r'Desconto:\s*aproximadamente\s*([\d.,]+)%', html_text)
            if desconto_match:
                pct_str = desconto_match.group(1).replace(',', '.')
                try:
                    data['desconto_pct'] = float(pct_str)
                except ValueError:
                    pass

            # Extract Primeira praça
            primeira_pattern = r'(?:Primeira\s+pra[çc]a|Pra[çc]a\s+[ÚU]nica):.*?(?=Segunda\s+pra[çc]a:|Desconto:|$)'
            primeira_section = re.search(primeira_pattern, html_text, re.IGNORECASE | re.DOTALL)

            if primeira_section:
                seção = primeira_section.group(0)
                prices = re.findall(r'R\$\s*([\d.,]+)', seção)
                dates = re.findall(r'(\d{2})/(\d{2})/(\d{4})\s+às\s+(\d{2}):(\d{2})', seção)

                if prices:
                    for price in prices:
                        price_float = float(price.replace('.', '').replace(',', '.'))
                        if price_float > 1000:
                            data['praca1_valor'] = f"R$ {price}"
                            break
                    if not data['praca1_valor'] and prices:
                        data['praca1_valor'] = f"R$ {prices[-1]}"

                if dates:
                    d = dates[0]
                    data['praca1_data'] = f"{d[0]}/{d[1]}/{d[2]}"

            # Extract Segunda praça
            segunda_pattern = r'Segunda\s+pra[çc]a:.*?(?=Desconto:|Abaixo Avaliado|$)'
            segunda_section = re.search(segunda_pattern, html_text, re.IGNORECASE | re.DOTALL)

            if segunda_section:
                seção = segunda_section.group(0)
                prices = re.findall(r'R\$\s*([\d.,]+)', seção)
                dates = re.findall(r'(\d{2})/(\d{2})/(\d{4})\s+às\s+(\d{2}):(\d{2})', seção)

                if prices:
                    data['praca2_valor'] = f"R$ {prices[-1]}"
                    data['segunda_praca'] = True

                if dates:
                    d = dates[0]
                    data['praca2_data'] = f"{d[0]}/{d[1]}/{d[2]}"

            return data
        except Exception as e:
            print(f"[ERROR] Error extracting data: {e}")
            return None


def main():
    print("=" * 70)
    print("PRODUCTION: Generate PDFs for All Properties")
    print("=" * 70)

    post_dir = Path("C:\\Users\\andre\\Desktop\\Leiloaria\\Post")
    output_dir = post_dir / "imoveis"
    output_dir.mkdir(exist_ok=True)

    template_pptx = post_dir / "1 e 2 praça.pptx"
    link_pdf = post_dir / "Posts IG.pdf"

    # Validate files exist
    if not template_pptx.exists():
        print(f"ERROR: Template PPTX not found: {template_pptx}")
        return
    if not link_pdf.exists():
        print(f"ERROR: Link PDF not found: {link_pdf}")
        return

    print("\n[1/3] Scraping all properties...")
    scraper = PropertyScraper()
    auctions = scraper.get_all_auctions()

    if not auctions:
        print("ERROR: No properties found")
        return

    print(f"\n[2/3] Validating data extraction...")
    print(f"      (checking first property)")

    # Test with first property
    test_data = scraper.get_property_data(auctions[0]['url'], auctions[0]['title'])
    required_fields = ['titulo', 'cidade', 'estado', 'praca1_valor', 'praca1_data']
    missing = [f for f in required_fields if not test_data.get(f)]
    if missing:
        print(f"WARNING: Some fields missing: {missing}")
    else:
        print(f"      [OK] Data extraction working")

    print(f"\n[3/3] Generating PDFs for all {len(auctions)} properties...")
    print("=" * 70)

    # All template options
    template_1prac = post_dir / "1prac.pptx"  # Praca unica, no desconto
    template_1pracD = post_dir / "1pracD.pptx"  # Praca unica, with desconto
    template_2praca = post_dir / "2praca.pptx"  # Duas pracas, no desconto
    template_duas_com_desconto = template_pptx  # Duas pracas, with desconto (1 e 2 praça.pptx)

    success_count = 0
    failed_count = 0

    for i, auction in enumerate(auctions, 1):
        print(f"\n[{i}/{len(auctions)}] {auction['title'][:60]}")

        property_data = scraper.get_property_data(auction['url'], auction['title'])
        if not property_data:
            print("  [SKIP] No data")
            failed_count += 1
            continue

        # Use search results title as primary source of truth (more reliable than page extraction)
        property_data['titulo'] = auction['title']

        # Use fallback values for other missing fields
        if not property_data.get('cidade'):
            property_data['cidade'] = 'Cidade'
        if not property_data.get('estado'):
            property_data['estado'] = 'UF'
        if not property_data.get('praca1_valor'):
            property_data['praca1_valor'] = 'R$ 0,00'
        if not property_data.get('praca1_data'):
            property_data['praca1_data'] = '01/01/2026'

        # Select template based on property characteristics
        has_segunda = property_data.get('segunda_praca', False)
        has_desconto = bool(property_data.get('desconto_pct'))

        if has_segunda and has_desconto:
            selected_template = str(template_duas_com_desconto)
            template_name = "1 e 2 praça"
        elif has_segunda and not has_desconto:
            selected_template = str(template_2praca)
            template_name = "2praca"
        elif not has_segunda and has_desconto:
            selected_template = str(template_1pracD)
            template_name = "1pracD"
        else:  # not has_segunda and not has_desconto
            selected_template = str(template_1prac)
            template_name = "1prac"

        print(f"  [Template: {template_name}]")

        generator = PropertyPDFGenerator(
            template_pptx=selected_template,
            link_pdf=str(link_pdf),
            output_dir=str(output_dir)
        )

        # Extract property ID from URL for unique filename
        property_id = auction['url'].split('/')[-1]  # Get last part of URL

        # Sanitize title for filename
        title_for_file = re.sub(r'\s*[–-].*$', '', auction['title']).strip()
        safe_title = re.sub(r'[<>:"/\\|?*]', '', title_for_file).strip()

        # Use property ID to ensure uniqueness
        final_filename = f"{safe_title} - {property_id}" if safe_title else f"Property_{property_id}"

        try:
            pptx_path = generator.generate(
                property_url=auction['url'],
                property_data=property_data,
                output_name=final_filename
            )

            if pptx_path and Path(pptx_path).exists():
                print(f"  [OK] PPTX created")
                success_count += 1
            else:
                print(f"  [ERROR] PPTX generation failed")
                failed_count += 1

        except Exception as e:
            print(f"  [ERROR] {str(e)[:50]}")
            failed_count += 1

        time.sleep(0.5)

    print("\n" + "=" * 70)
    print(f"Complete!")
    print(f"  Generated: {success_count}/{len(auctions)} PPTX files")
    print(f"  Failed: {failed_count}")
    print(f"  Output folder: {output_dir}")
    print(f"\nNEXT STEP:")
    print(f"  Open each PPTX in PowerPoint and export as PDF")
    print(f"  Or install LibreOffice for automated PDF conversion")


if __name__ == "__main__":
    main()
