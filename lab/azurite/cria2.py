from tenable.io import TenableIO
import re

ACCESS_KEY = 'a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9'
SECRET_KEY = 'c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213'
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

# Função para escolher o scanner com base em palavras-chave no domínio
def selecionar_scanner(dominio, scanners):
    dominio = dominio.lower()
    for scanner in scanners:
        nome = scanner['name'].lower()
        if 'valeglobal' in dominio and 'IT_BRAZIL_NEW' in nome:
            return scanner['id']
        # Aqui você pode adicionar outras condições, se desejar
    return None  # Pode colocar ID de fallback aqui se quiser

# Busca scanners disponíveis
scanners = list(tio.scanners.allowed_scanners())

#for scaner in scanners:
#   print(scaner['id'])

#with open('inc.txt', 'r', encoding='utf-8') as f:
#    for l in f:
#        ip_match = re.search(r'IP:\s*([\d\.]+)', l)
#        domain_match = re.search(r'Domain:\s*(.*?)(?:\s*-\s*OS:|$)', l)
#        if ip_match:
#            print(ip_match.group(1))
#            print(domain_match.group(1))
#
#        if domain_match = "valenet.valeglobal.net"
#            for scanner in scanners
#                scanner = re.search(r'id')


with open('inc.txt', 'r', encoding='utf-8') as f:
    for l in f:
        ip_match = re.search(r'IP:\s*([\d\.]+)', l)
        domain_match = re.search(r'Domain:\s*(.*?)(?:\s*-\s*OS:|$)', l)

        if ip_match and domain_match:
            ip = ip_match.group(1)
            domain = domain_match.group(1)
#            print(f"IP: {ip}")
#            print(f"Domain: {domain}")
             scanner_id = selecionar_scanner(dominio, scanners)

def selecionar_scanner(dominio, scanners):
    dominio = dominio.lower()
    for scanner in scanners:
        nome = scanner['name'].lower()
        if 'valenet.valeglobal.net' in dominio:
            return scanner['id']
            print('id')

#            if domain == "valenet.valeglobal.net":
#                for scanner in scanners:
#                    print(f"Scanner ID: {scanner['id']} | Nome: {scanner['name']}")



"""
# Leitura do arquivo e criação de scans
with open('inc.txt', 'r', encoding='utf-8') as f:
    for linha in f:
        ip_match = re.search(r'IP:([\d\.]+)', linha)
        domain_match = re.search(r'Domain:\s*(.*?)(?:\s*-\s*OS:|$)', linha)

        if ip_match and domain_match:
            ip = ip_match.group(1).strip()
            domain = domain_match.group(1).strip()
            scanner_id = selecionar_scanner(domain, scanners)

            if scanner_id:
                scan = tio.scans.create(
                    name=f"Scan automático: {domain}",
                    targets=ip,
                    template='basic',
                    scanner=scanner_id  # Aqui era "scanner_id=scanner_id", o correto é "scanner="
                )
                scan_id = scan['id']
                tio.scans.launch(scan_id)
                print(f'Varredura iniciada para {domain} ({ip}) - Scan ID: {scan_id}')
            else:
                print(f'Nenhum scanner encontrado para o domínio: {domain}')
"""                
