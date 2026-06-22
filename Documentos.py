import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import re
import time

BASE_URL = "https://leiloariasmart.com.br"
MAIN_URL = "https://leiloariasmart.com.br/busca"

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
TIMEOUT = 30  # seconds before giving up on a request

def sanitize_folder_name(name):
    # Replace / with " - " for Windows compatibility, then remove other invalid chars
    name = name.replace('/', ' - ')
    return re.sub(r'[<>:"\\|?*]', '', name).strip()

def get_all_auctions(url):
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    auctions = []
    for card in soup.find_all('div', class_='caixa-imoveis'):
        title_tag = card.find('div', class_='info-imovel-2')
        if not title_tag:
            continue
        link_tag = title_tag.find('a', href=True)
        if not link_tag:
            continue
        title    = link_tag.text.strip()
        full_url = urljoin(BASE_URL, link_tag['href'])
        auctions.append({'title': title, 'url': full_url})
    
    print(f"Encontrados {len(auctions)} imóveis\n")
    return auctions


def get_documents_from_auction(auction_url):
    response = requests.get(auction_url, headers=HEADERS, timeout=TIMEOUT)
    soup     = BeautifulSoup(response.text, 'html.parser')
    
    docs = {}
    for btn in soup.find_all('a', class_='btn77'):
        label = btn.text.strip().upper()
        href  = btn.get('href', '')
        
        if not href.endswith('.pdf'):
            continue

        # FIX: make sure URL is always absolute
        full_url = href if href.startswith('http') else urljoin(BASE_URL, href)

        if 'EDITAL' in label:
            docs['edital'] = full_url
        elif 'MATR' in label:
            docs['matrícula'] = full_url
        elif 'AVALI' in label:
            docs['avaliação'] = full_url
    
    return docs


def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True, headers=HEADERS, timeout=TIMEOUT)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"    ✓ {os.path.basename(save_path)}")
        else:
            print(f"    ✗ Erro HTTP {response.status_code}: {url}")
    except requests.exceptions.Timeout:
        print(f"    ✗ Timeout ao baixar: {url}")
    except Exception as e:
        print(f"    ✗ Erro: {e}")


def scrape_leiloaria_smart():
    desktop  = r'C:\Users\andre\Desktop\Leiloaria'
    imob_dir = os.path.join(desktop, 'imobiliarios')
    os.makedirs(imob_dir, exist_ok=True)
    
    auctions = get_all_auctions(MAIN_URL)
    failed   = []  # track any that fail so we can retry

    for i, auction in enumerate(auctions):
        print(f"[{i+1}/{len(auctions)}] {auction['title']}")
        
        folder_name = sanitize_folder_name(auction['title'])
        house_dir   = os.path.join(imob_dir, folder_name)
        os.makedirs(house_dir, exist_ok=True)
        
        # Retry up to 3 times on timeout
        docs = {}
        for attempt in range(3):
            try:
                docs = get_documents_from_auction(auction['url'])
                break
            except requests.exceptions.Timeout:
                print(f"    ⚠ Timeout (tentativa {attempt+1}/3), aguardando...")
                time.sleep(5)
            except Exception as e:
                print(f"    ✗ Erro ao acessar página: {e}")
                break
        
        if not docs:
            print("    ⚠ Nenhum documento encontrado — pulando")
            failed.append(auction['title'])
        else:
            for doc_name, doc_url in docs.items():
                save_path = os.path.join(house_dir, f"{doc_name}.pdf")
                download_file(doc_url, save_path)
        
        time.sleep(1.5)  # slightly longer pause to be polite
    
    # Summary
    print("\n✅ Concluído!")
    if failed:
        print(f"\n⚠ {len(failed)} imóveis falharam:")
        for name in failed:
            print(f"   - {name}")


scrape_leiloaria_smart()