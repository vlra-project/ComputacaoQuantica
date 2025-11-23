from tenable.io import TenableIO
import re

ACCESS_KEY = 'SUA_ACCESS_KEY'
SECRET_KEY = 'SUA_SECRET_KEY'
tio = TenableIO(ACCESS_KEY, SECRET_KEY)

# Função para escolher o scanner com base em palavras-chave no domínio
def selecionar_scanner(dominio, scanners):
    dominio = dominio.lower()
    for scanner in scanners:
        name = scanner['name'].lower()
        if 'itabira' in dominio and 'itabira' in name:
            return scanner['id']
        elif 'valeglobal' in dominio and 'global' in name:
            return scanner['id']
        elif 'top.ta.vale.br' in dominio and 'ta' in name:
            return scanner['id']
#    return None  # Scanner padrão pode ser definido aqui se quiser
