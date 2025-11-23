import re
from tenable.io import TenableIO

# Inicializa o cliente do Tenable.io
ACCESS_KEY = 'SUA_ACCESS_KEY'
SECRET_KEY = 'SUA_SECRET_KEY'
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

# Lista de alvos extraídos
alvos = []
scanner_id = None

# Mapeamento Domain -> Scanner
zonas_para_scanner = {
    'valenet.valeglobal.net': 'All_IT_Scanners'  # ou o scanner_id numérico correspondente
}

# Lê o arquivo e extrai IP e Domain
with open('inc.txt', 'r', encoding='utf-8') as f:
    for linha in f:
        ip_match = re.search(r'IP:([\d\.]+)', linha)
        domain_match = re.search(r'Domain:\s*(.*?)(?:\s*-\s*OS:|$)', linha)

        if ip_match and domain_match:
            ip = ip_match.group(1).strip()
            domain = domain_match.group(1).strip()
            alvos.append(ip)
            scanner_id = zonas_para_scanner.get(domain)

if not scanner_id:
    raise ValueError('Domain não reconhecido — verifique o mapeamento.')

# Cria e inicia o scan
scan = tio.scans.create(
    name=f'Scan automático: {domain}',
    targets=','.join(alvos),
    template='basic',
    scanner=scanner_id
)

scan_id = scan['id']
tio.scans.launch(scan_id)
print(f'Scan iniciado com ID {scan_id} usando scanner "{scanner_id}"')
