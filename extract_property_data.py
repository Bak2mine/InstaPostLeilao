"""
Extract property data from HTML and prepare for PDF generation
"""

import re
from datetime import datetime

def extract_property_data_from_html(html_content):
    """Extract all relevant property data from HTML"""

    data = {
        'titulo': None,
        'cidade': None,
        'estado': None,
        'praca1_valor': None,
        'praca2_valor': None,
        'praca1_data': None,
        'praca2_data': None,
        'desconto_pct': None,
        'tipo': None,  # 'tipo1', 'tipo2', etc
    }

    # Extract title: <h2 class="texto-gg">Casa 147m² – Uberlândia/MG</h2>
    title_match = re.search(r'<h2[^>]*>([^<]+)</h2>', html_content)
    if title_match:
        data['titulo'] = title_match.group(1).strip()

    # Extract discount: "Desconto: aproximadamente 36%"
    discount_match = re.search(r'Desconto:\s*aproximadamente\s*([\d.]+)%', html_content)
    if discount_match:
        data['desconto_pct'] = float(discount_match.group(1))

    # Extract location: "Uberlândia/MG"
    if data['titulo']:
        # Try to extract from title
        loc_match = re.search(r'–\s*([^/\n]+)/([A-Z]{2})', data['titulo'])
        if loc_match:
            data['cidade'] = loc_match.group(1).strip()
            data['estado'] = loc_match.group(2).strip()

    # Extract Primeira praça: "R$ 320.418,61" and date "15/06/2026 às 14:00"
    primeira_section = re.search(
        r'Primeira praça.*?<div[^>]*>R\$\s*([\d.,]+)',
        html_content,
        re.DOTALL | re.IGNORECASE
    )
    if primeira_section:
        data['praca1_valor'] = f"R$ {primeira_section.group(1)}"

    primeira_date = re.search(
        r'Primeira praça.*?(\d{2})/(\d{2})/(\d{4})\s+às\s+(\d{2}):(\d{2})',
        html_content,
        re.DOTALL | re.IGNORECASE
    )
    if primeira_date:
        data['praca1_data'] = f"{primeira_date.group(1)}/{primeira_date.group(2)}/{primeira_date.group(3)}"
        data['praca1_hora'] = f"{primeira_date.group(4)}:{primeira_date.group(5)}"

    # Extract Segunda praça: "R$ 320.418,61" and date "29/06/2026 às 14:00"
    segunda_section = re.search(
        r'Segunda praça.*?<div[^>]*>R\$\s*([\d.,]+)',
        html_content,
        re.DOTALL | re.IGNORECASE
    )
    if segunda_section:
        data['praca2_valor'] = f"R$ {segunda_section.group(1)}"
        data['segunda_praca'] = True
    else:
        data['segunda_praca'] = False

    segunda_date = re.search(
        r'Segunda praça.*?(\d{2})/(\d{2})/(\d{4})\s+às\s+(\d{2}):(\d{2})',
        html_content,
        re.DOTALL | re.IGNORECASE
    )
    if segunda_date:
        data['praca2_data'] = f"{segunda_date.group(1)}/{segunda_date.group(2)}/{segunda_date.group(3)}"
        data['praca2_hora'] = f"{segunda_date.group(4)}:{segunda_date.group(5)}"

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


# Test with the Casa 147m² example
test_html = """
<h2 class="texto-gg">Casa 147m² – Uberlândia/MG</h2>
<p class="texto-p mt-2">
    Desconto: aproximadamente 36%<br />
</p>
<div class="col-md-4 borda-branca-produto">
    <div class="subtit-produto ">Primeira praça:</div>
    <div class="">
        <div class="texto-branco-produto texto-pp mt-2 mb-0">15/06/2026 às 14:00</div>
        <div class="texto-branco-produto bold mt-2">R$ 320.418,61</div>
    </div>
</div>
<div class="col-md-4">
    <div class="subtit-produto ">Segunda praça:</div>
    <div class="">
        <div class="texto-branco-produto texto-pp mt-2 mb-0">29/06/2026 às 14:00</div>
        <div class="texto-branco-produto bold mt-2">R$ 320.418,61</div>
    </div>
</div>
"""

if __name__ == "__main__":
    data = extract_property_data_from_html(test_html)
    print("Extracted Property Data:")
    print("-" * 50)
    for key, value in data.items():
        print(f"{key:20} : {value}")
    print("-" * 50)
    print(f"Template Type: {data['tipo']}")
    print(f"Desconto: {data['desconto_pct']}%")
    print(f"Segunda Praça: {data['segunda_praca']}")
