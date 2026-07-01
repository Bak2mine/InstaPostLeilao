"""
Web scraper for leiloariasmart.com.br property data
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
from typing import List, Dict, Optional
from config import BASE_URL, MAIN_URL, HEADERS, TIMEOUT

class PropertyScraper:
    """Scrapes and extracts property data from leiloariasmart.com.br"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def get_all_auctions(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all auctions from search page

        Args:
            limit: Maximum number of properties to return (None = all)

        Returns:
            List of dicts with 'title' and 'url' keys
        """
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

                if limit and len(auctions) >= limit:
                    break

            print(f"[OK] Found {len(auctions)} properties")
            return auctions

        except Exception as e:
            print(f"[ERROR] Error fetching auctions: {e}")
            return []

    def get_property_data(self, auction_url: str, auction_title: str) -> Optional[Dict]:
        """Extract all relevant data from property page

        Args:
            auction_url: Full URL to property page
            auction_title: Title from listing page

        Returns:
            Dict with all property data or None if extraction fails
        """
        try:
            response = self.session.get(auction_url, timeout=TIMEOUT)
            response.encoding = 'utf-8'
            html_text = response.text

            # Extract location from auction title: "Casa 147m² – Uberlândia/MG" or "Casa 190m² São Paulo/SP"
            # Match multi-word city names (e.g., São Paulo, Rio de Janeiro)
            # Pattern: Capital letter + letters, optionally followed by more words (capital OR lowercase)
            # Handles: São Paulo (capital-capital), Rio de Janeiro (capital-lowercase-capital), etc.
            # Then: optional space + / + optional space + 2-letter state code + trailing constraint

            # First pass: strict with non-greedy + trailing constraints (case-insensitive)
            loc_match = re.search(
                r'([A-Z][a-záàâãéèêíïóôõöúçñ]*(?:\s+(?:[A-Z]|de|do|da|dos|das)?[a-záàâãéèêíïóôõöúçñ]+)*)\s*/\s*([A-Z]{2})(?:\s|–|—|\-|$)',
                auction_title, re.UNICODE | re.IGNORECASE
            )
            if loc_match:
                cidade = loc_match.group(1).strip()
                estado = loc_match.group(2).strip()
                titulo_clean = re.sub(r'\s*[–—\-]?\s*' + re.escape(cidade) + r'/[A-Z]{2}.*$', '', auction_title, flags=re.IGNORECASE).strip()
            else:
                # Fallback: flexible pattern without strict trailing constraints (case-insensitive)
                slash_match = re.search(
                    r'([A-Z][a-záàâãéèêíïóôõöúçñ]*(?:\s+(?:[A-Z]|de|do|da|dos|das)?[a-záàâãéèêíïóôõöúçñ]+)*)\s*/\s*([A-Z]{2})',
                    auction_title, re.UNICODE | re.IGNORECASE
                )
                if slash_match:
                    cidade = slash_match.group(1).strip()
                    estado = slash_match.group(2).strip()
                    titulo_clean = re.sub(r'[\s–—\-]*' + re.escape(cidade) + r'/[A-Z]{2}.*$', '', auction_title, flags=re.IGNORECASE).strip()
                else:
                    cidade = None
                    estado = None
                    titulo_clean = auction_title

            data = {
                'titulo': titulo_clean,
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
                'auction_url': auction_url,
            }

            # Extract discount percentage (with or without "aproximadamente")
            desconto_match = re.search(r'Desconto:\s*(?:aproximadamente\s+)?([\d.,]+)%', html_text, re.IGNORECASE)
            if desconto_match:
                pct_str = desconto_match.group(1).replace(',', '.')
                try:
                    data['desconto_pct'] = float(pct_str)
                except ValueError:
                    pass

            # Extract Primeira praça OR Praça Única
            primeira_pattern = r'(?:Primeira\s+pra[çc]a|Pra[çc]a\s+[ÚU]nica):.*?(?=Segunda\s+pra[çc]a:|Desconto:|$)'
            primeira_section = re.search(primeira_pattern, html_text, re.IGNORECASE | re.DOTALL)

            if primeira_section:
                seção = primeira_section.group(0)
                prices = re.findall(r'R\$\s*([\d.,]+)', seção)
                dates = re.findall(r'(\d{2})/(\d{2})/(\d{4})\s+às\s+(\d{2}):(\d{2})', seção)

                # Use first valid price (> 1000)
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
                    data['praca1_hora'] = f"{d[3]}:{d[4]}"

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
                    data['praca2_hora'] = f"{d[3]}:{d[4]}"

            # Determine template type
            has_segunda = data['segunda_praca']
            has_desconto = data['desconto_pct'] is not None

            if has_segunda and has_desconto:
                data['tipo'] = 'tipo1'
            elif not has_segunda and has_desconto:
                data['tipo'] = 'tipo2'
            elif has_segunda and not has_desconto:
                data['tipo'] = 'tipo3'
            else:
                data['tipo'] = 'tipo4'

            return data

        except Exception as e:
            print(f"[ERROR] Error extracting data from {auction_url}: {e}")
            return None

    def extract_first_image_url(self, html_text: str) -> Optional[str]:
        """Extract first image URL from property page HTML"""
        matches = re.findall(r'src="(https://leiloariasmart\.com\.br/_admin_/upload/[^"]+)"', html_text)
        return matches[0] if matches else None

    def get_property_page_html(self, property_url: str) -> Optional[str]:
        """Get raw HTML from property page"""
        try:
            response = self.session.get(property_url, timeout=TIMEOUT)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"[ERROR] Error downloading property page: {e}")
            return None
