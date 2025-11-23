import re
from tenable.io import TenableIO

ACCESS_KEY = 'a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9'
SECRET_KEY = 'c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213'
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

#lista de alvos
alvos =[]
s_id = None

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
            ip = str(ip_match.group(1))
            zone = str(zone_match.group(1))
            alvos.append(ip)
            print(ip_match.group(1))
            print(zone)
            
            for scanner in scanners:
               nome = scanner['name']
               s_id = scanner['id']
               #s_uuid = scanner['uuid']
               #print(s_uuid)
               if nome == zone:
                 print(s_id)

# Cria e inicia scan
scan = tio.scans.create(
        name='Scan teste1',
        targets=alvos,
        template='basic',
        scanner=(zone)
)

scan_id = scan['id']
tio.scans.launch(scan_id)
print('Iniciado')

                 #scan = tio.scans.create(
                 #        name='Scan teste',
                 #        scanner_id=s_id,
                 #        targets=[ip],
                 #        template='basic'                         
                 #        ) 

#               scan_id = scan['id']
                # print(scan)
                 #tio.scans.launch(scan)
#               print(f'✅ Varredura iniciada para {zone} ({ip}) - Scan ID: {s_id}')
#        else:
#            print(f'⚠️ Scanner não encontrado para {zone} — varredura não iniciada
