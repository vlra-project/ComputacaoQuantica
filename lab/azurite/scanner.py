import re
import json
from tenable.io import TenableIO

# Substitua pelas suas credenciais da API do Tenable.io
ACCESS_KEY = 'a9c3c8fa5880f482585744123ff97b541031816adba5c96a1702690b906b05e9'
SECRET_KEY = 'c9fe8a4a8a244b1d404730c08e99391a17f5c9cacb9ab669db902677e2cde213'

# Inicializa o cliente do Tenable.io
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

scanners = list(tio.scanners.allowed_scanners())

with open('scanners_disponiveis.json', 'w', encoding='utf-8') as f:
    json.dump(scanners, f, ensure_ascii=False, indent=4)

    print('Arquivo "scanners_disponiveis.json" salvo com sucesso!')


