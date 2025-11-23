import re
from tenable.io import TenableIO

# Substitua pelas suas credenciais da API do Tenable.io
ACCESS_KEY = 'a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9'
SECRET_KEY = 'c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213'

# Inicializa o cliente do Tenable.io
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

# Lista de alvos extraídos
alvos = []
scanner_id = None

zonas_para_scanner = {
        'Brasil - OT Site - MG - Itabira - Conceição' :101,
    }


# Lê o arquivo e extrai IP e Security Zone
with open('inc.txt', 'r', encoding='utf-8') as f:
    for linha in f:
        ip_match = re.search(r'IP:([\d\.]+)', linha)
        zona_match = re.search(r'Security Zone:\s*(.*?)(?:\s*-\s*OS:|$)', linha)

        if ip_match and zona_match:
            ip = ip_match.group(1).strip()
            zona = zona_match.group(1).strip()
            alvos.append(ip)
            scanner_id = zonas_para_scanner.get(zona)
#if not scanner_id:
#    raise ValueError('Security Zone não reconhecida — verifique o mapeamento.')

scan = tio.scans.create(
    name=f'Scan automático: {zona}',
    targets='{ip}',
#    template='VALE_SCAN_TEMPLATE',
#    scanner='OT_MG_ITABIRA'

)

scan_id = scan['id']
tio.scans.launch(scan_id)
#print(ip,zona)
