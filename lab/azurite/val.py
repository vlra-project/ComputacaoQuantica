import re
from tenable.io import TenableIO

ACCESS_KEY = 'a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9'
SECRET_KEY = 'c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213'
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

# Busca scanners disponíveis
scanners = list(tio.scanners.allowed_scanners())


#def selecionar_scanner(dominio, scanners):
#    zone = zone.lower()
#    for scanner in scanners:
#        nome = scanner['name'].lower()
#        if 'valenet.valeglobal.net' in dominio and  'IT_BRAZIL_NEW' in nome:
#            print(f"Scanner selecionado: {scanner['id']}")
#            return scanner['id']
#    return None

#def selecionar_scanner(zone,scanners):
#    zone = zone.lower()
#    for scanner in scanners:
#        nome = scanner['name'].lower()
#        if zone == nome;
#             print(f"Scanner selecionado: {scanner['id']}")
#             return scanner['id']

with open('inc.txt', 'r', encoding='utf-8') as f:
    for l in f:
        ip_match = re.search(r'IP:\s*([\d\.]+)', l)
        zone_match = re.search(r'Security Zone:\s*(.*?)(?:\s*-\s*OS:|$)', l)

        if ip_match and zone_match:
            ip = ip_match.group(1)
            zone = zone_match.group(1)
#            scanner_id = selecionar_scanner(zone, scanners)
            print(ip_match.group(1))
            print(zone_match.group(1))
#        if scanner_id:
#            scan = tio.scans.create(
#            name=f"Scan automático: {domain}",
#            targets=ip,
#            template='basic',
#            scanner=scanner_id  # Correto: o parâmetro é scanner, não scanner_id
#        )   
#            scan_id = scan['id']
#            tio.scans.launch(scan_id)
#            print(f'✅ Varredura iniciada para {domain} ({ip}) - Scan ID: {scan_id}')
#        else:
#            print(f'⚠️ Scanner não encontrado para {zone} — varredura não iniciada
