import re
from tenable.io import TenableIO

import time

#import logging
#logging.basicConfig(level=logging.DEBUG)


ACCESS_KEY = 'a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9'
SECRET_KEY = 'c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213'
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

#lista de alvos
alvos =[]
s_id = None

# Busca scanners disponíveis
scanners = list(tio.scanners.allowed_scanners())


#def buscar_credencial_por_nome(nome_desejado, credenciais):
#    for cred in credenciais:
#        if cred['name'].lower() == nome_desejado.lower():
#            return cred['uuid']
#    return None

#credenciais = list(tio.credentials.list())

#Busca Credencial
#cred = list(tio.credentials.list())
#print(cred)


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

#cred_id = buscar_credencial_por_nome('test_scan', credenciais)
#print(cred_id)

# Cria e inicia scan
scan = tio.scans.create(
        name='Scan teste1',
        targets=alvos,
        template='basic',
        scanner=(zone),
        settings={
            "credentials" :[
                {
                    "id": "Host",
                    "category": "Host",
                    "default_expand": true,
                    "types": [
                      {
                           "id": "Windows",
                           "name": "Windows",
                           "max": -1,
                           "configuration": [
                               {
                                   "type": "select",
                                   "name": "Authentication method",
                                   "default": "Password",
                                   "required": true,
                                   "id": "auth_method",
                                   "options": [
                                       {
                                           "name": "Password",
                                           "inputs": [
                                               {
                                                   "type": "text",
                                                    "name": "Username",
                                                    "required": true,
                                                    "placeholder": "administrator",
                                                    "id": "username"
                                                }
                                               ]
                                               
                                       }
                                   ]
                               }
                           ]
                      }
                    ]
                }
            

                           

        #settings={
        #    'credentials':{'Host':{'Windows':[{'id':'662bb281-ecdb-401c-af4a-09266410e06d'}]}},
                #'Windows':[{
                #   'name':'Valenet',
                #   'uuid': '662bb281-ecdb-401c-af4a-09266410e06d'
                #}]
             #}
        #}




scan_id = scan['id']
tio.scans.launch(scan_id)
print('Iniciado')

def aguardar_conclusao_e_exportar(scan_id, formato='pdf'):
 #   # Aguarda até o scan ser concluído
    while True:
        status = tio.scans.status(scan_id)
        print(f"⏳ Status atual do scan {scan_id}: {status}")
        if status == 'completed':
            print("✅ Scan concluído!")
            break
        elif status in ['canceled', 'aborted']:
            print(f"⚠️ Scan encerrado prematuramente com status: {status}")
            return
        time.sleep(15)  # espera 15 segundos antes de checar novamente

    # Solicita a exportação
    export_id = tio.scans.export(scan_id, format=json)
    print(f"📦 Exportação iniciada (formato: {formato}, export_id: {export_id})")

    # Aguarda o relatório ficar pronto
    while not tio.scans.export_status(scan_id, export_id) == 'ready':
        print("🕒 Aguardando finalização da exportação...")
        time.sleep(5)

    # Baixa o arquivo
    nome_arquivo = f"relatorio_scan_{scan_id}.{json}"
    with open(nome_arquivo, 'wb') as f:
        tio.scans.export_download(scan_id, export_id, f)
    print(f"📁 Relatório salvo como: {nome_arquivo}")
