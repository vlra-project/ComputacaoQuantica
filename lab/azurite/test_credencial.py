import re
import json
from tenable.io import TenableIO

# Substitua pelas suas credenciais da API do Tenable.io
ACCESS_KEY = 'a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9'
SECRET_KEY = 'c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213'

# Inicializa o cliente do Tenable.io
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

#from pprint import pprint

def listar_credenciais_windows(tio):
    print("🔐 Credenciais do tipo Windows disponíveis:\n")
    credenciais_windows = []
    for credencial in tio.credentials.list():
        if credencial.get('type') == 'windows':
            info = {
                'id': credencial['id'],
                'name': credencial['name'],
                'last_updated': credencial.get('last_modification_date')
            }
            credenciais_windows.append(info)
            pprint(info)
            return credenciais_windows

cred = listar_credenciais_windows(tio)

# Chame a função
#listar_credenciais_windows(tio)

with open('credenciais_disponiveis2.json', 'w', encoding='utf-8') as f:
#    json.dump(cred, f, ensure_ascii=False, indent=4)
#
    print('Arquivo salvo com sucesso!')
