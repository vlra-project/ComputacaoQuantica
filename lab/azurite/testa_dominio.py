import re
from tenable.io import TenableIO

ACCESS_KEY = 'SUA_ACCESS_KEY'
SECRET_KEY = 'SUA_SECRET_KEY'
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

def selecionar_scanner(dominio, scanners):
    dominio = dominio.lower()
    for scanner in scanners:
        nome = scanner['name'].lower()
        if 'itabira' in dominio and 'itabira' in nome:
            return scanner['id']
        elif 'valeglobal' in dominio and 'global' in nome:
            return scanner['id']
        elif 'top.ta.vale.br' in dominio and 'ta' in nome:
            return scanner['id']
    return None  # Scanner padrão pode ser colocado aqui

def processar_arquivo_scanners(nome_arquivo):
    scanners = list(tio.scanners.allowed_scanners())
    with open(nome_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    dominios = re.findall(r'Domain:\s*([^\s-]+)', conteudo)
    ips = re.findall(r'IP:\s*([\d\.]+)', conteudo)
print ['id'] 
